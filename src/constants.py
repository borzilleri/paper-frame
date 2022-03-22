from pathlib import Path

VALID_VIDEO_TYPES = [".avi", ".mp4", ".m4v", ".mkv", ".mov"]
FRAME_TEMP_FILE = Path("/tmp/frame.bmp") # Path("/dev/shm/frame.bmp")
PROGRESS_FILE = Path.cwd().joinpath("progress_log.json") # Path.home().joinpath(".paper-frame-data/progress_log.json")
MODES = {"image": {}, "video": {}, "album": {}, "playlist": {}}
