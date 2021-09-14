import yaml
import logging
import os
import shutil

if not os.path.exists("../conf/app.conf"):
    shutil.copy("../conf/app.dist.conf", "../conf/app.conf")

with open("../conf/app.conf") as yaml_data:
    cfg = yaml.safe_load(yaml_data)

logging.basicConfig(
    filename=cfg["logging"]["filename"],
    encoding="utf-8",
    level=getattr(logging, cfg["logging"]["level"].upper()),
)
