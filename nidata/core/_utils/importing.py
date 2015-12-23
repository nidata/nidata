"""
"""

import os
import os.path as op


def import_all_submodules(dir_path, locals, globals, recursive=True):

    subdirs = (filter(lambda fil: op.isdir(op.join(dir_path, fil)) and
               op.exists(op.join(dir_path, fil, '__init__.py')),
                      os.listdir(dir_path)))

    for subdir in subdirs:
        if recursive:
            exec('from .%s import *' % subdir, locals, globals)
        else:
            exec('from . import %s' % subdir, locals, globals)
