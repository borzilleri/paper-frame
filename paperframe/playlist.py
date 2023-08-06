import json
import random
import time
from pathlib import Path
from PIL import Image
from typing import Any, Dict, List, Optional

from epdproxy import EPD
from . import util, images, videos
from .config import Config
from .log import LOG
from .models import Playlist, PlaylistDefinition

__PLAYLIST_DEFINITION_FILE = "playlist.toml"
__PLAYLIST_SAVE_FILE = "playlist-save.json"


def __create_save(playlist: Playlist):
    save_file = Path(Config.data_dir, __PLAYLIST_SAVE_FILE)
    with save_file.open("w") as f:
        json.dump(playlist.to_json(), f)


def __load_save() -> Optional[Playlist]:
    save_file = Path(Config.data_dir, __PLAYLIST_SAVE_FILE)
    print(str(save_file))
    if not save_file.is_file():
        LOG.info("no save data found.")
        return None
    with save_file.open("r") as f:
        data: Dict[str, Any] = json.load(f)
    if data["config"] is None or not isinstance(data["config"], dict):
        LOG.warn("malformed save data: config data missing or malformed.")
        return None
    playlist = Playlist(**data)
    if playlist.config.resume_playback and playlist.in_progress():
        LOG.info("Found in progress save data with 'resume_playback=true'")
        return playlist
    LOG.info("Save found, but playlist was complete, or 'resume_playback=false'")
    return None


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


def init_playlist(playlist_path: str | None) -> Playlist:
    save_data = __load_save()
    if save_data is not None:
        return save_data
    if playlist_path is None:
        playlist_path = str(Path(Config.data_dir, __PLAYLIST_DEFINITION_FILE))
    pl_def_data = util.load_toml(playlist_path)
    playlist_def = PlaylistDefinition(**pl_def_data)
    LOG.debug(f"loaded playlist definition: {playlist_def}")
    playlist_files = load_media(Path(playlist_def.media_path), playlist_def.random)
    return Playlist(playlist_def, files=playlist_files)


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
        __create_save(playlist)
        epd.sleep()
        time_diff = time.perf_counter() - time_start
        time.sleep(max(playlist.config.wait_seconds - time_diff, 0))


def start_playback(playlist: Playlist, epd: EPD):
    if len(playlist) == 0:
        raise Exception("Playlist is empty, cannot start playback.")
    while True:
        __play_media_files(playlist, epd)
        if playlist.config.clear_display:
            epd.clear()
        if playlist.config.loop:
            LOG.info("Restarting playback.")
        else:
            break
