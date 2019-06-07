import os
import pathlib
import sys
from pathlib import Path
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


def absolutepath(path: _Pathish) -> Path:
    # `Path.absolute` is not a public API
    # (https://bugs.python.org/issue29688) so let's be a bit careful.
    p = Path(path)
    assert p.absolute().resolve() == p.resolve()
    return p.absolute()


class ApplicationError(RuntimeError):
    pass
