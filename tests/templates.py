import os
import stat

from typing import Dict, List
from tests.util import *
from jinja2 import Template

TRANSPILE_SH: str = r"""#!/usr/bin/env bash
# this file was autogenerated by templates.py
set -e; set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0" )" && pwd)"

RUST_BACKTRACE=1 c2rust transpile \
    --output-dir "$SCRIPT_DIR/repo" {{binary}} \
    {{tflags}} ${EXTRA_TFLAGS:---overwrite-existing} \
    compile_commands.json \
    -- {{cflags}} ${EXTRA_CFLAGS:--w} \
     2>&1 | tee `basename "$0"`.log

if [[ -f "$SCRIPT_DIR/build.rs" ]]; then
    cp "$SCRIPT_DIR/build.rs" "$SCRIPT_DIR/repo"
fi

if [[ -n "$C2RUST_DIR" ]]; then
    sed --in-place --regexp-extended "s|c2rust-bitfields = \"([0-9.]+)\"|c2rust-bitfields = { version = \"\1\", path = \"$C2RUST_DIR/c2rust-bitfields\" }|" "$SCRIPT_DIR/repo/Cargo.toml"
fi
"""

CARGO_SH: str = r"""#!/usr/bin/env bash
# this file was autogenerated by templates.py
set -e; set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0" )" && pwd)"

(cd "$SCRIPT_DIR/repo" \
    && cargo ${TOOLCHAIN} build 2>&1 | tee ../`basename "$0"`.log)

"""


def render_script(template: str, out_path: str, params: Dict):
    out = Template(template).render(**params)

    with open(out_path, 'w') as fh:
        fh.writelines(out)
    os.chmod(out_path, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)


def autogen_cargo(conf_file, yaml: Dict):
    cargo = yaml.get("cargo")
    if cargo and isinstance(cargo, Dict):
        ag = cargo.get("autogen")
        if ag and isinstance(ag, bool):
            params = {}

            out_path = os.path.join(
                os.path.dirname(conf_file),
                "cargo.gen.sh"
            )
            render_script(CARGO_SH, out_path, params)


def autogen_transpile(conf_file, yaml: Dict):
    transpile = yaml.get("transpile")
    if transpile and isinstance(transpile, Dict):
        ag = transpile.get("autogen")
        if ag and isinstance(ag, bool):
            params = {"binary": "--emit-build-files", "cflags": ""}

            binary = transpile.get("binary")
            if binary:
                params["binary"] = f"--binary {binary}"

            cflags = transpile.get("cflags")
            if cflags:
                if isinstance(cflags, List):
                    cflags = " ".join(cflags)
                params["cflags"] = cflags


            out_path = os.path.join(
                os.path.dirname(conf_file),
                "transpile.gen.sh"
            )
            render_script(TRANSPILE_SH, out_path, params)


def autogen(conf: Config):
    for (cf, yaml) in conf.project_conf.items():
        autogen_transpile(cf, yaml)
        autogen_cargo(cf, yaml)
