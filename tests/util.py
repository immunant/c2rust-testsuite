import os
import sys
import yaml
import errno
import subprocess

from typing import List

CONF_YML: str = "conf.yml"


class Config(object):
    def __init__(self, args):
        self.verbose = args.verbose
        self.project = args.project  # project filter
        self.stage = args.stage      # stage filter
        self.project_dirs = find_project_dirs(self)


class Colors(object):
    # Terminal escape codes
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    NO_COLOR = '\033[0m'


def die(emsg: str, status: int=errno.EINVAL):
    (red, nc) = (Colors.FAIL, Colors.NO_COLOR)
    print(f"{red}error:{nc} {emsg}", file=sys.stderr)
    exit(status)


def warn(wmsg: str):
    (yellow, nc) = (Colors.WARNING, Colors.NO_COLOR)
    print(f"{yellow}warning:{nc} {wmsg}", file=sys.stderr)


def info(imsg: str):
    (blue, nc) = (Colors.OKBLUE, Colors.NO_COLOR)
    print(f"{blue}info:{nc} {imsg}", file=sys.stdout)


def is_dir_empty(dirp: str):
    return len(os.listdir(dirp)) == 0


def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))


def find_project_dirs(conf: Config) -> List[str]:
    script_dir = get_script_dir()
    subdirs = sorted(next(os.walk(script_dir))[1])

    # filter out __pycache__ and anything else starting with `_`
    subdirs = filter(lambda d: not(d.startswith("_") or d.startswith(".")),
                     subdirs)

    if conf.project:  # only test named project
        project = filter(lambda d: d == conf.project, subdirs)
        if not project:
            nl = ", ".join(map(lambda p: os.path.basename(p), test_dirs))
            y, nc = Colors.WARNING, Colors.NO_COLOR
            msg = f"no such project: {y}{conf.project}{nc}. projects: {nl}."
            die(msg)
        subdirs = project

    return [os.path.join(script_dir, s) for s in subdirs]


def get_yaml(file: str) -> dict:
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            die(str(exc))