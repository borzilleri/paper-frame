from pathlib import Path
from epdproxy import FAKE_EPD_DRIVER
from .util import load_toml


class Config:
    __DEFAULT_EPD = FAKE_EPD_DRIVER
    __DEFAULT_DATA_DIR = str(Path.cwd())
    __DEFAULT_LOG_LEVEL = "INFO"

    epd: str = __DEFAULT_EPD
    data_dir: str = __DEFAULT_DATA_DIR
    log_level: str = __DEFAULT_LOG_LEVEL

    @classmethod
    def to_str(cls) -> str:
        return f"""{cls.__name__}(
            epd='{cls.epd}',
            data_dir='{str(cls.data_dir)}',
            log_level='{cls.log_level}'
        )"""


def init_config(config_path: str):
    data = load_toml(config_path)
    for k, v in data.items():
        setattr(Config, k, v)
