"test __version__ property."
from importlib.metadata import version as _version

import pycheck


def test_version():
    "test __version__ property."
    assert pycheck.__version__ == _version("pycheck")
