import sys
import subprocess

import pytest

from .. import cli


def test_init(initialized):
    assert (initialized / ".jlm").is_dir()


@pytest.mark.parametrize(
    "args",
    [
        ["create-default-sysimage"],
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
    assert (initialized / ".jlm").is_dir()
