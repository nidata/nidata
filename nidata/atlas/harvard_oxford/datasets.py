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
from ...core.datasets import HttpDataset
from ...core.fetchers import (format_time, md5_sum_file, get_dataset_dir)


class HarvardOxfordDataset(HttpDataset):
    """Load Harvard-Oxford parcellation from FSL if installed or download it.

    This function looks up for Harvard Oxford atlas in the system and load it
    if present. If not, it downloads it and store it in NIDATA_PATH
    directory.

    Parameters
    ==========
    atlas_name: string
        Name of atlas to load. Can be:
        cort-maxprob-thr0-1mm,  cort-maxprob-thr0-2mm,
        cort-maxprob-thr25-1mm, cort-maxprob-thr25-2mm,
        cort-maxprob-thr50-1mm, cort-maxprob-thr50-2mm,
        sub-maxprob-thr0-1mm,  sub-maxprob-thr0-2mm,
        sub-maxprob-thr25-1mm, sub-maxprob-thr25-2mm,
        sub-maxprob-thr50-1mm, sub-maxprob-thr50-2mm,
        cort-prob-1mm, cort-prob-2mm,
        sub-prob-1mm, sub-prob-2mm

    data_dir: string, optional
        Path of data directory. It can be FSL installation directory
        (which is dependent on your installation).

    symmetric_split: bool, optional
        If True, split every symmetric region in left and right parts.
        Effectively doubles the number of regions. Default: False.
        Not implemented for probabilistic atlas (*-prob-* atlases)

    Returns
    =======
    regions: nibabel.Nifti1Image
        regions definition, as a label image.
    """
    def __init__(self, data_dir=None):
        super(HarvardOxfordDataset, self).__init__(data_dir=data_dir)
        self.data_dir = get_dataset_dir(self.name, data_dir=data_dir,
                                        env_vars=['FSL_DIR', 'FSLDIR'])

    def fetch(self, atlas_name, symmetric_split=False,
              resume=True, force=False, verbose=1):
        atlas_items = ("cort-maxprob-thr0-1mm", "cort-maxprob-thr0-2mm",
                       "cort-maxprob-thr25-1mm", "cort-maxprob-thr25-2mm",
                       "cort-maxprob-thr50-1mm", "cort-maxprob-thr50-2mm",
                       "sub-maxprob-thr0-1mm", "sub-maxprob-thr0-2mm",
                       "sub-maxprob-thr25-1mm", "sub-maxprob-thr25-2mm",
                       "sub-maxprob-thr50-1mm", "sub-maxprob-thr50-2mm",
                       "cort-prob-1mm", "cort-prob-2mm",
                       "sub-prob-1mm", "sub-prob-2mm")
        if atlas_name not in atlas_items:
            raise ValueError("Invalid atlas name: {0}. Please chose an atlas "
                             "among:\n{1}".format(
                                 atlas_name, '\n'.join(atlas_items)))

        # grab data from internet first
        url = 'https://www.nitrc.org/frs/download.php/7363/HarvardOxford.tgz'
        opts = {'uncompress': True}
        atlas_file = os.path.join('HarvardOxford',
                                  'HarvardOxford-' + atlas_name + '.nii.gz')
        if atlas_name[0] == 'c':
            label_file = 'HarvardOxford-Cortical.xml'
        else:
            label_file = 'HarvardOxford-Subcortical.xml'

        atlas_img, label_file = self.fetcher.fetch(
            [(atlas_file, url, opts), (label_file, url, opts)],
            resume=resume, force=force, verbose=verbose)

        names = {}
        from xml.etree import ElementTree
        names[0] = 'Background'
        for label in ElementTree.parse(label_file).findall('.//label'):
            names[int(label.get('index')) + 1] = label.text
        names = np.asarray(list(names.values()))

        if not symmetric_split:
            return atlas_img, names

        if atlas_name in ("cort-prob-1mm", "cort-prob-2mm",
                          "sub-prob-1mm", "sub-prob-2mm"):
            raise ValueError("Region splitting not supported for probabilistic "
                             "atlases")

        atlas_img = check_niimg(atlas_img)
        atlas = atlas_img.get_data()

        labels = np.unique(atlas)
        # ndimage.find_objects output contains None elements for labels
        # that do not exist
        found_slices = (s for s in ndimage.find_objects(atlas)
                        if s is not None)
        middle_ind = (atlas.shape[0] - 1) // 2
        crosses_middle = [s.start < middle_ind and s.stop > middle_ind
                          for s, _, _ in found_slices]

        # Split every zone crossing the median plane into two parts.
        # Assumes that the background label is zero.
        half = np.zeros(atlas.shape, dtype=np.bool)
        half[:middle_ind, ...] = True
        new_label = max(labels) + 1
        # Put zeros on the median plane
        atlas[middle_ind, ...] = 0
        for label, crosses in zip(labels[1:], crosses_middle):
            if not crosses:
                continue
            atlas[np.logical_and(atlas == label, half)] = new_label
            new_label += 1

        # Duplicate labels for right and left
        new_names = [names[0]]
        for n in names[1:]:
            new_names.append(n + ', right part')
        for n in names[1:]:
            new_names.append(n + ', left part')

        return new_img_like(atlas_img, atlas, atlas_img.get_affine()), new_names


def fetch_harvard_oxford(atlas_name, data_dir=None, symmetric_split=False,
                        resume=True, verbose=1):
    return HarvardOxfordDataset(data_dir=data_dir).fetch(atlas_name=atlas_name,
                                                         symmetric_split=symmetric_split,
                                                         resume=resume, verbose=verbose)

