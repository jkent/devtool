# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys

import devtool
import devtool.project as project
import devtool.toolchain as toolchain
from devtool.process import run


def main():
    if len(sys.argv) > 2:
        usage(True)

    path = sys.argv[1] if len(sys.argv) == 2 else None
    project_dir = project.find(path)

    if not project_dir:
        print "could not find project"
        sys.exit(1)

    config_file = os.path.join(project_dir, '.config')

    if not os.path.isfile(config_file):
        print "project is not configured"
        sys.exit(1)

    toolchain.setup(config_file)
    os.environ['PS1'] = "\u@\h:\w [dt]\$ "
    run(os.environ['SHELL'], '--norc')

def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt shell [<project>]"""

    print dedent(usage)

    if exit:
        sys.exit(64)

