import os
from pathlib import Path

import pytest

from .. import cli
from ..utils import pathstr


@pytest.fixture
def cleancwd(tmp_path):
    oldcwd = Path.cwd()
    newcwd = tmp_path / "cleancwd"
    newcwd.mkdir(exist_ok=True)
    os.chdir(pathstr(newcwd))
    try:
        yield newcwd
    finally:
        os.chdir(pathstr(oldcwd))


@pytest.fixture
def initialized(cleancwd):
    cli.run(["--verbose", "init"])
    return cleancwd
