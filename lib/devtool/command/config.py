# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys

import devtool
import devtool.project as project


def main():
    if len(sys.argv) > 2:
        usage(True)

    path = sys.argv[1] if len(sys.argv) == 2 else None
    project.edit_config(path)

def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt config [<project>]"""

    print dedent(usage)

    if exit:
        sys.exit(64)

