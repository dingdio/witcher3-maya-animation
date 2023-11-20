__version__ = "0.0.2"


def version():
    """
    Return the current version of the Witcher 3 Tools

    :rtype: str
    """
    return __version__

import sys
from pathlib import Path

current_module_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_module_dir))

import w3tool

from importlib import reload
reload(w3tool)