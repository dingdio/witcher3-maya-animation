__version__ = "0.0.1"


def version():
    """
    Return the current version of the Witcher 3 Tools

    :rtype: str
    """
    return __version__

import w3tool
reload(w3tool)
