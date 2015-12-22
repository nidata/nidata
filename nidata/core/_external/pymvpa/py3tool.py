#!/usr/bin/env python3
"""
Convert *py files with lib2to3.
Taken from MDP and numpy.
"""

import shutil
import os
import os.path as op
import sys
import fnmatch
import lib2to3.main
from io import StringIO


EXTRA_2TO3_FLAGS = {'*': '-x import'}

BASE = op.normpath(op.join(op.dirname(__file__), '..'))
TEMP = op.normpath(op.join(BASE, '_py3k'))

def custom_mangling(filename):
    pass

def walk_sync(dir1, dir2, _seen=None):
    if _seen is None:
        seen = {}
    else:
        seen = _seen

    if not dir1.endswith(op.sep):
        dir1 = dir1 + op.sep

    # Walk through stuff (which we haven't yet gone through) in dir1
    for root, dirs, files in os.walk(dir1):
        sub = root[len(dir1):]
        if sub in seen:
            dirs = [x for x in dirs if x not in seen[sub][0]]
            files = [x for x in files if x not in seen[sub][1]]
            seen[sub][0].extend(dirs)
            seen[sub][1].extend(files)
        else:
            seen[sub] = (dirs, files)
        if not dirs and not files:
            continue
        yield op.join(dir1, sub), op.join(dir2, sub), dirs, files

    if _seen is None:
        # Walk through stuff (which we haven't yet gone through) in dir2
        for root2, root1, dirs, files in walk_sync(dir2, dir1, _seen=seen):
            yield root1, root2, dirs, files


def sync_2to3(src, dst, clean=False):

    to_convert = []

    for src_dir, dst_dir, dirs, files in walk_sync(src, dst):
        for fn in dirs + files:
            src_fn = op.join(src_dir, fn)
            dst_fn = op.join(dst_dir, fn)

            # skip temporary etc. files
            if fn.startswith('.#') or fn.endswith('~'):
                continue

            # remove non-existing
            if op.exists(dst_fn) and not op.exists(src_fn):
                if clean:
                    if op.isdir(dst_fn):
                        shutil.rmtree(dst_fn)
                    else:
                        os.unlink(dst_fn)
                continue

            # make directories
            if op.isdir(src_fn):
                if not op.isdir(dst_fn):
                    os.makedirs(dst_fn)
                continue

            dst_dir = op.dirname(dst_fn)
            if op.isfile(dst_fn) and not op.isdir(dst_dir):
                os.makedirs(dst_dir)

            # don't replace up-to-date files
            try:
                if op.isfile(dst_fn) and \
                       os.stat(dst_fn).st_mtime >= os.stat(src_fn).st_mtime:
                    continue
            except OSError:
                pass

            # copy file
            if not op.islink(src_fn):
                shutil.copyfile(src_fn, dst_fn)
            elif not op.islink(dst_fn):
                # replicate ths symlink at the destination if doesn't exist yet
                os.symlink(os.readlink(src_fn), dst_fn)

            # add .py files to 2to3 list
            if dst_fn.endswith('.py'):
                to_convert.append((src_fn, dst_fn))

    # run 2to3
    flag_sets = {}
    for fn, dst_fn in to_convert:
        flag = ''
        for pat, opt in EXTRA_2TO3_FLAGS.items():
            if fnmatch.fnmatch(fn, pat):
                flag = opt
                break
        flag_sets.setdefault(flag, []).append(dst_fn)

    for flags, filenames in flag_sets.items():
        if flags == 'skip':
            continue

        _old_stdout = sys.stdout
        try:
            sys.stdout = StringIO()
            lib2to3.main.main("lib2to3.fixes", ['-w'] + flags.split()+filenames)
        finally:
            sys.stdout = _old_stdout

    for fn, dst_fn in to_convert:
        # perform custom mangling
        custom_mangling(dst_fn)
