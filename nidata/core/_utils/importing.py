"""
"""
import os.path


def import_all_submodules(dir_path, locals, globals, recursive=True):

    subdirs = filter(lambda fil: os.path.isdir(os.path.join(dir_path, fil)),
                     os.listdir(dir_path))

    for subdir in subdirs:
        if recursive:
            exec('from .%s import *' % subdir) in locals, globals
        else:
            exec('from . import %s' % subdir) in locals, globals
