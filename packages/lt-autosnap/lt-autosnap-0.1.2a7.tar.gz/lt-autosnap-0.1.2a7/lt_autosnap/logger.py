"""Logger for this package"""
import logging
from typing import Union

logging.basicConfig(format="%(levelname)7s: %(message)s", level=logging.WARNING)
daemon_formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s")


def set_daemon_formatter():
    logging.root.handlers[0].setFormatter(daemon_formatter)


def set_loglevel(level: Union[int, str]):
    logging.root.setLevel(level)
