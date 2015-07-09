# *- encoding: utf-8 -*-
"""
Utilities to download resting state MRI datasets
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

from ..core._utils.compat import _basestring, BytesIO, cPickle, _urllib, md5_hash
from ..core._utils.niimg import check_niimg, new_img_like
from ..core.fetchers import (format_time, md5_sum_file, fetch_files,
                             get_dataset_dir, get_dataset_descr, filter_columns)


def fetch_smith_2009(data_dir=None, url=None, resume=True, verbose=1):
    """Download and load the Smith ICA and BrainMap atlas (dated 2009)

    Parameters
    ----------
    data_dir: string, optional
        Path of the data directory. Use to forec data storage in a non-
        standard location. Default: None (meaning: default)
    url: string, optional
        Download URL of the dataset. Overwrite the default URL.

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        dictionary-like object, contains:
        - 20-dimensional ICA, Resting-FMRI components:
            - all 20 components (rsn20)
            - 10 well-matched maps from these, as shown in PNAS paper (rsn10)

        - 20-dimensional ICA, BrainMap components:
            - all 20 components (bm20)
            - 10 well-matched maps from these, as shown in PNAS paper (bm10)

        - 70-dimensional ICA, Resting-FMRI components (rsn70)

        - 70-dimensional ICA, BrainMap components (bm70)


    References
    ----------

    S.M. Smith, P.T. Fox, K.L. Miller, D.C. Glahn, P.M. Fox, C.E. Mackay, N.
    Filippini, K.E. Watkins, R. Toro, A.R. Laird, and C.F. Beckmann.
    Correspondence of the brain's functional architecture during activation and
    rest. Proc Natl Acad Sci USA (PNAS), 106(31):13040-13045, 2009.

    A.R. Laird, P.M. Fox, S.B. Eickhoff, J.A. Turner, K.L. Ray, D.R. McKay, D.C
    Glahn, C.F. Beckmann, S.M. Smith, and P.T. Fox. Behavioral interpretations
    of intrinsic connectivity networks. Journal of Cognitive Neuroscience, 2011

    Notes
    -----
    For more information about this dataset's structure:
    http://www.fmrib.ox.ac.uk/analysis/brainmap+rsns/
    """
    if url is None:
        url = "http://www.fmrib.ox.ac.uk/analysis/brainmap+rsns/"

    files = [('rsn20.nii.gz', url + 'rsn20.nii.gz', {}),
             ('PNAS_Smith09_rsn10.nii.gz',
                 url + 'PNAS_Smith09_rsn10.nii.gz', {}),
             ('rsn70.nii.gz', url + 'rsn70.nii.gz', {}),
             ('bm20.nii.gz', url + 'bm20.nii.gz', {}),
             ('PNAS_Smith09_bm10.nii.gz',
                 url + 'PNAS_Smith09_bm10.nii.gz', {}),
             ('bm70.nii.gz', url + 'bm70.nii.gz', {}),
             ]

    dataset_name = 'smith_2009'
    data_dir = get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    files_ = fetch_files(data_dir, files, resume=resume,
                          verbose=verbose)

    fdescr = get_dataset_descr(dataset_name)

    keys = ['rsn20', 'rsn10', 'rsn70', 'bm20', 'bm10', 'bm70']
    params = dict(zip(keys, files_))
    params['description'] = fdescr

    return Bunch(**params)

