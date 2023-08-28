import json
from pathlib import Path
from typing import Any, Dict

from .constants import VALID_VIDEO_TYPES, VALID_IMAGE_TYPES


def is_video(f: Path) -> bool:
    return f.is_file() and f.suffix in VALID_VIDEO_TYPES


def is_image(f: Path) -> bool:
    return f.is_file() and f.suffix in VALID_IMAGE_TYPES


def is_valid_media(f: Path) -> bool:
    return is_image(f) or is_video(f)


def load_config(file_path: str) -> Dict[str, Any]:
    real_path: Path = Path(file_path).expanduser().absolute()
    if not real_path.is_file():
        raise Exception(f"Playlist file is not readable: {real_path}")
    with real_path.open("rb") as f:
        return json.load(f)
