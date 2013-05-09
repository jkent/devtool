# -*- utf-8 -*-
# vim: set ts=4 et

import sys

import devtool
import devtool.command as command


def main():
    if len(sys.argv) == 1:
        devtool.usage()
        sys.exit(0)
    elif len(sys.argv) > 2:
        usage(True)

    module = command.use(sys.argv[1])
    if not module:
        print "'%s' is not a command" % sys.argv[1]
        sys.exit(64)

    try:
        module.usage()
    except:
        print "'%s' does not have any help" % sys.argv[1]

def usage(exit=False):
    from textwrap import dedent

    usage = """\
        usage: dt help [command]"""

    print dedent(usage)

    if exit:
        sys.exit(64)

