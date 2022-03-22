try:
    from omni_epd import displayfactory, EPDNotFoundError
except ModuleNotFoundError:
    from .epd import displayfactory, EPDNotFoundError
    