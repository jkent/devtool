# -*- utf-8 -*-
# vim: set ts=4 et

import os
import re

import devtool
from devtool.process import run, run_background
from devtool.task import task

config_dir = os.path.join(devtool.root_dir, 'configs')

def check():
    mconf = os.path.join(devtool.bin_dir, 'kconfig-mconf')
    if not os.path.exists(mconf):
        setup()

@task('Setting up kconfig')
def setup():
    src_dir = os.path.join(devtool.root_dir, 'build-tools', 'kconfig')

    @task('Building')
    def build():
        rv = run_background('make', 'clean', cwd=src_dir)
        if rv:
            raise Exception, 'clean failed'

        rv = run_background('make', cwd=src_dir)
        if rv:
            raise Exception, 'build failed'

    @task('Installing')
    def install():
        rv = run_background('make', 'install', cwd=src_dir)
        if rv:
            raise Exception, 'install failed'

    build()
    install()

def edit(options, settings):
    check()
    env = dict(os.environ)
    env['KCONFIG_CONFIG'] = settings
    run('%s/kconfig-mconf' % devtool.bin_dir, options, env=env)

def value(settings, option):
    with open(settings, 'r') as f:
        for line in f.readlines():
            if line.startswith('# CONFIG_%s is not set' % option):
                return False
            m = re.match(r'^CONFIG_%s=(.*)$' % option, line)
            if m:
                value = m.group(1)
                if value == 'y':
                    return True
                return value
    return None

def choice(settings, option):
    with open(settings, 'r') as f:
        for line in f.readlines():
            m = re.match(r'^CONFIG_%s_(.*)=y$' % option, line)
            if m:
                return m.group(1)
    return None

def get_values(settings, values):
    values.clear()
    with open(settings, 'r') as f:
        for line in f.readlines():
            m = re.match(r'^CONFIG_(.+)="?(.*?)"?$', line)
            if m:
                value = m.group(2)
                if value.isdigit():
                    value = int(value)
                elif value == 'y':
                    value = True
                elif value == 'n':
                    value = False
                values[m.group(1)] = value

def update_project(options, settings):
    if not os.environ.get('_DT_PROJECT', None):
        return
    check()
    env = dict(os.environ)
    env['KCONFIG_CONFIG'] = settings
    include = os.path.join(env['_DT_PROJECT'], 'include')
    env['KCONFIG_AUTOHEADER'] = os.path.join(include, 'config.h')
    env['KCONFIG_AUTOCONFIG'] = os.path.join(include, 'auto.conf')
    executable = os.path.join(devtool.bin_dir, 'kconfig-conf')
    run(executable, '--silentoldconfig', options, env=env)

