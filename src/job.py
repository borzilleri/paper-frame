import json
from pathlib import Path

from .config import config
from .constants import Mode
from .log import logger

STATE_FILE = Path(config.ProgramStatePath)

class Job:
    def __init__(self, mode: str, dir: Path, file: Path, frame: int, random: bool, loop: bool):
        self.mode = Mode[mode.upper()]
        self.dir = dir
        self.file = file
        self.frame = frame
        self.random = random
        self.loop = loop

    def __str__(self):
        return f"ProgressLog(mode='{self.mode.name}', dir='{self.dir}', file='{self.file}' frame={self.frame}, random={self.random}, loop={self.loop})"

    def toJson(self):
        return {
            "mode": self.mode.name,
            "dir": str(self.dir),
            "file": str(self.file),
            "frame": self.frame,
            "random": self.random,
            "loop": self.loop,
        }
    
    def save(self):
        with STATE_FILE.open("w") as f:
            json.dump(self.toJson(), f)
    
    def getNextPathItem() -> Path:
        return None

def build_job(resume: bool, mode: Mode, dir: Path, file: Path, random: bool, loop: bool) -> Job:
    log = None
    if resume and STATE_FILE.is_file():
        with STATE_FILE.open("r") as f:
            data = json.load(f)
            data['dir'] = Path(data['dir'])
            data['file'] = Path(data['file'])
            log = Job(**data)
    else:
        log = Job(mode, dir, file, 0, random, loop)
    logger.debug(f"Configured playback\n{log}")
    return log
