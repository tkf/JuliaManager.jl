#!/bin/bash

JULIA="julia --color=yes"
PATH="$HOME/.julia/bin:$PATH"

set -ex

$JULIA -e "using JuliaManager; JuliaManager.install_cli()"
which jlm
jlm --help
time jlm create-default-sysimage

cd jlm
tox
