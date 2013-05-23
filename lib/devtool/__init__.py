# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys

import command

debug = False

root_dir = ''
bin_dir = ''


def main(rootdir):
    global root_dir, bin_dir

    root_dir = rootdir
    bin_dir = os.path.join(root_dir, 'bin')
    
    os.environ['_DT'] = root_dir
    os.environ['PATH'] = os.pathsep.join((bin_dir, os.environ['PATH']))

    if len(sys.argv) < 2:
        usage(True)

    module = command.use(sys.argv[1])
    if not module:
        usage(True)

    del sys.argv[0]
    module.main()


def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt <command> [<args>]

        command list:%s

        See 'dt help <command>' for more information on a specific command."""
   
    commands = (s for s in command.modules if not s.startswith('_'))
    command_list = ''.join('\n           %s' % s for s in commands)
    print dedent(usage % command_list)

    if exit:
        sys.exit(64)

