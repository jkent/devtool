# -*- utf-8 -*-
# vim: set ts=4 et

from functools import wraps
import sys


tasks = []
last = 0


def update_task(status=''):
    global tasks

    if not tasks:
        return

    output = '\033[2K\r%s%s...%s' % ('  ' * (len(tasks)-1), tasks[-1], status)
    sys.stdout.write(output)
    sys.stdout.flush()


def task(message):
    def task_decorator(f):
        @wraps(f)
        def task_wrapper(*args, **kwargs):
            global tasks, last

            if tasks and last < len(tasks):
                output = '\033[2K\r%s%s\n' % ('  ' * last, tasks[-1])
                sys.stdout.write(output)
                sys.stdout.flush()

            tasks.append(message)
            last = len(tasks)-1
            update_task()

            try:
                r = f(*args, **kwargs)
            except:
                update_task('failed')
                del tasks[-1]
                print
                raise

            update_task('done')
            del tasks[-1]
            print

            return r
        return task_wrapper
    return task_decorator

