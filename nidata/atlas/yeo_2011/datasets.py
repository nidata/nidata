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
from ...core.datasets import Dataset
from ...core.fetchers import (format_time, md5_sum_file, fetch_files)


class Yeo2011Dataset(Dataset):
    """Download and return file names for the Yeo 2011 parcellation.

    The provided images are in MNI152 space.

    Parameters
    ----------
    data_dir: string
        directory where data should be downloaded and unpacked.

    url: string
        url of file to download.

    resume: bool
        whether to resumed download of a partly-downloaded file.

    verbose: int
        verbose level (0 means no message).

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        dictionary-like object, keys are:

        - "thin_7", "thick_7": 7-region parcellations,
          fitted to resp. thin and thick template cortex segmentations.

        - "thin_17", "thick_17": 17-region parcellations.

        - "colors_7", "colors_17": colormaps (text files) for 7- and 17-region
          parcellation respectively.

        - "anat": anatomy image.

    Notes
    -----
    For more information on this dataset's structure, see
    http://surfer.nmr.mgh.harvard.edu/fswiki/CorticalParcellation_Yeo2011

    Yeo BT, Krienen FM, Sepulcre J, Sabuncu MR, Lashkari D, Hollinshead M,
    Roffman JL, Smoller JW, Zollei L., Polimeni JR, Fischl B, Liu H,
    Buckner RL. The organization of the human cerebral cortex estimated by
    intrinsic functional connectivity. J Neurophysiol 106(3):1125-65, 2011.

    Licence: unknown.
    """


    def fetch(self, url=None, resume=True, verbose=1):
        if url is None:
            url = "ftp://surfer.nmr.mgh.harvard.edu/" \
                  "pub/data/Yeo_JNeurophysiol11_MNI152.zip"
        opts = {'uncompress': True}

        keys = ("thin_7", "thick_7",
                "thin_17", "thick_17",
                "colors_7", "colors_17", "anat")
        basenames = (
            "Yeo2011_7Networks_MNI152_FreeSurferConformed1mm.nii.gz",
            "Yeo2011_7Networks_MNI152_FreeSurferConformed1mm_LiberalMask.nii.gz",
            "Yeo2011_17Networks_MNI152_FreeSurferConformed1mm.nii.gz",
            "Yeo2011_17Networks_MNI152_FreeSurferConformed1mm_LiberalMask.nii.gz",
            "Yeo2011_7Networks_ColorLUT.txt",
            "Yeo2011_17Networks_ColorLUT.txt",
            "FSL_MNI152_FreeSurferConformed_1mm.nii.gz")

        filenames = [(os.path.join("Yeo_JNeurophysiol11_MNI152", f), url, opts)
                     for f in basenames]

        sub_files = fetch_files(self.data_dir, filenames, resume=resume,
                                verbose=verbose)

        params = dict(list(zip(keys, sub_files)))
        return Bunch(**params)


def fetch_yeo_2011_atlas(data_dir=None, url=None, resume=True, verbose=1):
    return Yeo2011Dataset(data_dir=data_dir).fetch(url=url, resume=resume, verbose=verbose)
