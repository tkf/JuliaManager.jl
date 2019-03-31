import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path

from . import __version__


@contextmanager
def atomicopen(path, *args):
    tmppath = Path("{}.{}.tmp".format(path, os.getpid()))
    try:
        with open(str(tmppath), *args) as file:
            yield file
        tmppath.rename(path)
    finally:
        if tmppath.exists():
            os.remove(tmppath)


class BaseStore:
    @property
    def execpath(self):
        m = hashlib.sha1(self.julia.encode("utf-8"))
        return self.path / "exec" / m.hexdigest()


class HomeStore(BaseStore):

    defaultpath = Path.home() / ".julia" / "jlm"

    def __init__(self, julia, path=defaultpath):
        self.julia = julia
        self.path = Path(path)


class LocalStore(BaseStore):
    def __init__(self, julia, path):
        self.julia = julia
        self.path = Path(path)

    def loaddata(self):
        datapath = self.path / "data.json"
        if datapath.exists():
            with open(str(datapath)) as file:
                return json.load(file)
        return {
            "name": "jlm.LocalStore",
            "jlm_version": __version__,
            "config": {"runtime": {}},
        }

    def set(self, config):
        datapath = self.path / "data.json"
        data = self.loaddata()

        if "default" in config:
            data["config"]["default"] = config["default"]
        if "runtime" in config:
            data["config"]["runtime"].update(config["runtime"])

        with atomicopen(datapath, "w") as file:
            json.dump(data, file)
