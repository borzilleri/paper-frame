import json
from pathlib import Path

from configargparse import ArgumentTypeError

from .constants import VALID_IMAGE_TYPES, VALID_VIDEO_TYPES, Mode


def validate_path_type(value) -> Path:
    path = Path(value).expanduser().absolute()
    if not path.is_file() and not path.is_dir():
        raise ArgumentTypeError(f"Path '{value}' must be a valid file or directory.")
    return path


def validate_path_and_mode(mode: Mode, value: Path) -> None:
    if mode in (Mode.ALBUM, Mode.PLAYLIST) and not value.is_dir():
        raise ArgumentTypeError(
            f"Path '{value}' must be a directory for mode {mode.name}"
        )
    if mode == Mode.IMAGE and value.suffix not in VALID_IMAGE_TYPES:
        raise ArgumentTypeError(
            f"Path '{value}' must be a file with a supported extension: {', '.join(VALID_IMAGE_TYPES)}"
        )
    if mode == Mode.VIDEO and value.suffix not in VALID_VIDEO_TYPES:
        raise ArgumentTypeError(
            f"Path '{value}' must be a file with a supported extension: {', '.join(VALID_VIDEO_TYPES)}"
        )
