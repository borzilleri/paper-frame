from pathlib import Path
from PIL import Image
from typing import Optional

from .log import LOG


def load_image(image_path: Path) -> Optional[Image.Image]:
    try:
        img: Optional[Image.Image] = Image.open(image_path)
        LOG.debug(f"Loaded image {str(image_path)}")
        return img
    except Exception as e:
        LOG.error(f"Unable to load image: {str(image_path)}", e)
