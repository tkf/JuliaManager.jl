import os
import shlex
import subprocess
import sys
from pathlib import Path
from shutil import which

from .datastore import HomeStore, LocalStore
from .utils import KnownError, dlext


class Runtime:
    @classmethod
    def consume(cls, dry_run, verbose, **kwargs):
        return cls(dry_run, verbose), kwargs

    def __init__(self, dry_run, verbose):
        self.dry_run = dry_run
        self.verbose = verbose
        self._verbose = dry_run or verbose

    def print(self, message):
        print(message)
        # TODO: hide when "quiet"

    def info(self, message):
        if self._verbose:
            print(message)

    def warn(self, message):
        print(message, file=sys.stderr)

    def check_call(self, cmd, **kwargs):
        self.info("Run: " + " ".join(map(shlex.quote, cmd)))
        if self.dry_run:
            return
        subprocess.check_call(cmd, *kwargs)

    def ensuredir(self, path):
        path = Path(path)
        if path.is_dir():
            return
        self.info("Directory {} does not exist. Creating...".format(path))
        if not self.dry_run:
            path.mkdir(parents=True)


class Application:
    @classmethod
    def consume(cls, dry_run, verbose, julia=None, **kwargs):
        return cls(dry_run, verbose, julia), kwargs

    def __init__(self, dry_run, verbose, julia):
        _julia = julia
        if julia is not None:
            _julia = which(julia)
            if _julia is None:
                raise KnownError("Julia executable {} is not found".format(julia))

        self.dry_run = dry_run
        self.verbose = verbose
        self.julia = _julia
        self.rt = Runtime(dry_run, verbose)
        self.homestore = HomeStore()
        self.localstore = LocalStore(Path.cwd() / ".jlm")

    sysimage_name = "sys." + dlext

    def default_sysimage(self, julia):
        return self.homestore.execpath(julia) / self.sysimage_name

    @property
    def effective_sysimage(self):
        julia = self.effective_julia
        return self.localstore.sysimage(julia) or self.default_sysimage(julia)

    @property
    def effective_julia(self):
        if self.julia is not None:
            return self.julia
        return self.localstore.default_julia

    def julia_cmd(self):
        cmd = [self.effective_julia]
        cmd.extend(["--sysimage", self.effective_sysimage])
        return cmd

    @property
    def precompile_key(self):
        return self.effective_sysimage

    def compile_patched_sysimage(self, sysimage):
        code = """
        using JuliaManager: compile_patched_sysimage
        compile_patched_sysimage(ARGS[1])
        """
        self.rt.check_call([self.julia, "-e", code, str(sysimage)])

    def create_default_sysimage(self):
        sysimage = self.default_sysimage(self.julia)
        self.rt.ensuredir(sysimage.parent)
        self.compile_patched_sysimage(sysimage)

    def ensure_default_sysimage(self):
        sysimage = self.default_sysimage(self.julia)
        if sysimage.exists():
            self.rt.print("Default system image {} already exists.".format(sysimage))
            return
        self.create_default_sysimage()

    def initialize_localstore(self):
        self.rt.ensuredir(self.localstore.path)

    def cli_run(self, arguments):
        env = os.environ.copy()
        env["JLM_PRECOMPILE_KEY"] = self.precompile_key
        cmd = self.julia_cmd()
        cmd.extend(arguments)
        os.execvpe(cmd[0], cmd, env)

    def cli_init(self, sysimage):
        self.initialize_localstore()
        config = {"default": self.julia}
        if sysimage:
            config.update({"runtime": {self.julia: {"sysimage": sysimage}}})
        else:
            self.ensure_default_sysimage()
        if not self.dry_run:
            self.localstore.set(config)

    def cli_set_default(self):
        """ Set default Julia executable to be used. """
        self.localstore.set({"default": self.julia})

    def cli_set_sysimage(self, sysimage):
        """ Set system image for `juila`. """
        self.localstore.set_sysimage(self.julia, sysimage)

    def cli_unset_sysimage(self):
        """ Unset system image for `juila`. """
        self.localstore.unset_sysimage(self.julia)

    def cli_create_default_sysimage(self):
        """ Compile default system image for `julia`. """
        self.create_default_sysimage()
