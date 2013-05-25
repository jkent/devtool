# -*- utf-8 -*-
# vim: set ts=4 et

from glob import glob
import os
from shutil import copyfile
import sys

import devtool
import devtool.kconfig as kconfig
from devtool.profile import profiles, profiles_dir
import devtool.profile as profile


def main():
    if len(sys.argv) <= 1:
        usage(True)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd in ['cp', 'copy']:
        cmd_copy(args)
    elif cmd in ['del', 'delete', 'rm']:
        cmd_delete(args)
    elif cmd == 'edit':
        cmd_edit(args)
    elif cmd == 'list':
        cmd_list(args)
    elif cmd == 'new':
        cmd_new(args)
    else:
        usage(True)


def cmd_copy(args):
    if len(args) != 2:
        usage(True)

    src, dst = args
    profile.copy(src, dst)
    profile.edit(dst)


def cmd_delete(args):
    if len(args) != 1:
        usage(True)

    name, = args
    profile.delete(name)


def cmd_edit(args):
    if len(args) != 1:
        usage(True)

    name, = args
    profile.edit(name)


def cmd_list(args):
    if len(args) != 0:
        usage(True)

    for name in profiles:
        print name


def cmd_new(args):
    if len(args) != 1:
        usage(True)

    name, = args
    profile.new(name)
    profile.edit(name)


def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt profile list
           or: dt profile new <profile>
           or: dt profile del <profile>
           or: dt profile edit <profile>
           or: dt profile copy <src_profile> <dst_profile>"""

    print dedent(usage)

    if exit:
        sys.exit(64)

