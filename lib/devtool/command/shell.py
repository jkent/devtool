# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys

from devtool.process import run
from devtool.profile import profiles_dir, profiles


def main():
    if len(sys.argv) != 2:
        usage(True)

    if os.environ.get('_DT_SHELL', None):
        print "already in a shell"
        sys.exit(1)
 
    profile = sys.argv[1]
    if profile not in profiles:
        print "no profile '%s'" % profile
        sys.exit(1)

    profile_file = os.path.join(profiles_dir, profile)
    env = dict(os.environ)
    env['_DT_PROFILE'] = profile
    env['_DT_SHELL'] = "1"
    env['PS1'] = "\u@\h:\w [dt:${_DT_PROFILE}]\$ "
    run(os.environ['SHELL'], '--norc', env=env)


def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt shell <profile>"""

    print dedent(usage)

    if exit:
        sys.exit(64)

