from flask import Flask, request, render_template
from flask_restful import Api

from .control_api.eventReceiver import eventReceiver

from conf import cfg
import os
from getkey import getkey
import time
import threading
import atexit

from ansi2html import Ansi2HTMLConverter

from ingestor.directoryWatcher import directoryWatcher
from ingestor.PDFExtractor import PDFExtractor
from ingestor.TextExtractor import TextExtractor

from prodigy_helper.ProdigyCommand import ProdigyCommand

from elastic.ElasticManager import ElasticManager

from pymitter import EventEmitter
ee = EventEmitter(wildcard=True, new_listener=True, max_listeners=-1)

app = Flask(__name__)
api = Api(app)

er = eventReceiver.withEmitter(ee)
api.add_resource(er, '/event/<string:event_id>')

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

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
        
    html_log = conv.convert(logdata)
    html_curve_log = conv.convert(curvedata)
    
    return render_template('training-log.html',logdata=html_log,curvedata=html_curve_log)

dw = directoryWatcher(cfg['folders']['watch_folder'])

@ee.on("run_directory_watcher")
def run_directory_watcher():
    
    print("Running Directory Watcher")
    
    dw.add_handler("pdf",PDFExtractor.getContent)
    dw.add_handler("txt",TextExtractor.getContent)
    
    dw.run(30)

@ee.on("stop_directory_watcher")
def stop_directory_watcher():
    dw.stop()

prodigy_running = False
app_should_loop = True
can_halt = False

prodigy = ProdigyCommand()

@ee.on("prodigy_start")
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
    
    while app_should_loop:
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
        
        if app_should_loop:
            
            print("Training...")
        
            prodigy.train(output_dir=cfg['folders']['output'])
        
            prodigy.train_curve(output_dir=cfg['folders']['output'])
        
    print("Prodigy done.")
    ee.emit("prodigy_halted")

@ee.on("prodigy_stop")
def stop_prodigy():
    global prodigy_running
    
    prodigy.stop()
    prodigy_running = False

@ee.on("halt_app")
def halt_app():
    global app_should_loop
    global can_halt
    app_should_loop = False
    
    ee.emit("prodigy_stop")
    ee.emit("stop_directory_watcher")
    
    while not can_halt:
        time.sleep(5)
    
@ee.on("prodigy_halted")
def _halt_app():
    global can_halt
    print ("Prodigy stopped. App can exit.")
    can_halt = True

@app.before_first_request
def main():
    global prodigy_running
    global app_should_loop
    global can_halt
    
    prodigy_running = False
    app_should_loop = True
    can_halt = False
    
    atexit.register(ee.emit,'halt_app')
    
    ee.emit("run_directory_watcher")
    ee.emit("prodigy_start")
    
    print("Ready.")