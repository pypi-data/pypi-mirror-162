from pathlib import Path

import single_version

__version__ = single_version.get_version(__name__, Path(__file__).parent.parent)
