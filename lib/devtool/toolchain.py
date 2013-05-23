# -*- utf-8 -*-
# vim: set ts=4 et

import os
import platform
import sys

import devtool
from devtool.process import run_background
from devtool.task import task
import kconfig
from util import download, check_md5, check_sha1, extract

build_tools_dir = os.path.join(devtool.root_dir, 'build-tools')

toolchains = {
    'LINARO_2013Q1': {
        'name': 'Linaro ARM Embedded 2013q1',
        'arch': 'ARM',
        'prefix': 'arm-none-eabi-',
        'dir': 'gcc-arm-none-eabi-4_7-2013q1',
        'linux': {
            'tarball': 'gcc-arm-none-eabi-4_7-2013q1-20130313-linux.tar.bz2',
            'url': 'https://launchpad.net/gcc-arm-embedded/4.7/4.7-2013-q1-update/+download',
            'md5': 'bcf845e5cd0608a0d56825d8763cba77',
        },
    },
    'CODESOURCERY_201203': {
        'name': 'CodeSourcery ARM EABI 2012.03',
        'arch': 'ARM',
        'prefix': 'arm-none-eabi-',
        'dir': 'arm-2012.03',
        'linux': {
            'tarball': 'arm-2012.03-56-arm-none-eabi-i686-pc-linux-gnu.tar.bz2',
            'url': 'https://sourcery.mentor.com/GNUToolchain/package10385/public/arm-none-eabi',
            'md5': 'f2fcb35a9e09b0f96e058a0176c80444',
        },
    },
}        

def info(settings):
    key = kconfig.choice(settings, 'TOOLCHAIN')
    plat = platform.system().lower()
    toolchain = {}
    if key == 'USER_DEFINED':
        toolchain['name'] = 'Custom toolchain'
        toolchain['prefix'] = kconfig.value('TOOLCHAIN_PREFIX')
        toolchain['dir'] = kconfig.value('TOOLCHAIN_DIRECTORY')
        toolchain['arch'] = toolchain['prefix'].split('-', 1)[0].upper()
        return toolchain
    elif key in toolchains:
        toolchain.update(toolchains[key])
        toolchain.update(toolchains[key][plat])
        return toolchain

def setup(settings, env):
    toolchain = info(settings)
    if not toolchain:
        print "no toolchain selected"
        sys.exit(1)

    toolchain_dir = os.path.join(build_tools_dir, toolchain['dir'])
    toolchain_bin = os.path.join(toolchain_dir, 'bin')
    downloads_dir = os.path.join(devtool.root_dir, 'downloads')

    def installed():
        gcc = os.path.join(toolchain_bin, '%sgcc' % toolchain['prefix'])
        return os.path.isfile(gcc)

    def have_tarball():
        if not toolchain.get('tarball', None):
            return False
        path = os.path.join(downloads_dir, toolchain['tarball'])
        return os.path.isfile(path)

    @task("Setting up %s" % toolchain['name'])
    def install():
        if not toolchain.get('tarball', False):
            print "Please setup your selected toolchain"
            sys.exit(1)

        if not have_tarball():
            if not toolchain.get('url', False):
                print 'Please place "%s" in "%s"' % (toolchain['tarball'],
                        downloads_dir)
                sys.exit(1)
            download("%s/%s" % (toolchain['url'], toolchain['tarball']))

        tarball_path = os.path.join(downloads_dir, toolchain['tarball'])

        if toolchain.get('md5', None):
            check_md5(tarball_path, toolchain['md5'])

        if toolchain.get('sha1', None):
            check_sha1(tarball_path, toolchain['sha1'])

        extract(tarball_path, build_tools_dir)

        if not installed():
            raise Exception('Toolchain installation failed')

    if not installed():
        install()

    env['CROSS_COMPILE'] = toolchain['prefix']
    env['ARCH'] = toolchain['arch']
    env['PATH'] = os.pathsep.join((toolchain_bin, env.get('PATH', os.environ['PATH'])))

