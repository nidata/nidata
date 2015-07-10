# *- encoding: utf-8 -*-
"""
Utilities to download NeuroImaging-based atlases
"""
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import contextlib
import collections
import os
import tarfile
import zipfile
import sys
import shutil
import time
import hashlib
import fnmatch
import warnings
import re
import base64

import numpy as np
from scipy import ndimage
from sklearn.datasets.base import Bunch

from ...core._utils.compat import (_basestring, BytesIO, cPickle, _urllib,
                                   md5_hash)
from ...core._utils.niimg import check_niimg, new_img_like
from ...core.fetchers import (format_time, md5_sum_file, fetch_files,
                              get_dataset_dir)


def fetch_power_2011():
    """Download and load the Power et al. brain atlas composed of 264 ROIs.
    Returns
    -------
    data: sklearn.datasets.base.Bunch
        dictionary-like object, contains:
        - "rois": coordinates of 264 ROIs in MNI space
    References
    ----------
    Power, Jonathan D., et al. "Functional network organization of the human
    brain." Neuron 72.4 (2011): 665-678.
    """
    # https://raw.githubusercontent.com/nilearn/nilearn/master/nilearn/data/power_2011.csv
    dataset_name = 'power_2011'
    package_directory = os.path.dirname(os.path.abspath(__file__))
    csv = os.path.join(package_directory, "data", "power_2011.csv")
    params = dict(rois=np.recfromcsv(csv))

    return Bunch(**params)