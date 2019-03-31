"""
"""

import argparse
import subprocess
import sys

from .application import Application
from .utils import KnownError

doc_run = """
Run `julia` executable (or default executable configured by `jlm
init`) with appropriate system image.
"""

doc_init = """
Initialize `jlm`.

It does:

* Create a data store (`.jlm` directory).
* Install `JuliaManager.jl` if it is not installed for `<julia>`.  [TODO]
* Compile the (patched [#]_) default system image for `<julia>` if not
  already found and `--sysimage|-J` is not given.  This can be done
  separately by `jlm compile-default-sysimage`.
* Set the system image to be used for `<julia>`.  This can be re-done
  later by `set-sysimage`.

.. [#] `jlm` compiles the system image with a patch that does
   `Suggestion: Use different precompilation cache path for different
   system image by tkf · Pull Request #29914 · JuliaLang/julia
   <https://github.com/JuliaLang/julia/pull/29914>`_
"""


class FormatterClass(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def make_parser(doc=__doc__):
    parser = argparse.ArgumentParser(formatter_class=FormatterClass, description=doc)

    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--pdb", action="store_true")

    subparsers = parser.add_subparsers()

    def subp(command, func, doc):
        title = None
        for title in filter(None, map(str.strip, (doc or "").splitlines())):
            break
        p = subparsers.add_parser(
            command, formatter_class=FormatterClass, help=title, description=doc
        )
        p.set_defaults(func=func)
        return p

    p = subp("run", Application.cli_run, doc_run)
    p.add_argument("julia", default="julia", nargs="?")
    p.add_argument("arguments", nargs="*")

    p = subp("init", Application.cli_init, doc_init)
    p.add_argument("julia", default="julia", nargs="?")
    p.add_argument("--sysimage", "-J")

    return parser


def main(args=None):
    parser = make_parser()
    ns = parser.parse_args(args)
    kwargs = vars(ns)
    func = kwargs.pop("func")
    enable_pdb = kwargs.pop("pdb")
    app, kwargs = Application.consume(**kwargs)

    if enable_pdb:
        import pdb

    try:
        return func(app, **kwargs)
    except Exception:
        if enable_pdb:
            pdb.post_mortem()
        raise
    except (KnownError, subprocess.CalledProcessError) as err:
        print(err, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
