import threading

import os
import subprocess
import psutil
import time
import signal

import logging

from conf import cfg


class ProdigyCommand:
    def __init__(self) -> None:
        self.running = False
        self.proc = None
        self.event = threading.Event()

    def prodigy_cmd(self, cmd, **kwargs):

        if "block" in kwargs:
            block = kwargs["block"]
        else:
            block = False

        prodigy_config = os.path.abspath(cfg["prodigy"]["config_file"])
        os.environ["PRODIGY_CONFIG"] = prodigy_config
        os.environ["PRODIGY_LOGGING"] = "basic"

        prodigy_output_file = open(
            os.path.abspath(f"{cfg['folders']['output']}/prodigy.{cmd}.log"), "w"
        )
        prodigy_err_file = open(
            os.path.abspath(f"{cfg['folders']['output']}/prodigy.{cmd}.err.log"), "w"
        )

        prodigy_env = os.environ.copy()

        base_model = "--base-model en_core_web_trf "

        try:
            for model in cfg["prodigy"]["model"]:
                model_path = kwargs["output_dir"] + "/training/" + model
                if os.path.exists(model_path):
                    base_model = f"--base-model {model_path} "
        except:
            pass

        if cmd == "annotate-manual":
            text_classes = ",".join(
                "'{0}'".format(x) for x in cfg["learning_model"]["labels"]
            )
            prodigy_command = f"prodigy textcat.manual {cfg['prodigy']['dataset']} {kwargs['output_file']} --label {text_classes}"

        if cmd == "train":
            prodigy_command = f"prodigy train {kwargs['output_dir']}/training --textcat-multilabel {cfg['prodigy']['dataset']} {base_model}--label-stats -g 0"

        if cmd == "train-curve":
            prodigy_command = f"prodigy train-curve --textcat-multilabel {cfg['prodigy']['dataset']} {base_model} -g 0"

        if cmd == "db-out":
            prodigy_command = f"prodigy db-out {cfg['prodigy']['dataset']} {kwargs['output_dir']}/annotations"

        self.proc = subprocess.Popen(
            prodigy_command,
            env=prodigy_env,
            shell=True,
            stdout=prodigy_output_file,
            stderr=prodigy_err_file,
            preexec_fn=os.setpgrp,
        )

        logging.info(f"Prodigy ({cmd}) running as PID {self.proc.pid}")

        if block:
            while psutil.pid_exists(self.proc.pid):
                os.wait()
                time.sleep(5)

        return self.proc

    def annotate_manual(self, output_file):
        if self.running:
            return

        self.annotate_thread = threading.Thread(
            target=self._annotate_manual, args=[output_file]
        )
        self.annotate_thread.start()

    def stop(self):
        self.event.set()
        time.sleep(60)
        if self.running is True and self.event.is_set():
            print("Timeout expired, killing process...")
            os.system("killall prodigy")

    def _annotate_manual(self, output_file):
        self.running = True
        self.prodigy_cmd(cmd="annotate-manual", output_file=output_file)

        while not self.event.is_set():
            self.event.wait(600)

        os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        self.event.clear()
        self.running = False

    def db_out(self, output_dir):
        self.running = True
        self.prodigy_cmd(cmd="db-out", output_dir=output_dir, block=True)
        self.running = False

    def train(self, output_dir):
        self.running = True
        self.prodigy_cmd(cmd="train", output_dir=output_dir, block=True)
        self.running = False

    def train_curve(self, output_dir):
        self.running = True
        self.prodigy_cmd(cmd="train-curve", output_dir=output_dir, block=True)
        self.running = False
