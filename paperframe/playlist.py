import json
import random
import time
from pathlib import Path
from PIL import Image
from typing import Any, Dict, List, Optional

from epdproxy import EPD
from . import util, images, videos
from .config import Config
from .constants import PLAYLIST_DEFINITION_FILE, PLAYLIST_SAVE_FILE
from .log import LOG
from .models import Playlist, PlaylistDefinition


def __get_savefile() -> Path:
    return Path(Config.data_dir, PLAYLIST_SAVE_FILE).expanduser().absolute()


def __create_save(playlist: Playlist):
    with __get_savefile().open("w") as f:
        json.dump(playlist.to_json(), f)


def __clear_save():
    __get_savefile().unlink()


def __load_save() -> Optional[Playlist]:
    save_file = __get_savefile()
    if not save_file.is_file():
        LOG.info("no save data found.")
        return None
    with save_file.open("r") as f:
        data: Dict[str, Any] = json.load(f)
    if data["config"] is None or not isinstance(data["config"], dict):
        LOG.warn("malformed save data: config data missing or malformed.")
        return None
    playlist = Playlist(**data)
    LOG.info("Found in progress save data")
    return playlist


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


def __read_playlist_file(playlist_path: Optional[str]) -> PlaylistDefinition:
    if playlist_path is None:
        playlist_path = str(
            Path(Config.data_dir, PLAYLIST_DEFINITION_FILE).expanduser().absolute()
        )
    pl_def_data = util.load_config(playlist_path)
    playlist_def = PlaylistDefinition(**pl_def_data)
    LOG.debug(f"loaded playlist definition: {playlist_def}")
    return playlist_def


def init_playlist(playlist_path: Optional[str]) -> Playlist:
    save_data = __load_save()
    playlist_def = __read_playlist_file(playlist_path)
    if save_data is not None and save_data.config.resume_playback:
        # If we found a save AND it's configured to resume playback,
        # compare it to our loaded playlist config:
        if save_data.config.to_json() == playlist_def.to_json():
            # They match, so return our saved data.
            return save_data
    playlist_files = load_media(
        Path(playlist_def.media_path).expanduser().absolute(), playlist_def.random
    )
    return Playlist(playlist_def, files=playlist_files)


def __play_media_files(playlist: Playlist, epd: EPD):
    for current_file in playlist.iter():
        time_start = time.perf_counter()
        image: Optional[Image.Image] = None
        if util.is_image(current_file):
            image = images.load_image(current_file, epd.width, epd.height)
        if util.is_video(current_file):
            info: Optional[videos.VideoInfo] = videos.get_video_info(current_file)
            if info is None:
                LOG.error("Unable to query video info: ")
            else:
                playlist.frame_count = info.frame_count
                image = videos.get_frame(
                    current_file, info, playlist.frame, epd.width, epd.height
                )
        if image is not None:
            epd.prepare()
            epd.display(image)
            epd.sleep()
        __create_save(playlist)
        time_diff = time.perf_counter() - time_start
        time.sleep(max(playlist.config.wait_seconds - time_diff, 0))


def __clear_display(epd: EPD, clear_image: Optional[str]):
    if clear_image is not None:
        image = images.load_image(
            Path(clear_image).expanduser().absolute(), epd.width, epd.height
        )
        if image is not None:
            LOG.debug(f"Displaying clear image: {clear_image}")
            epd.prepare()
            epd.display(image)
            epd.sleep()
            return
        else:
            LOG.warn(f"Unable to load clear image: {clear_image}")
    LOG.debug("Playlist complete.")


def start_playback(playlist: Playlist, epd: EPD):
    if len(playlist) == 0:
        raise Exception("Playlist is empty, cannot start playback.")
    while True:
        __play_media_files(playlist, epd)
        if playlist.config.loop:
            LOG.info("Restarting playback.")
        else:
            break
    __clear_save()
    __clear_display(epd, playlist.config.clear_image)
