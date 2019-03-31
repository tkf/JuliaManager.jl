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

doc_julia = """
The name of Julia executable on `$PATH` or a path to the Julia
executable.
"""

doc_sysimage = """
The path to system image.
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

    def subp(command, func, doc=None):
        doc = doc or func.__doc__
        title = None
        for title in filter(None, map(str.strip, (doc or "").splitlines())):
            break
        p = subparsers.add_parser(
            command, formatter_class=FormatterClass, help=title, description=doc
        )
        p.set_defaults(func=func)
        return p

    p = subp("run", Application.cli_run, doc_run)
    p.add_argument("julia", default="julia", nargs="?", help=doc_julia)
    p.add_argument("arguments", nargs="*")

    p = subp("init", Application.cli_init, doc_init)
    p.add_argument("julia", default="julia", nargs="?", help=doc_julia)
    p.add_argument("--sysimage", "-J", help=doc_sysimage)

    p = subp("set-default", Application.cli_set_default)
    p.add_argument("julia", default="julia", help=doc_julia)

    p = subp("set-sysimage", Application.cli_set_sysimage)
    p.add_argument("julia", default="julia", nargs="?", help=doc_julia)
    p.add_argument("sysimage", help=doc_sysimage)

    p = subp("unset-sysimage", Application.cli_unset_sysimage)
    p.add_argument("julia", default="julia", nargs="?", help=doc_julia)

    p = subp("create-default-sysimage", Application.cli_create_default_sysimage)
    p.add_argument("julia", default="julia", nargs="?", help=doc_julia)
    p.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="""
        Re-compile default system image for `julia` even if it already
        exists.
        """,
    )

    locate_parser = subparsers.add_parser(
        "locate",
        formatter_class=FormatterClass,
        help="Show paths to related files and directories",
    )
    subparsers = locate_parser.add_subparsers()

    p = subp("sysimage", Application.cli_locate_sysimage)
    p.add_argument("julia", default="julia", nargs="?", help=doc_julia)

    p = subp("base", Application.cli_locate_base)
    p = subp("dir", Application.cli_locate_local_dir)
    p = subp("home-dir", Application.cli_locate_home_dir)

    return parser


def preparse_run(args):
    try:
        stop = args.index("--")
    except ValueError:
        stop = len(args)
    try:
        irun = args.index("run", 0, stop) + 1
    except ValueError:
        return args, None

    # Parse whatever after `run` _unless_ it looks like an option.
    if irun < len(args) and not args[irun].startswith("-"):
        irun += 1
    if irun < len(args) and args[irun] == "--":
        irun += 1

    return args[:irun], args[irun:]


def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]
    pre_args, julia_arguments = preparse_run(args)
    parser = make_parser()
    ns = parser.parse_args(pre_args)
    if julia_arguments:
        assert not ns.arguments
        ns.arguments = julia_arguments
    if not hasattr(ns, "func"):
        parser.error("please specify a subcommand or --help")
    return ns


def main(args=None):
    kwargs = vars(parse_args())
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
