#!/bin/sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0" )" && pwd)"

ulimit -s 16384 # debug build requires this much stack to pass tests
cd $SCRIPT_DIR/repo/testes && \
    cargo run -- -e_U=true all.lua \
    | tee `basename "$0"`.log
