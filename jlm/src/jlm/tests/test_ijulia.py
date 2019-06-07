import json

from .. import cli


def test_install(tmp_path):
    kernelname = "test-kernel-name"
    kerneldir = tmp_path / kernelname
    cli.run(
        [
            "--verbose",
            "install-ijulia-kernel",
            "--output-dir",
            str(kerneldir),
            "--dont-store-jlm-dir",
        ]
    )

    with open(str(kerneldir / "kernel.json")) as file:
        kernelspec = json.load(file)

    assert kernelspec["argv"][0].endswith("jlm")
    assert "--jlm-dir" not in kernelspec["argv"]
    assert kernelspec["display_name"] == kernelname
    assert kernelspec["language"] == "julia"
