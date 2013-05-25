# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys
from shutil import copyfile

import devtool
import devtool.kconfig as kconfig


profiles_dir = os.path.join(devtool.root_dir, 'profiles')
profiles = []


def valid_name(name):
    if name.startswith('.'):
        return False

    if name.endswith('.old'):
        return False

    return True


def rescan():
    global profiles

    for name in os.listdir(profiles_dir):
        if not os.path.isfile(os.path.join(profiles_dir, name)):
            continue

        if not valid_name(name):
            continue

        profiles.append(name)

    profiles.sort()

rescan()


def edit(name):
    if not valid_name(name):
        sys.stderr.write("'%s' is not a valid profile name\n" % name)
        sys.exit(1)

    if name not in profiles:
        sys.stderr.write("no profile '%s'\n" % name)
        sys.exit(1)

    options = os.path.join(devtool.root_dir, 'options', 'profile.dt')
    profile = os.path.join(profiles_dir, name)
    kconfig.edit(options, profile)


def new(name):
    if not valid_name(name):
        sys.stderr.write("'%s' is not a valid profile name\n" % name)
        sys.exit(1)

    if name in profiles:
        sys.stderr.write("already a profile '%s'\n" % name)
        sys.exit(1)

    profile = os.path.join(profiles_dir, name)
    open(profile, 'w').close()
    rescan()
    

def copy(src, dst):
    if not valid_name(src):
        sys.stderr.write("'%s' is not a valid profile name\n" % src)
        sys.exit(1)

    if not valid_name(dst):
        sys.stderr.write("'%s' is not a valid profile name\n" % dst)
        sys.exit(1)

    if src not in profiles:
        sys.stderr.write("no profile '%s'\n" % src)
        sys.exit(1)

    src_profile = os.path.join(profiles_dir, src)
    dst_profile = os.path.join(profiles_dir, dst)
    copyfile(src_profile, dst_profile)
    rescan()


def delete(name):
    if not valid_name(name):
        sys.stderr.write("'%s' is not a valid profile name\n" % name)
        sys.exit(1)

    if name not in profiles:
        sys.stderr.write("no profile '%s'\n" % name)
        sys.exit(1)

    profile = os.path.join(profiles_dir, name)
    os.remove(profile)
    rescan()

