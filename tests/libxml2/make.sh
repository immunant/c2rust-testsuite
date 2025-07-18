#!/bin/bash
set -e; set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0" )" && pwd)"
make -C "$SCRIPT_DIR/repo" clean && rm -f compile_commands.json
intercept-build make -C "$SCRIPT_DIR/repo" -j`nproc` runtest 2>&1 \
    | tee `basename "$0"`.log
