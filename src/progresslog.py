import json
from pathlib import Path
from pprint import pformat
from .constants import PROGRESS_FILE, MODES
from .log import logger


class ProgressLog:
    mode: str
    path: Path
    frame: 0
    random: bool
    loop: bool

    def __init__(self, mode: str, path: Path, frame: int, random: bool, loop: bool):
        self.mode = mode
        self.path = path
        self.frame = frame
        self.random = random
        self.loop = loop

    def __str__(self):
        return f"ProgressLog(mode='{self.mode}', path={self.path}, frame={self.frame}, random={self.random}, loop={self.loop})"

    def toJson(self):
        return {
            "mode": self.mode,
            "path": str(self.path),
            "frame": self.frame,
            "random": self.random,
            "loop": self.loop,
        }


def save(progress_log: ProgressLog):
    with PROGRESS_FILE.open("w") as f:
        json.dump(progress_log.toJson(), f)


def load(resume: bool, mode: str, dir: Path, file: Path, random: bool, loop: bool) -> ProgressLog:
    log = None
    if resume and PROGRESS_FILE.is_file():
        with PROGRESS_FILE.open("r") as f:
            data = json.load(f)
            log = ProgressLog(
                data["mode"],
                Path(data["path"]),
                data["frame"],
                data["random"],
                data["loop"],
            )
    else:
        if mode == "album" or mode == "playlist":
            path = dir
        else:
            path = file
        log = ProgressLog(mode, path, 0, random, loop)
    logger.debug(f"Configured playback\n{log}")
    return log
