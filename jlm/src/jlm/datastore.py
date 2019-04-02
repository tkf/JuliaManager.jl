import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path

from . import __version__
from .utils import KnownError, pathstr


@contextmanager
def atomicopen(path, *args):
    tmppath = Path("{}.{}.tmp".format(path, os.getpid()))
    try:
        with open(pathstr(tmppath), *args) as file:
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
    return None


class BaseStore:
    def execpath(self, julia):
        assert Path(julia).is_absolute()
        m = hashlib.sha1(julia.encode("utf-8"))
        return self.path / "exec" / m.hexdigest()


class HomeStore(BaseStore):

    defaultpath = Path.home() / ".julia" / "jlm"

    def __init__(self, path=defaultpath):
        self.path = Path(path)


class LocalStore(BaseStore):
    def locate_path(self):
        return locate_localstore(Path.cwd())

    def find_path(self):
        path = self.locate_path()
        if path is None:
            raise KnownError("Cannot locate `.jlm` local directory")
        return path

    @property
    def path(self):
        try:
            return self._path
        except AttributeError:
            pass

        self.path = self.find_path()
        return self._path

    @path.setter
    def path(self, value):
        self._path = Path(value)

    def exists(self):
        path = self.locate_path()
        return path is not None and (path / "data.json").exists()

    def loaddata(self):
        if self.exists():
            datapath = self.path / "data.json"
            with open(pathstr(datapath)) as file:
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
            assert isinstance(config["default"], str)
            data["config"]["default"] = config["default"]
        if "runtime" in config:
            data["config"]["runtime"].update(config["runtime"])

        self.storedata(data)

    def has_default_julia(self):
        return "default" in self.loaddata()["config"]

    @property
    def default_julia(self):
        config = self.loaddata()["config"]
        try:
            return config["default"]
        except KeyError:
            raise AttributeError

    def sysimage(self, julia):
        return self.loaddata()["config"]["runtime"].get(julia, None)

    def set_sysimage(self, julia, sysimage):
        config = self.loaddata()["config"]
        config["runtime"][julia] = pathstr(sysimage)
        self.set(config)

    def unset_sysimage(self, julia):
        data = self.loaddata()
        data["config"]["runtime"].pop(julia, None)
        self.storedata(data)
