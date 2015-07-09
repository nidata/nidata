"""
"""
import gzip
import os.path as _osp
from .core._utils import import_all_submodules as _impall


_impall(_osp.dirname(_osp.abspath(__file__)), locals(), globals(), recursive=False)

# Monkey-patch gzip to have faster reads on large gzip files
if hasattr(gzip.GzipFile, 'max_read_chunk'):
    gzip.GzipFile.max_read_chunk = 100 * 1024 * 1024  # 100Mb
