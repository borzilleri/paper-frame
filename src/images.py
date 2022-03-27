from pathlib import Path
from PIL import Image

def load_image(image_path: Path) -> Image:
    return Image.open(image_path)
