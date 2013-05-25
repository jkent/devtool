# -*- utf-8 -*-
# vim: set ts=4 et

import os
from shutil import copyfile

import devtool
import devtool.kconfig as kconfig


profiles_dir = os.path.join(devtool.root_dir, 'profiles')
profiles = []


def rescan():
    global profiles

    for f in os.listdir(profiles_dir):
        if not os.path.isfile(os.path.join(profiles_dir, f)):
            continue

        if f.endswith('.old'):
            continue

        profiles.append(f)

    profiles.sort()

rescan()


def edit(name):
    if name not in profiles:
        sys.stderr.write("no profile '%s'" % name)
        sys.exit(1)

    options = os.path.join(devtool.root_dir, 'options', 'profile.dt')
    profile = os.path.join(profiles_dir, name)
    kconfig.edit(options, profile)


def new(name):
    if name in profiles:
        sys.stderr.write("already a profile '%s'" % name)
        sys.exit(1)

    profile = os.path.join(profiles_dir, name)
    open(profile, 'w').close()
    rescan()
    

def copy(src, dst):
    if src not in profiles:
        sys.stderr.write("no profile '%s'" % src)
        sys.exit(1)

    src_profile = os.path.join(profiles_dir, src)
    dst_profile = os.path.join(profiles_dir, dst)
    copyfile(src_profile, dst_profile)
    rescan()


def delete(name):
    if name not in profiles:
        sys.stderr.write("no profile '%s'" % name)
        sys.exit(1)

    profile = os.path.join(profiles_dir, name)
    os.remove(profile)
    rescan()

