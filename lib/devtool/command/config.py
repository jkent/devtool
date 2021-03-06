# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys

import devtool.project as project


def main():
    if len(sys.argv) > 2:
        usage(True)

    profile = os.environ.get('_DT_PROFILE', None)
    if len(sys.argv) > 1:
        profile = sys.argv[1]

    if not profile:
        usage(True)

    project.edit_config(profile)

def usage(exit=False):
    from textwrap import dedent

    profile = os.environ.get('_DT_PROFILE', None)
    if profile:
        usage = """\
            usage: dt config [<profile>]"""
    else:
        usage = """\
            usage: dt config <profile>"""

    print dedent(usage)

    if exit:
        sys.exit(64)

