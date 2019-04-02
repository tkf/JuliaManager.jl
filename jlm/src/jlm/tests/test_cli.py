import os
import subprocess
import sys

import pytest

from .. import cli
from ..utils import dlext, pathstr


def test_init(initialized):
    assert (initialized / ".jlm").is_dir()


@pytest.mark.parametrize(
    "args",
    [
        ["create-default-sysimage"],
        ["--dry-run", "create-default-sysimage", "--force"],
        ["set-default", "julia"],
        ["set-sysimage", "/dev/null"],
        ["unset-sysimage"],
        ["locate", "sysimage"],
        ["locate", "sysimage", "julia"],
        ["locate", "base"],
        ["locate", "dir"],
        ["locate", "home-dir"],
    ],
)
def test_smoke(initialized, args):
    cli.run(args)


@pytest.mark.parametrize(
    "args",
    [
        ["--dry-run", "create-default-sysimage"],
        ["--dry-run", "create-default-sysimage", "--force"],
        ["locate", "home-dir"],
    ],
)
def test_smome_non_initialized(args):
    cli.run(args)


def test_run(initialized):
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            cli.__name__,
            "--verbose",
            "run",
            "--startup-file=no",
            "-e",
            "Base.banner()",
        ]
    )


def test_relative_sysimage(initialized):
    app = cli.Application(dry_run=False, verbose=True, julia="julia")

    sysimage = initialized / "some" / "dir" / ("sys." + dlext)
    sysimage.parent.mkdir(parents=True)
    sysimage.symlink_to(app.default_sysimage(app.julia))

    cli.run(["--verbose", "set-sysimage", pathstr(sysimage.relative_to(initialized))])
    test_run(initialized)
    cli.run(["locate", "sysimage"])
    print()

    otherdir = initialized / "some" / "other" / "dir"
    otherdir.mkdir(parents=True)
    os.chdir(pathstr(otherdir))

    test_run(initialized)
    cli.run(["locate", "sysimage"])
    print()
