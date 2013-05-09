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
    'CODESOURCERY_201209': {
        'name': 'CodeSourcery ARM EABI 2012.09',
        'arch': 'ARM',
        'prefix': 'arm-none-eabi-',
        'dir': 'arm-2012.09',
        'linux': {
            'tarball': 'arm-2012.09-63-arm-none-eabi-i686-pc-linux-gnu.tar.bz2',
            'url': 'https://sourcery.mentor.com/GNUToolchain/package10926/public/arm-none-eabi',
            'md5': 'd094880c6ac3aea16d4bfb88077186f7',
        },
    }
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

def setup(settings):
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


    os.environ['CROSS_COMPILE'] = toolchain['prefix']
    os.environ['ARCH'] = toolchain['arch']
    os.environ['PATH'] = os.pathsep.join((toolchain_bin, os.environ['PATH']))

