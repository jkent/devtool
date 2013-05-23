# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys

import devtool.project as project
import devtool.toolchain as toolchain
from devtool.process import run
from devtool.profile import profiles_dir, profiles


def main():
    if len(sys.argv) != 2:
        usage(True)

    profile = os.environ.get('_DT_PROFILE', None)
    if not profile:
        sys.stderr.write("_DT_PROFILE not set\n")
        sys.exit(1)

    if profile not in profiles:
        print "export _DT_PROFILE :="
        sys.stderr.write("no profile '%s'\n" % profile)
        sys.exit(1)

    project_dir = project.find(sys.argv[1])
    if not project_dir:
        print "export _DT_PROFILE :="
        sys.stderr.write("project not found\n")
        sys.exit(1)

    config_file = os.path.join(project_dir, 'build', '%s.cfg' % profile)
    if not os.path.exists(config_file):
        print "export _DT_PROFILE :="
        sys.stderr.write("project not configured\n")
        sys.exit(1)

    profile_file = os.path.join(profiles_dir, profile)

    if os.path.getmtime(config_file) < os.path.getmtime(profile_file):
        if not project.check(profile, project_dir):
            print "export _DT_PROFILE :="
            sys.exit(1)
        project.update(profile, project_dir)

    env = {}
    env['_DT_PROFILE'] = profile
    toolchain.setup(profile_file, env)
    for key,value in env.items():
        print "export %s := %s" % (key, value)


def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt _prepmk <project>"""

    print dedent(usage)

    if exit:
        sys.exit(64)

