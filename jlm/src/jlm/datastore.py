import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from shutil import which
from typing import IO, Any, Dict, Iterator, List, Optional, Tuple

from . import __version__
from .runtime import JuliaRuntime
from .utils import ApplicationError, Pathish, _Pathish, absolutepath, pathstr


@contextmanager
def atomicopen(path: _Pathish, *args) -> Iterator[IO]:
    tmppath = Path("{}.{}.tmp".format(path, os.getpid()))
    try:
        with open(pathstr(tmppath), *args) as file:
            yield file
        tmppath.rename(path)
    finally:
        if tmppath.exists():
            os.remove(tmppath)


def locate_localstore(path: Path) -> Optional[Path]:
    prev = None
    while path != prev:
        candidate = path / ".jlm"
        if candidate.exists():
            return absolutepath(candidate)
        prev = path
        path = path.parent
    return None


class BaseStore:
    def execpath(self, julia: str) -> Path:
        assert Path(julia).is_absolute()
        m = hashlib.sha1(julia.encode("utf-8"))
        return self.path / "exec" / m.hexdigest()  # type: ignore


class HomeStore(BaseStore):

    # path: Path
    defaultpath = Path.home() / ".julia" / "jlm"

    def __init__(self, path: _Pathish = defaultpath):
        self.path = Path(path)


class LocalStore(BaseStore):
    @staticmethod
    def is_valid_path(path: _Pathish) -> bool:
        return (Path(path) / "data.json").exists()

    def __init__(self, path: Optional[_Pathish] = None):
        if path is not None:
            if not isinstance(path, Pathish):
                raise TypeError(
                    (
                        "`path` argument for `LocalStore(path)` must be a"
                        "`str` or `Path`, not {}"
                    ).format(type(path))
                )
            path = Path(path)
            if not self.is_valid_path(path):
                raise ApplicationError(
                    "{} is not a valid `.jlm` directory.".format(path)
                )
            self.path = path

    def locate_path(self) -> Optional[Path]:
        try:
            return self._path
        except AttributeError:
            return locate_localstore(Path.cwd())

    def find_path(self) -> Path:
        path = self.locate_path()
        if path is None:
            raise ApplicationError("Cannot locate `.jlm` local directory")
        return path

    # _path: Path

    @property
    def path(self) -> Path:
        try:
            return self._path
        except AttributeError:
            pass

        self.path = self.find_path()
        return self._path

    @path.setter
    def path(self, value: _Pathish):
        path = Path(value)
        if not path.is_absolute():
            raise ValueError("Not an absolute path:\n{}".format(path))
        self._path = path

    def exists(self) -> bool:
        path = self.locate_path()
        return path is not None and (path / "data.json").exists()

    def loaddata(self) -> Dict[str, Any]:
        if self.exists():
            datapath = self.path / "data.json"
            with open(pathstr(datapath)) as file:
                return json.load(file)  # type: ignore
        return {
            "name": "jlm.LocalStore",
            "jlm_version": __version__,
            "config": {"runtime": {}},
        }

    def storedata(self, data: Dict[str, Any]):
        with atomicopen(self.path / "data.json", "w") as file:
            json.dump(data, file)

    def set(self, config: Dict[str, Any]):
        data = self.loaddata()

        if "default" in config:
            assert isinstance(config["default"], str)
            data["config"]["default"] = config["default"]
        if "runtime" in config:
            data["config"]["runtime"].update(config["runtime"])

        self.storedata(data)

    def has_default_julia(self) -> bool:
        return "default" in self.loaddata()["config"]

    @property
    def default_julia(self) -> str:
        config = self.loaddata()["config"]
        try:
            return config["default"]
        except KeyError:
            raise AttributeError

    def sysimage(self, julia: str) -> Optional[str]:
        runtime = self.loaddata()["config"]["runtime"]
        try:
            return runtime[julia]["sysimage"]
        except KeyError:
            return None

    def set_sysimage(self, julia: str, sysimage: _Pathish):
        assert isinstance(julia, str)
        config = self.loaddata()["config"]
        config["runtime"][julia] = {"sysimage": pathstr(sysimage)}
        self.set(config)

    def unset_sysimage(self, julia: str):
        if not isinstance(julia, str):
            raise TypeError("`julia` must be a `str`, got: {!r}".format(julia))
        data = self.loaddata()
        data["config"]["runtime"].pop(julia, None)
        self.storedata(data)

    def available_runtimes(self) -> Tuple[JuliaRuntime, List[JuliaRuntime]]:
        config = self.loaddata()["config"]
        try:
            julia = config["default"]
        except KeyError:
            julia = which("julia")
        default = JuliaRuntime(julia, self.sysimage(julia))

        others = []
        for (julia, runtime) in config["runtime"].items():
            if julia != default.executable:
                others.append(JuliaRuntime(julia, runtime["sysimage"]))

        return default, others
