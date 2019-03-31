import os
from pathlib import Path

import pytest

from .. import cli


@pytest.fixture
def cleancwd(tmp_path):
    oldcwd = Path.cwd()
    newcwd = tmp_path / "cleancwd"
    newcwd.mkdir(exist_ok=True)
    os.chdir(str(newcwd))
    try:
        yield newcwd
    finally:
        os.chdir(str(oldcwd))


@pytest.fixture
def initialized(cleancwd):
    cli.run(["--verbose", "init"])
    return cleancwd
