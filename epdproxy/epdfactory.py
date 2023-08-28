import logging

from PIL import Image
from typing import Any

import importlib

logger = logging.getLogger()

FAKE_EPD_DRIVER = "fakeEpdDriver"


class FakeEPD:
    width: int = 800
    height: int = 480

    def __init__(self, driver_name: str):
        self.driver = driver_name

    def prepare(self):
        logger.debug("ProxyEPD->prepare() called.")

    def sleep(self):
        logger.debug("ProxyEPD->sleep() called")

    def display(self, image: Image.Image):
        logger.debug(f"ProxyEPD->display() called with {image}")

    def clear(self):
        logger.debug("ProxyEPD->clear() called.")

    def close(self):
        logger.debug("ProxyEPD->close() called.")


class EPD:
    epd: Any
    width: int = 0
    height: int = 0

    def __init__(self, epd: Any):
        self.epd = FakeEPD(FAKE_EPD_DRIVER) if epd is None else epd
        self.width = epd.width
        self.height = epd.height

    def prepare(self):
        self.epd.prepare()

    def display(self, image: Image.Image):
        self.epd.display(image)

    def sleep(self):
        self.epd.sleep()

    def clear(self):
        self.epd.clear()

    def close(self):
        self.epd.close()


class fakeEpdFactory:
    def load_display_driver(self, driver_name: str):
        return FakeEPD(driver_name)

    def list_supported_displays(self):
        return list(FAKE_EPD_DRIVER)


def load_epd(driver_name: str, log_level: int) -> EPD:
    logger.setLevel(log_level)
    displayfactory: Any = fakeEpdFactory()
    try:
        displayfactory = importlib.import_module("omni_epd.displayfactory")
    except ModuleNotFoundError:
        pass
    try:
        epd: Any = displayfactory.load_display_driver(driver_name)
        return EPD(epd)
    except Exception as e:
        validEpds = "\n".join(map(str, displayfactory.list_supported_displays()))
        logger.error(
            f"'{driver_name}' is not a valid e-paper display name. valid names are: {validEpds}"
        )
        raise e
