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


def conf(options, config, env=None):
    if env == None:
        env = dict(os.environ)
    env['KCONFIG_CONFIG'] = config
    executable = os.path.join(devtool.bin_dir, 'kconfig-conf')
    run(executable, '--silentoldconfig', options, env=env)


def edit(options, config, env=None):
    check()
    if env == None:
        env = dict(os.environ)

    config_dir = os.path.dirname(os.path.abspath(config))
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    mtime = 0
    if os.path.exists(config):
        mtime = os.path.getmtime(config)
    env['KCONFIG_CONFIG'] = config
    executable = os.path.join(devtool.bin_dir, 'kconfig-mconf')
    run(executable, options, env=env)
    if os.path.exists(config):
        mtime = os.path.getmtime(config) - mtime

    if mtime:
        return True

    return False


def value(config, option):
    with open(config, 'r') as f:
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


def choice(config, option):
    with open(config, 'r') as f:
        for line in f.readlines():
            m = re.match(r'^CONFIG_%s_(.*)=y$' % option, line)
            if m:
                return m.group(1)
    return None


def get_values(config, values):
    values.clear()
    with open(config, 'r') as f:
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

