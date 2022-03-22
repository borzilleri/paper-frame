#

# Inspired by, and much of the code borrowed from:
# https://github.com/TomWhitwell/SlowMovie

import signal
import sys
import configargparse
import time
from pprint import pformat
from epdproxy import displayfactory, EPDNotFoundError
from src.log import logger, get_logging_level
from src import util, video, progresslog
from src.constants import MODES


def exithandler(signum, frame):
    try:
        epd.close()
    finally:
        sys.exit()


# Add interrupt/termination signal hooks
signal.signal(signal.SIGTERM, exithandler)
signal.signal(signal.SIGINT, exithandler)

# Setup CLI arguments
parser = configargparse.ArgParser(default_config_files=["default.conf"])
parser.add_argument(
    "mode",
    choices=MODES.keys(),
    help="Display mode, single image, single video, album of images, or playlsit of videos",
)
parser.add_argument(
    "-d",
    "--dir",
    type=util.validate_dir,
    help="Directory to search for images or videos for the album and playlist display modes.",
)
parser.add_argument(
    "-f",
    "--file",
    type=util.validate_file,
    help="Image or Video file to display, for those display modes.",
)
parser.add_argument(
    "-r",
    "--random",
    action="store_true",
    help="In album or playlist mode, play files in a random orer.",
)
parser.add_argument(
    "-l",
    "--loop",
    action="store_true",
    help="In album or playlist modes, loop over files in the directory. In video mode loops the specified file.",
)
parser.add_argument(
    "-w",
    "--wait",
    type=int,
    default=120,
    help="wait in seconds between screen updates. (dfeault: %(default)s)",
)

parser.add_argument(
    "-R",
    "--resume",
    action="store_true",
    help="Attempt to resume and continue a previous execution, defaults to mode parameter if no previous execution found",
)
parser.add_argument("-e", "--epd", help="Name of epaper display driver to use.")
parser.add_argument(
    "-o",
    "--loglevel",
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="minimum importance-level of messages displayed and saved to the logfile (default: %(default)s)",
)
args = parser.parse_args()

logger.setLevel(get_logging_level(args.loglevel))
logger.debug(pformat(args))

# Set up e-paper display
try:
    epd = displayfactory.load_display_driver(args.epd)
except EPDNotFoundError:
    validEpds = displayfactory.list_supported_displays()
    logger.error("f'{args.epd}' is not a valid e-paper display name, valid names are:")
    logger.error("\n".join(map(str, validEpds)))
    sys.exit(1)


def display_image():
    print("displaying image")


### If mode=resume, load progerss log and continue
progress_log = progresslog.load(args.resume, args.mode, args.dir, args.file, args.random, args.loop)
## Load our next video
video_info = video.get_video_info(str(progress_log.path))

while video_info is not None and progress_log.frame <= video_info["frame_count"]:
    time_start = time.perf_counter()
    epd.prepare()

    timecode_ms = f"{int(progress_log.frame * video_info['frame_time'])}ms"

    image = video.get_frame_from_video(str(progress_log.path), epd.width, epd.height, timecode_ms)
    if image is not None:
        logger.debug(
            f"Displaying frame {progress_log.frame} of {progress_log.path} ({(progress_log.frame/video_info['frame_count'])*100:.1f}%)"
        )
        epd.display(image)
    else:
        logger.error(
            f"Unable to retrieve frame for {progress_log.path} : {timecode_ms}"
        )

    # Increment our frame
    progress_log.frame += 1
    if progress_log.frame > video_info["frame_count"] and progress_log.loop:
        # We're past the end of the file, and we're looping.
        progress_log.frame = 0

    # If we get here, we just write our progress log and continue.
    progresslog.save(progress_log)

    # Sleep until our next iteration.
    epd.sleep()
    time_diff = time.perf_counter() - time_start
    time.sleep(max(args.wait - time_diff, 0))
