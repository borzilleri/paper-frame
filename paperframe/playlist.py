import json
import random
import time
from pathlib import Path
from PIL import Image
from typing import Dict, List, Optional, Generator

from epdproxy import EPD
from . import util, images, videos
from .config import config
from .log import LOG


class PlaylistConfig:
    media_path: str
    wait_seconds: int = 30
    random: bool = False
    loop: bool = False
    resume_playback: bool = False
    clear_display: bool = True

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(media_path='{self.media_path}', wait_seconds='{self.wait_seconds}', random='{self.random}', loop='{self.loop}', resume_playback='{self.resume_playback}', clear_display='{self.clear_display}')"

    def to_json(self) -> Dict[str, object]:
        return vars(self)


class Playlist:
    config: PlaylistConfig
    files: List[str] = list()
    __index: int = 0
    frame: int = 0

    def __init__(
        self,
        config: PlaylistConfig,
        files: List[str] = list(),
        index: int = 0,
        frame: int = 0,
    ):
        self.config = config
        self.files = files
        self.__index = index
        self.frame = frame

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(files={len(self.files)} files, index={self.__index}, frame={self.frame}, config={self.config})"

    def to_json(self) -> Dict[str, object]:
        return {
            "config": self.config.to_json(),
            "files": self.files,
            "index": self.__index,
            "frame": self.frame,
        }

    def iter(self) -> Generator[Path, None, None]:
        while self.__index < len(self.files):
            yield Path(self.files[self.__index])
            self.__index += 1
        if self.config.loop:
            self.__index = 0

    def save(self):
        with Path(config.ProgramStatePath).open("w") as f:
            json.dump(self.to_json(), f)


def load_media(media_path: Path, random_order: bool) -> List[str]:
    media_list = []
    if media_path.is_file():
        media_list = [media_path]
    elif media_path.is_dir():
        media_list = [f for f in media_path.iterdir() if util.is_valid_media(f)]
    if random_order:
        random.shuffle(media_list)
    else:
        media_list = sorted(media_list, key=lambda f: f.name)
    media_list = [str(f) for f in media_list]
    LOG.info(f"Loaded media: {media_list}")
    return media_list


def init_playlist(playlist_path: str) -> Playlist:
    config: PlaylistConfig = util.load_config_to_object(playlist_path, PlaylistConfig())
    files: List[str] = load_media(Path(config.media_path), config.random)
    return Playlist(config, files=files)


def __play_media_files(playlist: Playlist, epd: EPD):
    for current_file in playlist.iter():
        LOG.info(f"playing {str(current_file)}")
        time_start = time.perf_counter()
        image: Optional[Image.Image] = None
        if util.is_image(current_file):
            image = images.load_image(current_file)
        if util.is_video(current_file):
            info: Optional[videos.VideoInfo] = videos.get_video_info(current_file)
            if info is None:
                LOG.error("Unable to query video info: ")
            else:
                image = videos.get_frame(
                    current_file, info, playlist.frame, epd.width, epd.height
                )
                playlist.frame += 1
                # If we've passed the end of our file, go to the next file.
                if playlist.frame >= info.frame_count:
                    playlist.frame = 0
        if image is not None:
            epd.prepare()
            epd.display(image)
        playlist.save()
        epd.sleep()
        time_diff = time.perf_counter() - time_start
        time.sleep(max(playlist.config.wait_seconds - time_diff, 0))


def start_playback(playlist: Playlist, epd: EPD):
    if len(playlist.files) == 0:
        raise Exception("Playlist is empty, cannot start playback.")
    while True:
        __play_media_files(playlist, epd)
        if playlist.config.clear_display:
            epd.clear()
        if playlist.config.loop:
            LOG.info("Restarting playback.")
        else:
            break
