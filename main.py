import argparse
import signal
import sys
from typing import Any, Optional
import epdproxy
import paperframe
from paperframe import LOG, Config

DEFAULT_CONFIG_PATH = "config.toml"

__epd: Optional[epdproxy.EPD]


def exit_handler(signum: Any, frame: Any):
    try:
        if __epd is not None:
            __epd.close()
    finally:
        sys.exit()


def init_signal_handlers():
    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)


def get_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to config TOML file.",
    )
    parser.add_argument(
        "--playlist",
        help="Path to the playlist config TOML file.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    init_signal_handlers()
    args = get_cli_args()
    paperframe.init_config(args.config)
    paperframe.init_logger(Config.log_level)
    LOG.debug(Config.to_str())

    # Set up e-paper display
    try:
        __epd = epdproxy.epdfactory.load_epd(Config.epd, LOG.getEffectiveLevel())
    except Exception as e:
        LOG.error("Exiting with exception.", exc_info=e)
        sys.exit(1)

    playlist = paperframe.init_playlist(args.playlist)
    LOG.debug(f"Loaded playlist: {playlist}")
    paperframe.start_playback(playlist, __epd)
