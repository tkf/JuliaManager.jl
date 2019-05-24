import os
import pathlib
import sys
from typing import List, Tuple, Union

Cmd = List[str]

_Pathish = Union[str, pathlib.PurePath]

try:
    Pathish = (str, os.PathLike)  # type: Tuple
except AttributeError:
    Pathish = (str, pathlib.PurePath)
    try:
        import pathlib2  # type: ignore
    except ImportError:
        pass
    else:
        Pathish += (pathlib2.PurePath,)

iswindows = os.name == "nt"  # type: bool
isapple = sys.platform == "darwin"  # type: bool

# See: Libdl.jl
if isapple:
    dlext = "dylib"
elif iswindows:
    dlext = "dll"
else:
    dlext = "so"


def pathstr(path: _Pathish) -> str:
    if not isinstance(path, Pathish):
        raise ValueError("Not a path or a string:\n{!r}".format(path))
    return str(path)


class ApplicationError(RuntimeError):
    pass
