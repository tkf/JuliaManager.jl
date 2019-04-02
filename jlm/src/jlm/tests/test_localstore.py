import pytest

from ..datastore import LocalStore
from ..utils import KnownError


def test_non_abspath(cleancwd):
    path = cleancwd / "a" / "b" / "c"
    path.mkdir(parents=True)

    store = LocalStore()

    with pytest.raises(ValueError):
        store.path = str(path.relative_to(cleancwd))

    # Should it be an AttributeError?
    with pytest.raises(KnownError):
        store.path

    store.path = str(path)
    assert store.path == path
