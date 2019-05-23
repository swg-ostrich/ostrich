# swg-main
Forked from https://github.com/SWG-Source/swg-main

## Initial Setup
 1. `cd ostrich`
 2. `git submodule update --init --recursive`
 3. `git submodule foreach -q --recursive 'git checkout $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master)'`
