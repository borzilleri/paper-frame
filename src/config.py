import json
from pathlib import Path
from .constants import DEFAULT_CONFIG_PATH

CONFIG_FILE = Path(DEFAULT_CONFIG_PATH)


class Config:
    EpdDriver = None
    FrameTempPath = None
    ProgramStatePath = None


config = Config()


def init(config_path: str):
    new_path = Path(config_path).expanduser().absolute()
    if new_path.is_file():
        CONFIG_FILE = new_path
    with CONFIG_FILE.open("r") as f:
        config_json = json.load(f)
        for k, v in config_json.items():
            setattr(config, k, v)
