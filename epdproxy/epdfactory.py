import logging

from PIL import Image

logger = logging.getLogger()


class FakeEPD:
    width = 800
    height = 480

    def __init__(self, driver_name):
        self.driver = driver_name

    def prepare(self):
        logger.debug("ProxyEPD->prepare() called.")

    def sleep(self):
        logger.debug("ProxyEPD->sleep() called")

    def display(self, image: Image):
        logger.debug(f"ProxyEPD->display() called with {image}")

    def clear(self):
        logger.debug("ProxyEPD->clear() called.")

    def close(self):
        logger.debug("ProxyEPD->close() called.")


class EPD:
    epd = None
    width = 0
    height = 0

    def __init__(self, epd):
        self.epd = FakeEPD() if epd is None else epd
        self.width = epd.width
        self.height = epd.height

    def prepare(self):
        self.epd.prepare()

    def display(self, image: Image):
        self.epd.display(image)

    def sleep(self):
        self.epd.sleep()

    def clear(self):
        self.epd.clear()

    def close(self):
        self.epd.close()


class fakeEpdFactory:
    def load_display_driver(self, driver_name):
        return FakeEPD(driver_name)

    def list_supported_displays():
        return list("proxy-display")


def load_epd(driver_name: str) -> EPD:
    try:
        from omni_epd import displayfactory

        local_display_factory = displayfactory
    except ModuleNotFoundError:
        local_display_factory = fakeEpdFactory()
    try:
        epd = local_display_factory.load_display_driver(driver_name)
        return EPD(epd)
    except Exception as e:
        validEpds = displayfactory.list_supported_displays()
        logger.error(
            "f'{args.epd}' is not a valid e-paper display name, valid names are:"
        )
        logger.error("\n".join(map(str, validEpds)))
        raise e
