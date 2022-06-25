import time
from fractions import Fraction
from pathlib import Path

import ffmpeg
from epdproxy.epdfactory import EPD
from PIL import Image

from .config import config
from .constants import Mode
from .images import load_image
from .job import Job
from .log import logger

VIDEO_INFO_LIST = []
__FRAME_TEMP_FILE = Path(config.FrameTempPath)


class VideoInfo:
    def __init__(self, frame_count, fps, duration, subtitle_file):
        self.frame_count = frame_count
        self.fps = fps
        self.frame_time = 1000 / fps
        self.duration = duration
        self.subtitle_file = subtitle_file

    def __str__(self):
        return f"VideoInfo(frame_count={self.frame_count}, fps={self.fps}, duration={self.duration}, frame_time={self.frame_time}, subtitle_file={self.subtitle_file})"


def get_video_info(file_path_str: str) -> VideoInfo:
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
        info = VideoInfo(
            frame_count=frame_count, fps=fps, duration=duration, subtitle_file=None
        )
    logger.debug(f"Loaded video info:\n{info}")
    return info


def get_frame_from_video(
    input_path_str: str, width: int, height: int, time: str
) -> Image:
    try:
        (
            ffmpeg.input(input_path_str, ss=time)
            .filter("scale", "iw*sar", "ih")
            .filter("scale", width, height, force_original_aspect_ratio=1)
            .filter("pad", width, height, -1, -1)
            # .overlay_filter()
            .output(str(__FRAME_TEMP_FILE), vframes=1, copyts=None)
            .overwrite_output()
            .run(quiet=True)
        )
        return load_image(__FRAME_TEMP_FILE)
    except ffmpeg.Error as e:
        logger.error(e.stderr)
    return None


def display_video(epd: EPD, job: Job, video: VideoInfo, wait: int):
    # If we're in single video mode, and we're past the end of the current video, just restart.
    # Even if we're not looping
    if job.mode == Mode.VIDEO and job.frame > video.frame_count:
        job.frame = 0

    while video is not None and job.frame <= video.frame_count:
        time_start = time.perf_counter()
        epd.prepare()

        timecode_ms = f"{int(job.frame * video.frame_time)}ms"

        img = get_frame_from_video(str(job.path), epd.width, epd.height, timecode_ms)
        if img is not None:
            logger.debug(
                f"Displaying frame {job.frame} of {job.path} ({(job.frame/video.frame_count)*100:.1f}%)"
            )
            epd.display(img)
        else:
            logger.error(f"Unable to retrieve frame for {job.path} : {timecode_ms}")

        # Increment our frame
        job.frame += 1
        if job.frame > video.frame_count and job.loop:
            # We're past the end of the file, and we're looping.
            job.frame = 0

        # If we get here, we just write our progress log and continue.
        job.save()

        # Sleep until our next iteration.
        epd.sleep()
        time_diff = time.perf_counter() - time_start
        time.sleep(max(wait - time_diff, 0))
