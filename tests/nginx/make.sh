#!/bin/bash
set -e; set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0" )" && pwd)"
rm -f compile_commands.json
intercept-build make -C "$SCRIPT_DIR/repo" -j`nproc` \
    MYCFLAGS="-std=c99" \
    | tee `basename "$0"`.log
