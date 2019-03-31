import os
import sys

iswindows = os.name == "nt"
isapple = sys.platform == "darwin"

# See: Libdl.jl
if isapple:
    dlext = "dylib"
elif iswindows:
    dlext = "dll"
else:
    dlext = "so"


class KnownError(RuntimeError):
    pass
