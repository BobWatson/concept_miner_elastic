import atexit
import json
import logging
import os
import threading
import time

from ansi2html import Ansi2HTMLConverter
from conf import cfg
from elastic.ElasticManager import ElasticManager
from flask import Flask, render_template, request
from flask_restful import Api
from ingestor.directoryWatcher import directoryWatcher
from ingestor.PDFExtractor import PDFExtractor
from ingestor.TextExtractor import TextExtractor
from prodigy_helper.ProdigyCommand import ProdigyCommand
from pymitter import EventEmitter
from werkzeug.utils import secure_filename
from pathlib import Path

from .control_api.eventReceiver import eventReceiver

ee = EventEmitter(wildcard=True, new_listener=True, max_listeners=-1)

app = Flask(__name__)
api = Api(app)

er = eventReceiver.withEmitter(ee)
api.add_resource(er, '/event/<string:event_id>')

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 1600 * 1024 * 1024

## -- Routes -- ##

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/training-log.html')
def training_log():
    conv = Ansi2HTMLConverter()
    with open(os.path.abspath(f"{cfg['folders']['output']}/prodigy.train.log"),"r") as f:
        logdata = f.read()
        
    with open(os.path.abspath(f"{cfg['folders']['output']}/prodigy.train-curve.log"),"r") as f:
        curvedata = f.read()
        
    html_log = conv.convert(logdata.replace("`","'"))
    html_curve_log = conv.convert(curvedata.replace("`","'"))
    
    return render_template('training-log.html',logdata=html_log,curvedata=html_curve_log)

@app.route('/upload', methods = ['POST'])
def upload_file():
    if request.method == 'POST':
        for file in request.files.getlist('files'):
            file_name = os.path.join(cfg['folders']['watch_folder'],secure_filename(file.filename))
            logging.info(f"Received {file_name}")
            file.save(file_name)
        return json.dumps({"status": "success"})
    else:
        return json.dumps({"status": "failure"})

## -- Done with routes -- ##

dw = directoryWatcher(cfg['folders']['watch_folder'])

@ee.on("directory_watcher.start")
def run_directory_watcher():
    
    print("Running Directory Watcher")
    
    dw.add_handler("pdf",PDFExtractor.getContent)
    dw.add_handler("txt",TextExtractor.getContent)
    
    dw.run(30)

@ee.on("directory_watcher.stop")
def stop_directory_watcher():
    dw.stop()

prodigy_running = False
app_should_loop = True
can_halt = False

prodigy = ProdigyCommand()

@ee.on("prodigy.start")
def run_prodigy():
    p = threading.Thread(target=_run_prodigy)
    p.start()

def _run_prodigy():
    global prodigy_running
    global app_should_loop
    
    if prodigy_running:
        print("Prodigy already running")
        return
    
    print("Running prodigy...")
    
    jsonl = ElasticManager.build_jsonl(cfg['prodigy']['batch_size'])
        
    output_file = os.path.join(cfg['folders']['output'], "data.jsonl")
    
    with open(output_file, 'w') as f:
        f.write(jsonl)
        f.close()
    
    prodigy_running = True
    prodigy.annotate_manual(output_file=output_file)
    
    while prodigy_running:
        time.sleep(5)
        
    prodigy.db_out(output_dir=cfg['folders']['output'])
    ee.emit("prodigy.db_written")
    
    if app_should_loop:
        
        print("Training...")
    
        prodigy.train(output_dir=cfg['folders']['output'])
        prodigy.train_curve(output_dir=cfg['folders']['output'])
        
        ee.emit("prodigy.start")
        
    else:
        print("Prodigy done.")
        ee.emit("prodigy.done")

@ee.on("prodigy.stop")
def stop_prodigy():
    global prodigy_running
    
    prodigy.stop()
    prodigy_running = False

@ee.on("app.halt")
def halt_app():
    global app_should_loop
    global can_halt
    app_should_loop = False
    
    ee.emit("prodigy.stop")
    ee.emit("directory_watcher.stop")
    
    while not can_halt:
        time.sleep(5)
    
@ee.on("prodigy.done")
def _halt_app():
    global can_halt
    print ("Prodigy stopped. App can exit.")
    can_halt = True
    
@ee.on("prodigy.db_written")
def read_annotations_into_elastic():
    em = ElasticManager(elastic_index=cfg["elastic"]["annotation_index"])
    annotations_folder = cfg['folders']['output']+"/annotations"
    fileList = [x for x in Path(annotations_folder).rglob('*.jsonl')]
    for file_name in fileList:
        file = open(file_name, 'r')
        lines = file.readlines()
        for line in lines:
            line_dict = json.loads(line)
            try:
                id = line_dict["meta"]["id"]
            except:
                id = "<err>"
                
            em.add(line_dict, id)
    

@app.before_first_request
def main():
    global prodigy_running
    global app_should_loop
    global can_halt
    
    prodigy_running = False
    app_should_loop = True
    can_halt = False
    
    atexit.register(ee.emit,'app.halt')
    
    ee.emit("directory_watcher.start")
    ee.emit("prodigy.start")
    
    print("Ready.")
