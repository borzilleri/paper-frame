# Paper Frame - video/image display software for e-ink screens

# Inspired by, and much of the code borrowed from:
# https://github.com/TomWhitwell/SlowMovie

import signal
import sys
import configargparse
from pprint import pformat
from epdproxy import epdfactory
from src import images, job, util, videos
from src.log import logger, get_logging_level
from src.constants import Mode, DEFAULT_CONFIG_PATH
from src.config import init_config, config

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
    choices=[m.name.lower() for m in Mode],
    help="Display mode, single image, single video, album of images, or playlsit of videos",
)
parser.add_argument(
    "path",
    type=util.validate_path_type,
    help="Directory to search for album or playlist modes, or file to play for image or video modes."
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
parser.add_argument(
    "-C",
    "--clear",
    action="store_true",
    help="Clear the display when program exits. Not applicable to normal exit in IMAGE mode."
)
parser.add_argument(
    "--config",
    default=DEFAULT_CONFIG_PATH,
    help="Path to config json file."
)
parser.add_argument(
    "-o",
    "--loglevel",
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="minimum importance-level of messages displayed and saved to the logfile (default: %(default)s)",
)
args = parser.parse_args()
init_config(args.config)
util.validate_path_and_mode(args.mode, args.path)

logger.setLevel(get_logging_level(args.loglevel))
logger.debug(pformat(args))

# Set up e-paper display
try:
    epd = epdfactory.load_epd(config.EpdDriver)
except Exception as e:
    logger.error("Exiting with exception.", exc_info=e)
    sys.exit(1)

### If mode=resume, load progerss log and continue
current_job = job.build_job(args.resume, args.mode, args.path, args.random, args.loop)

if current_job.mode == Mode.IMAGE:
    logger.info(f"Displaying single image: {str(current_job.path)}")
    # Simply load & display our iamge.
    img = images.load_image(current_job.path)
    epd.prepare()
    epd.display(images)
elif current_job.mode == Mode.VIDEO:
    logger.info(f"Playing single video: {str(current_job.path)}")
    # Read our video info, then display it.
    video_info = videos.get_video_info(str(current_job.path))
    videos.display_video(epd, current_job, video_info, args.wait)
elif current_job.mode == Mode.ALBUM:
    logger.info(f"Displaying {len(current_job.files)} images from directory: {str(current_job.path)}")
    logger.error(f"{current_job.mode.name} not yet implemented.")
elif current_job.mode == Mode.PLAYLIST:
    logger.info(f"Playing  {len(current_job.files)} videos from directory: {str(current_job.path)}")
    logger.error(f"{current_job.mode.name} not yet implemented.")

if current_job.mode != Mode.IMAGE and args.clear:
    logger.info("Clearing display.")
    epd.clear()

logger.info("Program run finished.")
