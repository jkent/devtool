# -*- utf-8 -*-
# vim: set ts=4 et

import os

import devtool


profiles_dir = os.path.join(devtool.root_dir, 'profiles')
default_profiles = []
profiles = []

def rescan():
    global default_profiles
    global profiles

    for f in os.listdir(profiles_dir):
        if not os.path.isfile(os.path.join(profiles_dir, f)):
            continue

        if f.endswith('_default'):
            default_profiles.append(f.rstrip('_default'))
            continue

        if f.endswith('.old'):
            continue

        profiles.append(f)

    default_profiles.sort()
    profiles.sort()

rescan()

