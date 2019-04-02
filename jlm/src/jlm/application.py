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

    def info_run(self, cmd):
        self.info("Run: " + " ".join(map(shlex.quote, cmd)))

    def check_call(self, cmd, **kwargs):
        self.info_run(cmd)
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
        # TODO: do not put `julia` in `self.juila`
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
        self.localstore = LocalStore()

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
        try:
            return self.localstore.default_julia
        except AttributeError:
            pass
        julia = which("julia")
        if julia is None:
            raise KnownError("Julia executable `julia` is not found.")
        return julia

    def julia_cmd(self):
        cmd = [str(self.effective_julia)]
        cmd.extend(["--sysimage", str(self.effective_sysimage)])
        return cmd

    @property
    def precompile_key(self):
        return str(self.effective_sysimage)

    def compile_patched_sysimage(self, julia, sysimage):
        code = """
        using JuliaManager: compile_patched_sysimage
        compile_patched_sysimage(ARGS[1])
        """
        self.rt.check_call([julia, "-e", code, str(sysimage)])

    def create_default_sysimage(self, julia):
        sysimage = self.default_sysimage(julia)
        self.rt.ensuredir(sysimage.parent)
        self.compile_patched_sysimage(julia, sysimage)

    def ensure_default_sysimage(self, julia):
        sysimage = self.default_sysimage(julia)
        if sysimage.exists():
            self.rt.print("Default system image {} already exists.".format(sysimage))
            return
        self.create_default_sysimage(julia)

    def initialize_localstore(self):
        self.localstore.path = Path.cwd() / ".jlm"
        self.rt.ensuredir(self.localstore.path)

    def cli_run(self, arguments):
        assert all(isinstance(a, str) for a in arguments)
        env = os.environ.copy()
        env["JLM_PRECOMPILE_KEY"] = self.precompile_key
        cmd = self.julia_cmd()
        cmd.extend(arguments)
        self.rt.info_run(cmd)
        if self.dry_run:
            return
        os.execvpe(cmd[0], cmd, env)

    def cli_init(self, sysimage):
        self.initialize_localstore()
        julia = self.julia
        effective_julia = self.effective_julia  # `julia` or which("julia")
        config = {}
        if julia:
            config["default"] = julia
        if sysimage:
            config.update({"runtime": {effective_julia: {"sysimage": sysimage}}})
        else:
            self.ensure_default_sysimage(effective_julia)
        if not self.dry_run:
            self.localstore.set(config)

    def cli_set_default(self):
        """ Set default Julia executable to be used. """
        self.localstore.set({"default": self.julia})

    def cli_set_sysimage(self, sysimage):
        """ Set system image for `juila`. """

        sysimage = Path(sysimage)
        if not sysimage.is_absolute():
            sysimage = Path.cwd() / sysimage
            # Don't `.resolve()` here to avoid resolving symlinks.
            # User may re-link sysimage and `jlm run` to use the new
            # target.  It would be useful, e.g., when sysimage is
            # stored in git-annex.

        self.localstore.set_sysimage(self.julia, sysimage)

    def cli_unset_sysimage(self):
        """ Unset system image for `juila`. """
        self.localstore.unset_sysimage(self.julia)

    def cli_create_default_sysimage(self, force):
        """ Compile default system image for `julia`. """
        julia = self.effective_julia
        if force:
            self.create_default_sysimage(julia)
        else:
            self.ensure_default_sysimage(julia)

    def cli_locate_sysimage(self):
        """ Print system image that would be used for `julia`. """
        print(self.effective_sysimage, end="")

    def cli_locate_base(self):
        """ Print directory for which `jlm init` was executed. """
        print(self.localstore.path.parent, end="")

    def cli_locate_local_dir(self):
        """ Print directory in which `jlm` information is stored. """
        print(self.localstore.path, end="")

    def cli_locate_home_dir(self):
        """ Print directory in which `jlm` global information is stored. """
        print(self.homestore.path, end="")
