"""
"""

import os
import os.path as op


def _is_module_dir(dir_path):
    return op.isdir(dir_path) and op.exists(op.join(dir_path, '__init__.py'))


def _get_all_subdirs(dir_path):
    all_paths = (op.join(dir_path, fil) for fil in os.listdir(dir_path))
    all_modules = filter(_is_module_dir, all_paths)
    all_module_names = (op.basename(fil) for fil in all_modules)
    return all_module_names


def import_all_submodules(dir_path, locals, globals, recursive=True):
    subdirs = _get_all_subdirs(dir_path)
    for subdir in subdirs:
        if recursive:
            exec('from .%s import *' % subdir, locals, globals)
        else:
            exec('from . import %s' % subdir, locals, globals)
