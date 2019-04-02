import os
import sys
from pathlib import PurePath

iswindows = os.name == "nt"
isapple = sys.platform == "darwin"

# See: Libdl.jl
if isapple:
    dlext = "dylib"
elif iswindows:
    dlext = "dll"
else:
    dlext = "so"


def pathstr(path):
    if not isinstance(path, (PurePath, str)):
        raise ValueError("Not a path or a string:\n{!r}".format(path))
    return str(path)


class KnownError(RuntimeError):
    pass
