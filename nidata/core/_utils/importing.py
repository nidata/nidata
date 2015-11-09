"""
"""
import os.path


def import_all_submodules(dir_path, locals, globals, recursive=True):

    subdirs = filter(lambda fil: os.path.isdir(os.path.join(dir_path, fil)) and
                                 os.path.exists(os.path.join(dir_path, fil, '__init__.py')),
                     os.listdir(dir_path))

    for subdir in subdirs:
        print(os.getcwd(), subdir)
        if recursive:
            exec('from .%s import *' % subdir, locals, globals)
        else:
            exec('from . import %s' % subdir, locals, globals)
