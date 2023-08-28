from epdproxy import FAKE_EPD_DRIVER
from pathlib import Path

VALID_IMAGE_TYPES = [".bmp", ".jpg", ".jpeg", ".png", ".tiff"]
VALID_VIDEO_TYPES = [".avi", ".mp4", ".m4v", ".mkv", ".mov"]

PLAYLIST_SAVE_FILE = "playlist-save.json"
PLAYLIST_DEFINITION_FILE = "playlist.json"
DEFAULT_PLAYLIST = str(Path(Path.cwd(), PLAYLIST_DEFINITION_FILE))
DEFAULT_EPD = FAKE_EPD_DRIVER
DEFAULT_DATA_DIR = str(Path.cwd())
DEFAULT_LOG_LEVEL = "INFO"
