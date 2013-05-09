# -*- utf-8 -*-
# vim: set ts=4 et

from glob import glob
import os
from shutil import copyfile
import sys

import devtool
import devtool.kconfig as kconfig
from devtool.profile import default_profiles, profiles, profiles_dir

def main():
    if len(sys.argv) <= 1:
        usage(True)

    if sys.argv[1] == 'list':
        do_list()
    elif sys.argv[1] == 'edit':
        do_edit()
    elif sys.argv[1] in ['del', 'delete']:
        do_delete()
    else:
        usage(True)

def do_list():
    if len(sys.argv) > 3:
        usage(True)

    if len(sys.argv) == 3 and (sys.argv[2]
            not in ['-d', 'default', 'defaults']):
        usage(True)

    if len(sys.argv) == 3:
        if not default_profiles:
            print "(no profiles)"
        else:
            for profile in default_profiles:
                print profile
    else:
        if not profiles:
            print "(no profiles)"
        else:            
            for profile in profiles:
                print profile

def do_edit():
    if len(sys.argv) not in [3, 5]:
        usage(True)

    if len(sys.argv) == 5 and sys.argv[2] != '-d':
        usage(True)

    if len(sys.argv) == 5:
        default = os.path.join(profiles_dir, "%s_default" % sys.argv[3])
        profile = os.path.join(profiles_dir, sys.argv[4])

        if profile.endswith('_default'):
            print "not allowed"
            sys.exit(1)

        if not os.path.isfile(default):
            print "no default for '%s'" % sys.argv[3]
            sys.exit(1)
        copyfile(default, profile) 
    else:
        default = os.path.join(profiles_dir, "%s_default" % sys.argv[2])
        profile = os.path.join(profiles_dir, sys.argv[2])
        if profile.endswith('_default'):
            print "not allowed"
            sys.exit(1)

        if not os.path.isfile(profile):
            if not os.path.isfile(default):
                print "no profile '%s'" % sys.argv[2]
                sys.exit(1)
            copyfile(default, profile)

    options = os.path.join(devtool.root_dir, 'options', 'profile.dt')
    kconfig.edit(options, profile)

def do_delete():
    if len(sys.argv) != 3:
        usage(True)

    profile = os.path.join(profiles_dir, sys.argv[2])
    if profile.endswith('_default'):
        print "not allowed"
        sys.exit(1)

    if not os.path.isfile(profile):
        print "no profile '%s'" % sys.argv[2]
        sys.exit(1)

    os.remove(profile)

def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt profile list [default]
           or: dt profile delete <profile>
           or: dt profile edit [-d <profile>] <profile>"""

    print dedent(usage)

    if exit:
        sys.exit(64)

