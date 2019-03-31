import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path

from . import __version__
from .utils import KnownError


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


def locate_localstore(path):
    prev = None
    while path != prev:
        candidate = path / ".jlm"
        if candidate.exists():
            return candidate.resolve()
        prev = path
        path = path.parent
    raise KnownError("Cannot locate `.jlm` local directory")


class BaseStore:
    def execpath(self, julia):
        m = hashlib.sha1(julia.encode("utf-8"))
        return self.path / "exec" / m.hexdigest()


class HomeStore(BaseStore):

    defaultpath = Path.home() / ".julia" / "jlm"

    def __init__(self, path=defaultpath):
        self.path = Path(path)


class LocalStore(BaseStore):
    @property
    def path(self):
        try:
            return self._path
        except AttributeError:
            pass

        self.path = locate_localstore()
        return self._path

    @path.setter
    def path(self, value):
        self._path = Path(value)

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

    def storedata(self, data):
        with atomicopen(self.path / "data.json", "w") as file:
            json.dump(data, file)

    def set(self, config):
        data = self.loaddata()

        if "default" in config:
            data["config"]["default"] = config["default"]
        if "runtime" in config:
            data["config"]["runtime"].update(config["runtime"])

        self.storedata(data)

    @property
    def default_julia(self):
        return self.loaddata()["config"]["default"]

    def sysimage(self, julia):
        return self.loaddata()["config"]["runtime"].get(julia, None)

    def set_sysimage(self, julia, sysimage):
        config = self.loaddata()["config"]
        config["runtime"][julia] = sysimage
        self.set(config)

    def unset_sysimage(self, julia):
        data = self.loaddata()
        data["config"]["runtime"].pop(julia, None)
        self.storedata(data)
