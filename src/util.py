import json
from pathlib import Path

import configargparse

from .constants import VALID_VIDEO_TYPES


def validate_file(value):
    path = Path(value).expanduser().absolute()
    if not path.is_file():
        raise configargparse.ArgumentTypeError(
            f"File '{value}' does not exist or is not a file."
        )
    if path.suffix not in VALID_VIDEO_TYPES:
        raise configargparse.ArgumentTypeError(
            f"File '{value}' should be a file with one of the following supported extensions: {', '.join(VALID_VIDEO_TYPES)}"
        )
    return path


def validate_dir(value: Path):
    path = Path(value).expanduser().absolute()
    if path.is_dir():
        return path
    else:
        raise configargparse.ArgumentTypeError(
            f"Directory '{value}' does not exist or is not a directory."
        )


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return {"_type": "Path", "path": str(obj)}
        return json.JSONEncoder.default(self, obj)


class CustomJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "_type" in obj:
            if obj["_type"] == "Path":
                return Path(obj["path"])
        return obj
