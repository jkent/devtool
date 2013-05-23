# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys

from devtool.process import run
from devtool.profile import profiles_dir, profiles


def main():
    if len(sys.argv) > 2:
        usage(True)

    profile = os.environ.get('_DT_PROFILE', None)
    if len(sys.argv) > 1:
        profile = sys.argv[1]

    if not profile:
        usage(True)

    if profile not in profiles:
        print "no profile '%s'" % profile
        sys.exit(1)

    env = dict(os.environ)
    env['_DT_PROFILE'] = profile
    run('make', env=env)


def usage(exit=False):
    from textwrap import dedent

    profile = os.environ.get('_DT_PROFILE', None)
    if profile:
        usage = """\
            usage: dt build [<profile>]"""
    else:
        usage = """\
            usage: dt build <profile>"""

    print dedent(usage)

    if exit:
        sys.exit(64)

