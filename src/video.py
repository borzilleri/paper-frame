import ffmpeg
from fractions import Fraction
from pathlib import Path
from PIL import Image
from pprint import pformat
from .log import logger
from .constants import FRAME_TEMP_FILE

VIDEO_INFO_LIST = []


def get_video_info(file_path_str: str):
    if file_path_str in VIDEO_INFO_LIST:
        info = VIDEO_INFO_LIST[file_path_str]
    else:
        logger.info(f"Retrieving info for file: {file_path_str}")
        try:
            probe_info = ffmpeg.probe(str(file_path_str), select_streams="v")
        except ffmpeg.Error as e:
            logger.error(e.stderr)
            return None
        stream = probe_info["streams"][0]
        fps = float(Fraction(stream["avg_frame_rate"]))
        duration = float(probe_info["format"]["duration"])
        try:
            frame_count = int(stream["nb_frames"])
        except KeyError:
            frame_count = int(duration * fps)
        frame_time = 1000 / fps
        info = {
            "frame_count": frame_count,
            "fps": fps,
            "duration": duration,
            "frame_time": frame_time,
            "subtitle_file": None,
        }
    logger.debug(f"Loaded video info:\n{pformat(info)}")
    return info


def get_frame_from_video(input_path_str: str, width: int, height: int, time: str):
    try:
        (
            ffmpeg.input(input_path_str, ss=time)
            .filter("scale", "iw*sar", "ih")
            .filter("scale", width, height, force_original_aspect_ratio=1)
            .filter("pad", width, height, -1, -1)
            # .overlay_filter()
            .output(str(FRAME_TEMP_FILE), vframes=1, copyts=None)
            .overwrite_output()
            .run(quiet=True)
        )
        return Image.open(FRAME_TEMP_FILE)
    except ffmpeg.Error as e:
        logger.error(e.stderr)
    return None
