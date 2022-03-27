import enum

VALID_VIDEO_TYPES = [".avi", ".mp4", ".m4v", ".mkv", ".mov"]

class Mode(enum.Enum):
    IMAGE = enum.auto()
    ALBUM = enum.auto()
    VIDEO = enum.auto()
    PLAYLIST = enum.auto()
