# -*- utf-8 -*-
# vim: set ts=4 et

import os
import glob


modules = []
files = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
for path in files:
    filename = os.path.basename(path)
    if not filename.startswith('_'):
        root, ext = os.path.splitext(filename)
        modules.append(root)
del files

__all__ = modules


def use(name):
    if name not in modules:
        return None

    module = __import__(name, globals(), locals(), [], -1)
    return module

