"""Wrappers for running system commands"""
import logging
import subprocess
from typing import List

logger = logging.getLogger(__name__)


def check_call(cmd: List[str], log=True):
    """Wrapper for subprocess.check_call"""
    # same as check_output with nothing returned
    check_output(cmd, log)


def check_output(cmd: List[str], log=True) -> bytes:
    """Wrapper for subprocess.check_output"""
    if log:
        logger.debug("cmd: %s", " ".join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return proc.stdout
