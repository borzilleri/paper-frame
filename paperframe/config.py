from .util import load_config_to_object


class Config:
    EpdDriver: str
    FrameTempPath: str
    ProgramStatePath: str
    LogLevel: str = "INFO"

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(EpdDriver='{self.EpdDriver}', FrameTempPath='{self.FrameTempPath}', ProgramStatePath='{self.ProgramStatePath}', LogLevel='{self.LogLevel}')"


config = Config()


def init_config(config_path: str):
    load_config_to_object(config_path, config)
