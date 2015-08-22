"""
"""
import glob
import gzip
import os.path as _osp
import sys
from .core._utils import import_all_submodules as _impall


_script_dir = _osp.dirname(_osp.abspath(__file__))
_impall(_script_dir, locals(), globals(), recursive=False)

# Monkey-patch gzip to have faster reads on large gzip files
if hasattr(gzip.GzipFile, 'max_read_chunk'):
    gzip.GzipFile.max_read_chunk = 100 * 1024 * 1024  # 100Mb

# Add '_external' subdirectories as modules
for _dir in glob.glob(_osp.join(_script_dir, 'core', '_external', '*')):
    if _osp.isdir(_dir):
        sys.path.insert(0, _dir)
