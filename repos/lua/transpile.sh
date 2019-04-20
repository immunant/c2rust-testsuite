#!/bin/sh

set -e

c2rust transpile \
    --overwrite-existing \
    --output-dir repo \
    -m lua compile_commands.json \
    | tee `basename "$0"`.log

SCRIPT_DIR="$(cd "$(dirname "$0" )" && pwd)"
cp $SCRIPT_DIR/build.rs $SCRIPT_DIR/repo