import json
from pathlib import Path
import random
from .config import config
from .constants import VALID_VIDEO_TYPES, Mode
from .log import logger


class Job:
    def __init__(
        self,
        mode: str,
        path: str,
        files: list = list(),
        index: int = 0,
        frame: int = 0,
        loop: bool = False,
    ):
        self.mode = Mode[mode.upper()]
        self.path = Path(path)
        self.files = [Path(p) for p in files]
        self.index = index
        self.frame = frame
        self.loop = loop

    def __str__(self):
        return f"ProgressLog(mode='{self.mode.name}', path='{self.path}', files='{len(self.files)} files', index={self.index}, frame={self.frame}, loop={self.loop})"

    def toJson(self):
        return {
            "mode": self.mode.name,
            "path": str(self.path),
            "files": [str(p) for p in self.files],
            "index": self.index,
            "frame": self.frame,
            "loop": self.loop,
        }

    def save(self):
        with Path(config.ProgramStatePath).open("w") as f:
            json.dump(self.toJson(), f)

    def getNextPathItem() -> Path:
        return None


def build_job(
    resume: bool, mode: Mode, path: Path, random_order: bool, loop: bool
) -> Job:
    log = None
    state_file = Path(config.ProgramStatePath)
    if resume and state_file.is_file():
        with state_file.open("r") as f:
            data = json.load(f)
            log = Job(**data)
    else:
        files = list()
        if mode in (Mode.ALBUM, Mode.PLAYLIST):
            files = [
                f
                for f in path.iterdir()
                if f.is_file() and f.suffix in VALID_VIDEO_TYPES
            ]
            if random_order:
                random.shuffle(files)
        log = Job(mode=mode, path=path, files=files, index=0, frame=0, loop=loop)
    logger.debug(f"Configured playback\n{log}")
    return log
