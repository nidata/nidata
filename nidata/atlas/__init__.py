"""
Datasets defining cortical parcellations.
"""

import os.path as _osp
from ..core._utils import import_all_submodules as _impall
_impall(_osp.dirname(_osp.abspath(__file__)), locals(), globals())
