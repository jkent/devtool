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
        if os.path.isfile(os.path.join(path, 'project.dt')):
            project_dir = path

    if not project_dir:
        return None

    return os.path.relpath(project_dir)


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

            if keyword != 'depends on':
                break

            deps.append('(%s)' % args)
    
    return ' && '.join(deps)


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


def build_autogen(project, profile, profile_dict):
    autogen = 'config PROFILE_%s\n' % profile.upper()
    autogen += '\tbool\n'
    autogen += '\tdefault y\n'

    for key, value in profile_dict.items():
        if value == None:
            continue

        autogen += 'config %s\n' % key
        if type(value) is bool:
            autogen += '\tbool\n'
            if value:
                autogen += '\tdefault y\n'
            else:
                autogen += '\tdefault n\n'
        elif type(value) is int:
            autogen += '\tbool\n'
            autogen += '\tdefault %s\n' % str(value)
        else:
            autogen += '\tstring\n'
            autogen += '\tdefault "%s"\n' % value

    f, filename = mkstemp()
    f = os.fdopen(f, 'w')
    f.write(autogen)
    f.close()

    return filename


def edit_config(profile, path=None):
    project_dir = find(path)
    if not project_dir:
        print "no project found"
        sys.exit(1)

    if profile not in profiles:
        print "no profile '%s'" % profile
        sys.exit(1)

    profile_dict = {}
    if not check(profile, project_dir, profile_dict):
        sys.exit(1)

    autogen = build_autogen(project_dir, profile, profile_dict)
    env = dict(os.environ)
    env['_DT_PROJECT'] = os.path.abspath(project_dir)
    env['_DT_PROFILE'] = profile
    env['_DT_AUTOGEN'] = autogen
    options = os.path.join(devtool.root_dir, 'options', 'project.dt')
    config_dir = os.path.join(project_dir, 'build')
    config = os.path.join(config_dir, '%s.cfg' % profile)
    if kconfig.edit(options, config, env):
        update(profile, project_dir, autogen)
    os.remove(autogen)


def check(profile, project_dir, profile_dict={}):
    deps_expr = get_deps(project_dir)
    check_deps = parse_deps(deps_expr, profile_dict)
    profile_file = os.path.join(profiles_dir, profile)
    kconfig.get_values(profile_file, profile_dict)
    if not check_deps():
        sys.stderr.write("profile does not meet project dependencies:\n")
        sys.stderr.write("%s\n" % deps_expr)
        return False
    return True


def update(profile, project_dir, autogen=None):
    make_autogen = autogen == None
    if make_autogen:
        profile_dict = {}
        profile_file = os.path.join(profiles_dir, profile)
        kconfig.get_values(profile_file, profile_dict)
        autogen = build_autogen(project_dir, profile, profile_dict)
    env = dict(os.environ)
    env['_DT_PROJECT'] = os.path.abspath(project_dir)
    env['_DT_AUTOGEN'] = autogen
    options = os.path.join(devtool.root_dir, 'options', 'project.dt')
    config_dir = os.path.join(project_dir, 'build')
    config = os.path.join(config_dir, '%s.cfg' % profile)
    include_dir = os.path.join(config_dir, profile)
    if not os.path.exists(include_dir):
        os.makedirs(include_dir)
    env['KCONFIG_AUTOHEADER'] = os.path.join(include_dir, 'config.h')
    env['KCONFIG_AUTOCONFIG'] = os.path.join(include_dir, 'auto.mk')
    kconfig.conf(options, config, env)
    if make_autogen:
        os.remove(autogen)

    return True    

