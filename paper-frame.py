#

# Inspired by, and much of the code borrowed from:
# https://github.com/TomWhitwell/SlowMovie

import signal
import sys
import ffmpeg
import logging
import configargparse
import time
import json

from pathlib import Path
from PIL import Image, ImageEnhance
from fractions import Fraction
from omni_epd import displayfactory, EPDNotFoundError


FRAME_TEMP_FILE = Path("/dev/shm/frame.bmp")
PROGRESS_FILE=Path.home().joinpath(".paper-frame-data/progress_log.json")
MODES = {"image": {}, "video": {}, "album": {}, "playlist": {}}
VIDEO_INFO_LIST = []

def exithandler(signum, frame):
    try:
        epd.close()
    finally:
        sys.exit()

# Add interrupt/termination signal hooks
signal.signal(signal.SIGTERM, exithandler)
signal.signal(signal.SIGINT, exithandler)

# Set up Logging
logger = logging.getLogger()
consoleLogHandler = logging.StreamHandler(sys.stdout)
consoleLogHandler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)-8s: %(module)s : %(message)s")
)
logger.addHandler(consoleLogHandler)


# Setup CLI arguments
parser = configargparse.ArgParser(default_config_files=["default.conf"])
parser.add_argument(
    "mode",
    choices=MODES.keys(),
    help="Display mode, single image, single video, album of images, or playlsit of videos",
)
parser.add_argument(
    "-d", "--dir", 
    type=lambda p: Path(p).expanduser().absolute(),
    help="Directory to search for images or videos for the album and playlist display modes."
)
parser.add_argument(
    "-f", "--file",
    type=lambda p: Path(p).expanduser().absolute(),
    help="Image or Video file to display, for those display modes."
)
parser.add_argument(
    "-r", "--random", action="store_true",
    help="In album or playlist mode, play files in a random orer."
)
parser.add_argument(
    "-l", "--loop", action="store_true",
    help="In album or playlist modes, loop over files in the directory. In video mode loops the specified file."
)
parser.add_argument(
    "-w", "--wait", type=int, default=120,
    help="wait in seconds between screen updates. (dfeault: %(default)s)"
)
# TODO
# frames-per-increment
# subtitles?
# display timecodE?
# start time/frame
# contrast
# clear-on-exit?

parser.add_argument("-R", "--resume", action="store_true",
    help="Attempt to resume and continue a previous execution, defaults to mode parameter if no previous execution found")
parser.add_argument("-e", "--epd", help="Name of epaper display driver to use.")
parser.add_argument(
    "-o", "--loglevel", default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="minimum importance-level of messages displayed and saved to the logfile (default: %(default)s)",
)
args = parser.parse_args()

print(args)
logger.setLevel(getattr(logging, args.loglevel))

# Set up e-paper display
try:
    epd = displayfactory.load_display_driver(args.epd)
except EPDNotFoundError:
    validEpds = displayfactory.list_supported_displays()
    logger.error("f'{args.epd}' is not a valid e-paper display name, valid names are:")
    logger.error("\n".join(map(str, validEpds)))
    sys.exit(1)

WIDTH = epd.width
HEIGHT = epd.height

def get_video_info(file_path):
    if file_path in VIDEO_INFO_LIST:
        info = VIDEO_INFO_LIST[file_path]
    else:
        logger.info(f"Retrieving info for file: {file_path}")
        try:
            probe_info = ffmpeg.probe(str(file_path), select_streams="v")
        except ffmpeg.Error as e:
            logger.error(e.stderr)
            exit(1)

        stream = probe_info["streams"][0]
        fps = float(Fraction(stream["avg_frame_rate"]))
        duration = float(probe_info["format"]["duration"])
        try:
            frame_count = int(stream["nb_frames"])
        except KeyError:
            frame_count = int(duration * fps)
        frame_time = 1000/fps
        # TODO: Load subtitles here?
        info = {
            "frame_count": frame_count,
            "fps": fps,
            "duration": duration,
            "frame_time": frame_time,
            "subtitle_file": None
        }
    return info

def get_frame_from_video(in_file, out_file, time):
    (
        ffmpeg.input(str(in_file), ss=time)
        .filter("scale", "iw*sar", "ih")
        .filter("scale", WIDTH, HEIGHT, force_original_aspect_ratio=1)
        .filter("pad", WIDTH, HEIGHT, -1, -1)
        #.overlay_filter()
        .output(str(out_file), vframes=1, copyts=None)
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )

def display_image():
    print("displaying image")


### If mode=resume, load progerss log and continue
progress_log = None
if args.resume and PROGRESS_FILE.is_file():
    with PROGRESS_FILE.open('r') as f:
        progress_log = json.load(f)
else:
    ## Setup from args
    progress_log = {
        "dir": args.dir,
        "file": args.file,
        "frame": 0,
        "random": args.random,
        "loop": args.loop
    }


## Load our next video

video_info = get_video_info(progress_log["file"])

while progress_log["frame"] <= video_info["frame_count"]:
    time_start = time.perf_counter()
    epd.prepare()

    timecode_int = int(progress_log["frame"] * video_info["frame_time"])
    timecode_str = f"{timecode_int}ms"
    get_frame_from_video(progress_log["file"], FRAME_TEMP_FILE, timecode_str)

    pil_image = Image.open(FRAME_TEMP_FILE)
    epd.display(pil_image)

    # Increment our frame
    # TODO: frames-per-increment
    progress_log["frame"] += 1
    if progress_log["frame"] > video_info["frame_count"] and progress_log["loop"]:
        # We're past the end of the file, and we're looping.
        progress_log["frame"] = 0
        # TODO: Handle playlist mode.
        # load next file in the directory.
    
    # If we get here, we just write our progress log and continue.
    with PROGRESS_FILE.open('w') as f:
        json.dump(progress_log, f)

    # Sleep until our next iteration.
    epd.sleep()
    time_diff = time.perf_counter() - time_start
    time.sleep(max(args.delay - time_diff, ))
