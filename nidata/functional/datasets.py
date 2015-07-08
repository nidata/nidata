# *- encoding: utf-8 -*-
"""
Utilities to download functional MRI datasets
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
from ..core._utils.img import check_niimg, new_img_like
from ..core.fetchers import (format_time, md5_sum_file, fetch_files,
                        get_dataset_dir, get_dataset_descr, _readmd5_sum_file)


def fetch_haxby_simple(data_dir=None, url=None, resume=True, verbose=1):
    """Download and load an example haxby dataset

    Parameters
    ----------
    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        Dictionary-like object, interest attributes are:
        'func': string.  Path to nifti file with bold data.
        'session_target': string. Path to text file containing session and
        target data.
        'mask': string. Path to nifti mask file.
        'session': string. Path to text file containing labels (can be used
        for LeaveOneLabelOut cross validation for example).

    References
    ----------
    `Haxby, J., Gobbini, M., Furey, M., Ishai, A., Schouten, J.,
    and Pietrini, P. (2001). Distributed and overlapping representations of
    faces and objects in ventral temporal cortex. Science 293, 2425-2430.`

    Notes
    -----
    PyMVPA provides a tutorial using this dataset :
    http://www.pymvpa.org/tutorial.html

    More informations about its structure :
    http://dev.pymvpa.org/datadb/haxby2001.html

    See `additional information
    <http://www.sciencemag.org/content/293/5539/2425>`_
    """
    # URL of the dataset. It is optional because a test uses it to test dataset
    # downloading
    if url is None:
        url = 'http://www.pymvpa.org/files/pymvpa_exampledata.tar.bz2'

    opts = {'uncompress': True}
    files = [
            (os.path.join('pymvpa-exampledata', 'attributes.txt'), url, opts),
            (os.path.join('pymvpa-exampledata', 'bold.nii.gz'), url, opts),
            (os.path.join('pymvpa-exampledata', 'mask.nii.gz'), url, opts),
            (os.path.join('pymvpa-exampledata', 'attributes_literal.txt'),
             url, opts),
    ]

    dataset_name = 'haxby2001_simple'
    data_dir = get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    files = fetch_files(data_dir, files, resume=resume, verbose=verbose)

    # There is a common file for the two versions of Haxby
    fdescr = get_dataset_descr('haxby2001')

    # return the data
    return Bunch(func=files[1], session_target=files[0], mask=files[2],
                 conditions_target=files[3], description=fdescr)


def fetch_haxby(data_dir=None, n_subjects=1, fetch_stimuli=False,
                url=None, resume=True, verbose=1):
    """Download and loads complete haxby dataset

    Parameters
    ----------
    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    n_subjects: int, optional
        Number of subjects, from 1 to 6.

    fetch_stimuli: boolean, optional
        Indicate if stimuli images must be downloaded. They will be presented
        as a dictionnary of categories.

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        Dictionary-like object, the interest attributes are :
        'anat': string list. Paths to anatomic images.
        'func': string list. Paths to nifti file with bold data.
        'session_target': string list. Paths to text file containing
        session and target data.
        'mask_vt': string list. Paths to nifti ventral temporal mask file.
        'mask_face': string list. Paths to nifti ventral temporal mask file.
        'mask_house': string list. Paths to nifti ventral temporal mask file.
        'mask_face_little': string list. Paths to nifti ventral temporal
        mask file.
        'mask_house_little': string list. Paths to nifti ventral temporal
        mask file.

    References
    ----------
    `Haxby, J., Gobbini, M., Furey, M., Ishai, A., Schouten, J.,
    and Pietrini, P. (2001). Distributed and overlapping representations of
    faces and objects in ventral temporal cortex. Science 293, 2425-2430.`

    Notes
    -----
    PyMVPA provides a tutorial making use of this dataset:
    http://www.pymvpa.org/tutorial.html

    More information about its structure:
    http://dev.pymvpa.org/datadb/haxby2001.html

    See `additional information
    <http://www.sciencemag.org/content/293/5539/2425>`

    Run 8 in subject 5 does not contain any task labels.
    The anatomical image for subject 6 is unavailable.
    """

    if n_subjects > 6:
        warnings.warn('Warning: there are only 6 subjects')
        n_subjects = 6

    dataset_name = 'haxby2001'
    data_dir = get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)

    # Dataset files
    if url is None:
        url = 'http://data.pymvpa.org/datasets/haxby2001/'
    md5sums = fetch_files(data_dir, [('MD5SUMS', url + 'MD5SUMS', {})],
                           verbose=verbose)[0]
    md5sums = _readmd5_sum_file(md5sums)

    # definition of dataset files
    sub_files = ['bold.nii.gz', 'labels.txt',
                  'mask4_vt.nii.gz', 'mask8b_face_vt.nii.gz',
                  'mask8b_house_vt.nii.gz', 'mask8_face_vt.nii.gz',
                  'mask8_house_vt.nii.gz', 'anat.nii.gz']
    n_files = len(sub_files)

    files = [
            (os.path.join('subj%d' % i, sub_file),
             url + 'subj%d-2010.01.14.tar.gz' % i,
             {'uncompress': True,
              'md5sum': md5sums.get('subj%d-2010.01.14.tar.gz' % i, None)})
            for i in range(1, n_subjects + 1)
            for sub_file in sub_files
            if not (sub_file == 'anat.nii.gz' and i == 6)  # no anat for sub. 6
    ]

    files = fetch_files(data_dir, files, resume=resume, verbose=verbose)

    if n_subjects == 6:
        files.append(None)  # None value because subject 6 has no anat

    kwargs = {}
    if fetch_stimuli:
        stimuli_files = [(os.path.join('stimuli', 'README'),
                          url + 'stimuli-2010.01.14.tar.gz',
                          {'uncompress': True})]
        readme = fetch_files(data_dir, stimuli_files, resume=resume,
                              verbose=verbose)[0]
        kwargs['stimuli'] = _tree(os.path.dirname(readme), pattern='*.jpg',
                                  dictionary=True)

    fdescr = get_dataset_descr(dataset_name)

    # return the data
    return Bunch(
            anat=files[7::n_files],
            func=files[0::n_files],
            session_target=files[1::n_files],
            mask_vt=files[2::n_files],
            mask_face=files[3::n_files],
            mask_house=files[4::n_files],
            mask_face_little=files[5::n_files],
            mask_house_little=files[6::n_files],
            description=fdescr,
            **kwargs)


def fetch_miyawaki2008(data_dir=None, url=None, resume=True, verbose=1):
    """Download and loads Miyawaki et al. 2008 dataset (153MB)

    Returns
    -------
    data: Bunch
        Dictionary-like object, the interest attributes are :
        'func': string list
            Paths to nifti file with bold data
        'label': string list
            Paths to text file containing session and target data
        'mask': string
            Path to nifti mask file to define target volume in visual
            cortex

    References
    ----------
    `Visual image reconstruction from human brain activity
    using a combination of multiscale local image decoders
    <http://www.cell.com/neuron/abstract/S0896-6273%2808%2900958-6>`_,
    Miyawaki, Y., Uchida, H., Yamashita, O., Sato, M. A.,
    Morito, Y., Tanabe, H. C., ... & Kamitani, Y. (2008).
    Neuron, 60(5), 915-929.

    Notes
    -----
    This dataset is available on the `brainliner website
    <http://brainliner.jp/data/brainliner-admin/Reconstruct>`_

    See `additional information
    <http://www.cns.atr.jp/dni/en/downloads/
    fmri-data-set-for-visual-image-reconstruction/>`_
    """

    url = 'https://www.nitrc.org/frs/download.php' \
          '/5899/miyawaki2008.tgz?i_agree=1&download_now=1'
    opts = {'uncompress': True}

    # Dataset files

    # Functional MRI:
    #   * 20 random scans (usually used for training)
    #   * 12 figure scans (usually used for testing)

    func_figure = [(os.path.join('func', 'data_figure_run%02d.nii.gz' % i),
                    url, opts) for i in range(1, 13)]

    func_random = [(os.path.join('func', 'data_random_run%02d.nii.gz' % i),
                    url, opts) for i in range(1, 21)]

    # Labels, 10x10 patches, stimuli shown to the subject:
    #   * 20 random labels
    #   * 12 figure labels (letters and shapes)

    label_filename = 'data_%s_run%02d_label.csv'
    label_figure = [(os.path.join('label', label_filename % ('figure', i)),
                     url, opts) for i in range(1, 13)]

    label_random = [(os.path.join('label', label_filename % ('random', i)),
                     url, opts) for i in range(1, 21)]

    # Masks

    file_mask = [
        'mask.nii.gz',
        'LHlag0to1.nii.gz',
        'LHlag10to11.nii.gz',
        'LHlag1to2.nii.gz',
        'LHlag2to3.nii.gz',
        'LHlag3to4.nii.gz',
        'LHlag4to5.nii.gz',
        'LHlag5to6.nii.gz',
        'LHlag6to7.nii.gz',
        'LHlag7to8.nii.gz',
        'LHlag8to9.nii.gz',
        'LHlag9to10.nii.gz',
        'LHV1d.nii.gz',
        'LHV1v.nii.gz',
        'LHV2d.nii.gz',
        'LHV2v.nii.gz',
        'LHV3A.nii.gz',
        'LHV3.nii.gz',
        'LHV4v.nii.gz',
        'LHVP.nii.gz',
        'RHlag0to1.nii.gz',
        'RHlag10to11.nii.gz',
        'RHlag1to2.nii.gz',
        'RHlag2to3.nii.gz',
        'RHlag3to4.nii.gz',
        'RHlag4to5.nii.gz',
        'RHlag5to6.nii.gz',
        'RHlag6to7.nii.gz',
        'RHlag7to8.nii.gz',
        'RHlag8to9.nii.gz',
        'RHlag9to10.nii.gz',
        'RHV1d.nii.gz',
        'RHV1v.nii.gz',
        'RHV2d.nii.gz',
        'RHV2v.nii.gz',
        'RHV3A.nii.gz',
        'RHV3.nii.gz',
        'RHV4v.nii.gz',
        'RHVP.nii.gz'
    ]

    file_mask = [(os.path.join('mask', m), url, opts) for m in file_mask]

    file_names = func_figure + func_random + \
                 label_figure + label_random + \
                 file_mask

    dataset_name = 'miyawaki2008'
    data_dir = get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    files = fetch_files(data_dir, file_names, resume=resume, verbose=verbose)

    fdescr = get_dataset_descr(dataset_name)

    # Return the data
    return Bunch(
        func=files[:32],
        label=files[32:64],
        mask=files[64],
        mask_roi=files[65:],
        description=fdescr)

