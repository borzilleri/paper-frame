import logging
from PIL import Image

logger = logging.getLogger()

canvas_width = 800
canvas_height = 480

class ProxyEPD():
    width = canvas_height
    height = canvas_height
    def prepare(self):
        logger.debug("ProxyEPD->prepare() called.")

    def sleep(self):
        logger.debug("ProxyEPD->sleep() called")

    def display(self, image: Image):
        logger.debug(f"ProxyEPD->display() called with {image}")

class EPDNotFoundError(Exception):
    pass

class displayfactory:
    def load_display_driver(driver_name):
        return ProxyEPD()
        
    def list_supported_displays():
        return list("proxy-display")
