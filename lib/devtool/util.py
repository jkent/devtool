# -*- utf-8 -*-
# vim: set ts=4 et

import os
import hashlib
import tarfile
import urllib2

import devtool
from task import task, update_task


def walk_up(bottom):
    bottom = os.path.abspath(bottom)

    while True:
        yield bottom
        new_path = os.path.abspath(os.path.join(bottom, '..'))
        if new_path == bottom:
            return
        bottom = new_path

def download(url):
    downloads_dir = os.path.join(devtool.root_dir, 'downloads')
    filename = url.split('/')[-1]

    @task("Downloading %s" % filename)
    def do():
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
        u = urllib2.urlopen(url)
        filepath = os.path.join(downloads_dir, filename)
        f = open(filepath, 'wb')
        meta = u.info()
        filesize = int(meta.getheaders("Content-Length")[0])

        complete = 0
        while True:
            block = u.read(32*1024)
            if not block:
                break
            complete += len(block)
            f.write(block)
            update_task("%.1f%%" % (float(complete*100)/filesize))

        f.close()
    do()

def check_md5(filepath, md5):
    filename = os.path.basename(filepath)
    
    @task('Checking MD5 for "%s"' % filename)
    def do():
        f = open(filepath)
        md5hash = hashlib.md5()
        while True:
            block = f.read(32*1024)
            if not block:
                break
            md5hash.update(block)
        if md5 != md5hash.hexdigest():
            raise Exception('MD5 hash mismatch')
    do()

def check_sha1(filepath, sha1):
    filename = os.path.basename(filepath)
    
    @task('Checking MD5 for "%s"' % filename)
    def do():
        f = open(filepath)
        sha1hash = hashlib.sha1()
        while True:
            block = f.read(32*1024)
            if not block:
                break
            sha1hash.update(block)
        if sha1 != sha1hash.hexdigest():
            raise Exception('SHA1 hash mismatch')
    do()

def extract(filepath, to_path):
    filename = os.path.basename(filepath)

    @task('Extracting %s' % filename)
    def do():
        if not os.path.exists(to_path):
            os.makedirs(to_path)

        tar = tarfile.open(filepath)
        tar.extractall(path=to_path)
        tar.close()
    do()

