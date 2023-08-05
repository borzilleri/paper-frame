import tomllib
from pathlib import Path
from typing import Any

from .constants import VALID_VIDEO_TYPES, VALID_IMAGE_TYPES

def is_video(f: Path) -> bool:
    return f.is_file() and f.suffix in VALID_VIDEO_TYPES

def is_image(f: Path) -> bool:
    return f.is_file() and f.suffix in VALID_IMAGE_TYPES

def is_valid_media(f: Path) -> bool:
    return is_image(f) or is_video(f)

def load_config_to_object(file_path: str, out: object) -> Any:
    resolved_path: Path = Path(file_path).expanduser().absolute()
    if not resolved_path.is_file():
        raise Exception(f"Config file is '{file_path}' is not readable.")
    with resolved_path.open("rb") as f:
        data = tomllib.load(f)
        for k, v in data.items():
            setattr(out, k, v)
    return out
