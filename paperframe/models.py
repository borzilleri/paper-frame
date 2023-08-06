import random
from pathlib import Path
from typing import Any, Dict, Generator, List


class PlaylistDefinition:
    __wait = 30
    __random = False
    __loop = False
    __resume = False
    __clear = True

    media_path: str
    wait_seconds: int
    random: bool
    loop: bool
    resume_playback: bool
    clear_display: bool

    def __init__(
        self,
        media_path: str,
        wait_seconds: int = __wait,
        random: bool = __random,
        loop: bool = __loop,
        resume_playback: bool = __resume,
        clear_display: bool = __clear,
    ):
        self.media_path = media_path
        self.wait_seconds = wait_seconds
        self.random = random
        self.loop = loop
        self.resume_playback = resume_playback
        self.clear_display = clear_display

    def __str__(self) -> str:
        return f"""{self.__class__.__name__}(
            media_path='{self.media_path}', 
            wait_seconds='{self.wait_seconds}', 
            random='{self.random}', 
            loop='{self.loop}', 
            resume_playback='{self.resume_playback}', 
            clear_display='{self.clear_display}'
        )"""

    def to_json(self) -> Dict[str, object]:
        return vars(self)


class Playlist:
    config: PlaylistDefinition
    __files: List[str]
    __index: int
    frame: int

    def __init__(
        self,
        config: PlaylistDefinition | Dict[str, Any],
        files: List[str] = list(),
        index: int = 0,
        frame: int = 0,
    ):
        if isinstance(config, PlaylistDefinition):
            self.config = config
        else:
            self.config = PlaylistDefinition(**config)
        self.__files = files
        self.__index = index
        self.frame = frame

    def __str__(self) -> str:
        return f"""{self.__class__.__name__}(
            files={len(self.__files)} files, 
            index={self.__index}, 
            frame={self.frame}, 
            config={self.config}
        )"""

    def __len__(self) -> int:
        return len(self.__files)

    def to_json(self) -> Dict[str, object]:
        return {
            "config": self.config.to_json(),
            "files": self.__files,
            "index": self.__index,
            "frame": self.frame,
        }

    def iter(self) -> Generator[Path, None, None]:
        while self.__index < len(self.__files):
            yield Path(self.__files[self.__index])
            self.__index += 1
        if self.config.loop:
            self.__index = 0
            if self.config.random:
                random.shuffle(self.__files)

    def in_progress(self) -> bool:
        return self.__index < len(self.__files)
