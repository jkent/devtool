# -*- utf-8 -*-
# vim: set ts=4 et

import os
import re
import sys
from tempfile import mkstemp

import kconfig
import devtool
from profile import profiles_dir, profiles
from util import walk_up
import toolchain


def find(path=None):
    project_dir = None
    if path == None:
        for path in walk_up(os.getcwd()):
            if os.path.isfile(os.path.join(path, 'project.dt')):
                project_dir = path
    else:
        path = os.path.abspath(path)
        if os.path.isfile(os.path.join(path, 'project.dt')):
            project_dir = path

    if project_dir:
        os.environ['_DT_PROJECT'] = project_dir

    return project_dir

def get_deps(project_dir):
    deps = []

    in_section = False
    with open(os.path.join(project_dir, 'project.dt')) as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue

            parts = re.split('(?!\s+on)\s+', line, 1)
            keyword = parts[0]
            if keyword.startswith('#'):
                continue

            args = parts[1] if len(parts) > 1 else ''

            if keyword == 'config' and args == 'PROJECT':
                in_section = True
                continue

            if not in_section:
                continue

            if keyword == 'config':
                break

            if keyword != 'depends on':
                print 'unexpected keyword in PROJECT config section'
                sys.exit(1)

            deps.append('(%s)' % args)
    
    return '&&'.join(deps)

# Shunting-yard algorithm
def parse_deps(expr, values):
    tokens = re.split("(\(|\)|\|\||&&|==?|!=|!)", expr)
    tokens = filter(None, map(str.strip, tokens))

    output = []
    stack = []
    paren = 0

    operators = {
        '||': (1, lambda a,b: lambda: a() or b()),
        '&&': (2, lambda a,b: lambda: a() and b()),
        '!' : (3, lambda a:   lambda: not a()),
        '!=': (4, lambda a,b: lambda: a() != b()),
        '=' : (5, lambda a,b: lambda: a() == b()),
    }

    def operator(s):
        f = operators[s][1]
        l = []
        for i in xrange(f.func_code.co_argcount):
            l.append(output.pop())
        return apply(f, l)

    def operand(s):
        if s[0] == '"' and s[-1] == '"':
            s = s[1:-1]
            return lambda: s
        elif s.isdigit():
            return lambda: int(s)
        elif re.match(r'^[a-z_][a-z0-9_]*$', s, re.I):
            if s == 'y':
                return lambda: True
            elif s == 'n':
                return lambda: False
            else:
                return lambda: values.get(s, False)
        else:
            print "invalid token"
            sys.exit(1)

    for item in tokens:
        if not item:
            continue
        if item in operators:
            while stack and stack[-1] != '(':
                if item in ['!']: # left-associative
                    if operators[stack[-1]][0] <= operators[item][0]:
                        break
                else:
                    if operators[stack[-1]][0] < operators[item][0]:
                        break
                output.append(operator(stack.pop()))
            stack.append(item)
        elif item == '(':
            paren += 1
            stack.append(item)
        elif item == ')':
            paren -= 1
            while stack and stack[-1] != '(':
                output.append(operator(stack.pop()))
            if not stack or stack[-1] != '(':
                print "unmatched parentheses"
                sys.exit(1)
            stack.pop()
        else:
            output.append(operand(item))

    while stack:
        output.append(operator(stack.pop()))

    if paren != 0:
        print "unmatched parentheses"
        sys.exit(1)        

    return output[0]

def build_autogen(project_dir):
    values = {}
    
    deps = get_deps(project_dir)
    if deps:
        check_deps = parse_deps(deps, values)

    profile_choice  = 'choice\n'
    profile_choice += '\tprompt "Profile"\n'
    presets = ''

    if not profiles:
        print "no profiles configured"
        sys.exit(1)

    for profile in profiles:
        profile_file = os.path.join(profiles_dir, profile)

        kconfig.get_values(profile_file, values)
        if deps and not check_deps():
            continue

        profile_choice += 'config PROFILE_%s\n' % profile
        profile_choice += '\tbool "%s"\n' % profile

        presets += 'if PROFILE_%s\n' % profile
        for key in values:
            value = values[key]
            if value != None:
                presets += 'config %s\n' % key
                if type(value) is bool:
                    presets += '\tbool\n'
                    if value:
                        presets += '\tdefault y\n'
                    else:
                        presets += '\tdefault n\n'
                elif type(value) is int:
                    presets += '\tbool\n'
                    presets += '\tdefault %s\n' % str(value)
                else:
                    presets += '\tstring\n'
                    presets += '\tdefault "%s"\n' % value
        presets += 'endif\n'

    profile_choice += 'endchoice\n'

    if not presets:
        return None

    f, filename = mkstemp()
    f = os.fdopen(f, 'w')
    f.write(profile_choice)
    f.write(presets)
    f.close()

    return filename

def edit_config(path=None):
    project_dir = find(path)
    if not project_dir:
        print "no project found"
        sys.exit(1)

    autogen = build_autogen(project_dir)
    if not autogen:
        print "no profiles that meet project dependencies"
        sys.exit(1)

    os.environ['_DT_AUTOGEN'] = autogen
    options = os.path.join(devtool.root_dir, 'options', 'project.dt')
    settings = os.path.join(project_dir, '.config')
    kconfig.edit(options, settings)
    os.remove(autogen)

