import pytest

from ..cli import Application, parse_args


def run_args(**kwargs):
    return dict(dict(func=Application.cli_run, julia="julia", arguments=[]), **kwargs)


@pytest.mark.parametrize(
    "args, included",
    [
        (["run"], run_args()),
        (["run", "-i"], run_args(arguments=["-i"])),
        (["run", "--", "-i"], run_args(arguments=["-i"])),
        (["run", "-i", "--"], run_args(arguments=["-i", "--"])),
        (["run", "bin/julia"], run_args(julia="bin/julia")),
        (
            ["run", "bin/julia", "--", "-i"],
            run_args(julia="bin/julia", arguments=["-i"]),
        ),
        (
            ["run", "bin/julia", "-i", "--"],
            run_args(julia="bin/julia", arguments=["-i", "--"]),
        ),
    ],
)
def test_parse_args(args, included):
    ns = parse_args(args)
    actual = {k: v for (k, v) in vars(ns).items() if k in included}
    assert actual == included
