from . import constants
from .util import load_config


class Config:
    playlist: str = constants.DEFAULT_PLAYLIST
    epd: str = constants.DEFAULT_EPD
    data_dir: str = constants.DEFAULT_DATA_DIR
    log_level: str = constants.DEFAULT_LOG_LEVEL

    @classmethod
    def to_str(cls) -> str:
        return f"""{cls.__name__}(
            playlist='{cls.playlist}',
            epd='{cls.epd}',
            data_dir='{str(cls.data_dir)}',
            log_level='{cls.log_level}'
        )"""


def init_config(config_path: str):
    data = load_config(config_path)
    for k, v in data.items():
        setattr(Config, k, v)
