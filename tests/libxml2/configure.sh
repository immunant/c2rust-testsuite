#!/bin/bash
set -e; set -o pipefail

# libxml2 uses a weird aliasing hack to optimize internal calls to 
# exported functions when building shared libraries. Blocked on Rust
# support for aliases with different linkage.
(cd repo && ./autogen.sh --enable-shared=no --enable-static=yes 2>&1 \
     | tee ../`basename "$0"`.log)

#(cd repo && ./autogen.sh --enable-shared=yes --enable-static=no 2>&1 \
#     | tee ../`basename "$0"`.log)     
