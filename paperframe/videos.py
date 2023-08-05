import ffmpeg  # type: ignore
import tempfile

from typing import Any, Dict, Optional

from fractions import Fraction
from pathlib import Path
from PIL import Image

from .log import LOG


class VideoInfo:
    def __init__(self, frame_count: int, fps: float, duration: float):
        self.frame_count = frame_count
        self.fps = fps
        self.frame_time = 1000 / fps
        self.duration = duration

    def __str__(self):
        return f"VideoInfo(frame_count={self.frame_count}, fps={self.fps}, duration={self.duration}, frame_time={self.frame_time})"


VIDEO_INFO_LIST: Dict[str, VideoInfo] = {}


def get_video_info(file: Path) -> Optional[VideoInfo]:
    path_str = str(file)
    if path_str in VIDEO_INFO_LIST:
        return VIDEO_INFO_LIST[path_str]
    else:
        LOG.info(f"Retrieving info for file: {path_str}")
        try:
            probe_info = ffmpeg.probe(path_str, select_streams="v")  # type: ignore
        except ffmpeg.Error as e:
            LOG.error(e.stderr)
            return None
        stream = probe_info["streams"][0]
        fps = float(Fraction(stream["avg_frame_rate"]))
        duration = float(probe_info["format"]["duration"])
        try:
            frame_count = int(stream["nb_frames"])
        except KeyError:
            frame_count = int(duration * fps)
        info = VideoInfo(frame_count=frame_count, fps=fps, duration=duration)
        VIDEO_INFO_LIST[path_str] = info
        LOG.debug(f"Loaded video info:\n{info}")
    return info


def get_frame(
    file: Path, info: VideoInfo, frame: int, width: int, height: int
) -> Optional[Image.Image]:
    image = None
    timecode_ms = f"{int(frame * info.frame_time)}ms"
    tmp_file: Any = tempfile.NamedTemporaryFile()
    try:
        (
            ffmpeg.input(str(file), ss=timecode_ms)  # type: ignore
            .filter("scale", "iw*sar", "ih")
            .filter("scale", width, height, force_original_aspect_ratio=1)
            .filter("pad", width, height, -1, -1)
            # .overlay_filter()
            .output(tmp_file.name, vframes=1, f="image2", copyts=None)
            .overwrite_output()
            .run(quiet=True)
        )
        image = Image.open(tmp_file)
        LOG.debug(
            f"Displaying frame {frame}/{info.frame_count} of {str(file)} ({(frame/info.frame_count)*100:.1f}%)"
        )
    except ffmpeg.Error as e:
        LOG.error(f"Unable to load frame {frame} from {str(file)}: \n{e.stderr}")
    except Exception as e:
        LOG.error(f"Unable to load frame {frame} from {str(file)}: \n{e}")
    return image
