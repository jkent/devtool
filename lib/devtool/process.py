# -*- utf-8 -*-
# vim: set ts=4 et

import os
import sys
from subprocess import call, PIPE, Popen, STDOUT
from threading import Thread
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

from devtool import debug


ON_POSIX = 'posix' in sys.builtin_module_names

class Process(object):
    def __init__(self, *args, **kwargs):
        if any(k not in ('cwd', 'env') for k in kwargs.keys()):
            raise TypeError, "only cwd and env are acceptable kwargs"

        cwd = kwargs.get('cwd', None)
        env = kwargs.get('env', None)

        self.p = Popen(args, bufsize=1, stdout= PIPE, stderr=STDOUT,
                 cwd=cwd, env=env)
        self.q = Queue()
        def enqueue():
            for line in iter(self.p.stdout.readline, b''):
                self.q.put(line.rstrip('\n'))
            self.p.stdout.close()

        self.t = Thread(target=enqueue)
        self.t.daemon = True
        self.t.start()

    def read(self):
        if self.q.empty():
            return

        return self.q.get()

    def poll(self):
        return self.p.poll()

    def wait(self):
        return self.p.wait()

    def close(self):
        status = self.p.poll()
        if status == None:
            self.p.kill()
    
        while not self.q.empty():
            self.q.get()

def run_background(*args, **kwargs):
    cwd = kwargs.get('cwd', None)
    if cwd == None:
        cwd = os.path.abspath(os.curdir)
    command = ' '.join('"%s"' % s if ' ' in s else s for s in args)
    
    p = Process(*args, **kwargs)
    if debug:
        print "\n%s$ %s" % (cwd, command)

    buf = ''
    while True:
        rv = p.poll()
        if rv != None:
            p.close()
            break

        line = p.read()
        if line != None:
            if debug:
                print line
            else:
                buf += ''

    if not debug and rv:
        print "\n%s$ %s" % (cwd, command)
        print buf

    return rv

def run(*args, **kwargs):
    if any(k not in ('cwd', 'env') for k in kwargs.keys()):
        raise TypeError, "only cwd and env are acceptable kwargs"

    cwd = kwargs.get('cwd', None)
    env = kwargs.get('env', None)
    return call(args, cwd=cwd, env=env)

