`jlm`: System image manager for Julia
=====================================

Installation
------------

.. code-block:: jlcon

   (v1.1) pkg> add https://github.com/tkf/JuliaManager.jl
   ...

   julia> using JuliaManager

   julia> JuliaManager.install_cli()
   ...

You need to add `~/.julia/bin` to `$PATH` as would be messaged if it
not.

Examples
--------

.. code-block:: console

   $ cd PATH/TO/YOUR/PROJECT

   $ jlm init
   ...

   $ jlm run
                  _
      _       _ _(_)_     |  Documentation: https://docs.julialang.org
     (_)     | (_) (_)    |
      _ _   _| |_  __ _   |  Type "?" for help, "]?" for Pkg help.
     | | | | | | |/ _` |  |
     | | |_| | | | (_| |  |  Version 1.1.0 (2019-01-21)
    _/ |\__'_|_|_|\__'_|  |  Official https://julialang.org/ release
   |__/                   |

   julia>


Manual
------

.. default-role:: code

.. argparse::
   :module: jlm.cli
   :func: make_parser
   :prog: jlm
