import random
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional


class PlaylistDefinition:
    __default_wait = 30
    __default_random = False
    __default_loop = False
    __default_resume = False

    media_path: str
    wait_seconds: int
    random: bool
    loop: bool
    resume_playback: bool
    clear_image: Optional[str]

    def __init__(
        self,
        media_path: str,
        wait_seconds: int = __default_wait,
        random: bool = __default_random,
        loop: bool = __default_loop,
        resume_playback: bool = __default_resume,
        clear_image: Optional[str] = None,
    ):
        self.media_path = media_path
        self.wait_seconds = wait_seconds
        self.random = random
        self.loop = loop
        self.resume_playback = resume_playback
        self.clear_image = clear_image

    def __str__(self) -> str:
        return f"""{self.__class__.__name__}(
            media_path='{self.media_path}', 
            wait_seconds='{self.wait_seconds}', 
            random='{self.random}', 
            loop='{self.loop}', 
            resume_playback='{self.resume_playback}', 
            clear_image='{self.clear_image}'
        )"""

    def to_json(self) -> Dict[str, object]:
        return vars(self)


class Playlist:
    config: PlaylistDefinition
    __files: List[str]
    __index: int
    frame: int
    frame_count: int

    def __init__(
        self,
        config: Any,
        files: List[str] = list(),
        index: int = 0,
        frame: int = 0,
        frame_count: int = 1,
    ):
        if isinstance(config, PlaylistDefinition):
            self.config = config
        else:
            self.config = PlaylistDefinition(**config)
        self.__files = files
        self.__index = index
        self.frame = frame
        self.frame_count = frame_count

    def __str__(self) -> str:
        return f"""{self.__class__.__name__}(
            files={len(self.__files)} files, 
            index={self.__index}, 
            frame={self.frame},
            frame_count{self.frame_count},
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
            "frame_count": self.frame_count,
        }

    def iter(self) -> Generator[Path, None, None]:
        while self.__index < len(self.__files):
            while self.frame < self.frame_count:
                yield Path(self.__files[self.__index])
                self.frame += 1
            self.frame = 0
            self.frame_count = 1
            self.__index += 1
        if self.config.loop:
            self.__index = 0
            if self.config.random:
                random.shuffle(self.__files)
