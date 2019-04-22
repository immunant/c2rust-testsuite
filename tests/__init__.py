
import os
import sys
import subprocess
from typing import List  # , Set, Dict, Tuple, Optional

from tests.util import *
from tests.requirements import *

REQUIREMENTS_YML: str = "requirements.yml"


class Config(object):
    # Terminal escape codes
    verbose = False
    project = None

    def update(self, args):
        self.verbose = args.verbose
        self.project = args.project


class Test(object):

    STAGES: dict = {
        "autogen": ["autogen.sh"],
        "configure": ["configure.sh"],
        "make": ["make.sh", "cmake.sh"],
        "transpile": ["transpile.sh"],
        "cargo": ["cargo.sh"],
        "check": ["check.sh", "test.sh"]
    }

    def __init__(self, conf: Config, directory: str):
        ff = next(os.walk(directory))[2]
        self.scripts = set(filter(lambda f: f.endswith(".sh"), ff))
        self.dir = directory
        self.name = os.path.basename(directory)
        self.conf = conf

    def run_script(self, stage, script, xfail=False) -> bool:
        """
        Returns true iff subsequent tests should run
        """
        prev_dir = os.getcwd()
        script_path = os.path.join(self.dir, script)
        if not self.conf.verbose:
            relpath = os.path.relpath(script_path, prev_dir)
            line = "{blue}{name}{nc}: {stage}({script})".format(
                blue=Colors.OKBLUE,
                name=self.name,
                nc=Colors.NO_COLOR,
                stage=stage,
                script=relpath)
            print(line, end="", flush=True)

        # noinspection PyBroadException
        try:
            os.chdir(self.dir)
            if self.conf.verbose:
                subprocess.check_call(args=[script_path])
            else:
                subprocess.check_call(
                    args=[script_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)

                print("{fill} {color}OK{nocolor}".format(
                    fill=(75 - len(line)) * ".",
                    color=Colors.OKGREEN,
                    nocolor=Colors.NO_COLOR)
                )
                return True
        except KeyboardInterrupt as ki:
            if not self.conf.verbose:
                print(": {color}INTERRUPT{nocolor}".format(
                    color=Colors.WARNING,
                    nocolor=Colors.NO_COLOR)
                )
                exit(1)
        except:  # noqa
            if not self.conf.verbose:
                outcome = "XFAIL" if xfail else "FAIL"
                print("{fill} {color}{outcome}{nocolor}".format(
                    fill=(75 - len(line)) * ".",
                    color=Colors.OKBLUE if xfail else Colors.FAIL,
                    outcome=outcome,
                    nocolor=Colors.NO_COLOR)
                )
            if not xfail:
                exit(1)
            else:
                return False
        finally:
            os.chdir(prev_dir)

    def is_xfail(self, script) -> bool:
        script_path = os.path.join(self.dir, script)
        if os.path.isfile(f"{script_path}.xfail"):
            return True
        script_path_noext = os.path.splitext(script_path)[0]
        return os.path.isfile(f"{script_path_noext}.xfail")

    def __call__(self):
        # make sure the `repo` directory exists and is not empty
        repo_dir = os.path.join(self.dir, "repo")
        if not os.path.isdir(repo_dir):
            die(f"missing directory: {repo_dir}")
        elif is_dir_empty(repo_dir):
            msg = f"submodule not checked out: {repo_dir}\n"
            msg += "(try running `git submodule update --init`)"
            die(msg)

        for (stage, scripts) in Test.STAGES.items():
            for script in scripts:
                if script in self.scripts:
                    xfail = self.is_xfail(script)
                    cont = self.run_script(stage, script, xfail)
                    if not cont:
                        return  # XFAIL


def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))


def find_test_dirs(_conf: Config) -> List[str]:
    script_dir = get_script_dir()
    subdirs = sorted(next(os.walk(script_dir))[1])

    # filter out __pycache__ and anything else starting with `_`
    subdirs = filter(lambda d: not(d.startswith("_") or d.startswith(".")),
                     subdirs)

    return [os.path.join(script_dir, s) for s in subdirs]


def find_requirements(conf: Config):
    script_dir = get_script_dir()
    subdirs = sorted(next(os.walk(script_dir))[1])

    if conf.project:
        subdirs = filter(lambda s: s == conf.project, subdirs)

    reqs = os.path.join(script_dir, REQUIREMENTS_YML)
    reqs = [reqs] if os.path.exists(reqs) else []

    subreqs = map(lambda d: os.path.join(script_dir, d, REQUIREMENTS_YML),
                  subdirs)
    reqs += filter(lambda f: os.path.exists(f), subreqs)
    return reqs


def run_tests(conf):
    tests = (Test(conf, tdir) for tdir in find_test_dirs(conf))

    if conf.project:  # only test named project
        project = list(filter(lambda t: t.name == conf.project, tests))
        if not project:
            nl = ", ".join(map(lambda p: os.path.basename(p), find_test_dirs(conf)))
            y, nc = Colors.WARNING, Colors.NO_COLOR
            msg = f"no such project: {y}{conf.project}{nc}. project names: {nl}."
            die(msg)
        else:
            tests = project

    for r in find_requirements(conf):
        requirements.check(conf, r)

    for tt in tests:
        tt()
