import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def errexit(msg: str, code: int = 1, ex: Optional[Exception] = None):
    if ex:
        msg += f" [{ex.__class__.__name__}] {ex}"
    logger.error(msg)
    if ex:
        if isinstance(ex, subprocess.CalledProcessError):
            logger.info("[Process stdout] %s", ex.stdout.decode("utf-8"))
            logger.error("[Process stderr] %s", ex.stderr.decode("utf-8"))
        logger.debug("[Traceback]", exc_info=True)
    exit(code)
