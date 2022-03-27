import json
from pathlib import Path

CONFIG_FILE = Path("config.json")


class Config:
    EpdDriver = None
    FrameTempPath = None
    ProgramStatePath = None


config = Config()

with CONFIG_FILE.open("r") as f:
    config_json = json.load(f)
    for k, v in config_json.items():
        setattr(config, k, v)
