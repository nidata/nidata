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

from .._utils.compat import _basestring, BytesIO, cPickle, _urllib, md5_hash
from .._utils.img import check_niimg, new_img_like
from ..fetchers import _format_time, _md5_sum_file, _fetch_files, _get_dataset_dir, _get_dataset_descr


def fetch_craddock_2012_atlas(data_dir=None, url=None, resume=True, verbose=1):
    """Download and return file names for the Craddock 2012 parcellation

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
        verbosity level (0 means no message).

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        dictionary-like object, keys are:
        scorr_mean, tcorr_mean,
        scorr_2level, tcorr_2level,
        random

    References
    ----------
    Licence: Creative Commons Attribution Non-commercial Share Alike
    http://creativecommons.org/licenses/by-nc-sa/2.5/

    Craddock, R. Cameron, G.Andrew James, Paul E. Holtzheimer, Xiaoping P. Hu,
    and Helen S. Mayberg. "A Whole Brain fMRI Atlas Generated via Spatially
    Constrained Spectral Clustering". Human Brain Mapping 33, no 8 (2012):
    1914–1928. doi:10.1002/hbm.21333.

    See http://www.nitrc.org/projects/cluster_roi/ for more information
    on this parcellation.
    """

    if url is None:
        url = "ftp://www.nitrc.org/home/groups/cluster_roi/htdocs" \
              "/Parcellations/craddock_2011_parcellations.tar.gz"
    opts = {'uncompress': True}

    dataset_name = "craddock_2012"
    keys = ("scorr_mean", "tcorr_mean",
            "scorr_2level", "tcorr_2level",
            "random")
    filenames = [
            ("scorr05_mean_all.nii.gz", url, opts),
            ("tcorr05_mean_all.nii.gz", url, opts),
            ("scorr05_2level_all.nii.gz", url, opts),
            ("tcorr05_2level_all.nii.gz", url, opts),
            ("random_all.nii.gz", url, opts)
    ]

    data_dir = _get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    sub_files = _fetch_files(data_dir, filenames, resume=resume,
                             verbose=verbose)

    fdescr = _get_dataset_descr(dataset_name)

    params = dict([('description', fdescr)] + list(zip(keys, sub_files)))

    return Bunch(**params)


def fetch_yeo_2011_atlas(data_dir=None, url=None, resume=True, verbose=1):
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
        verbosity level (0 means no message).

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
    if url is None:
        url = "ftp://surfer.nmr.mgh.harvard.edu/" \
              "pub/data/Yeo_JNeurophysiol11_MNI152.zip"
    opts = {'uncompress': True}

    dataset_name = "yeo_2011"
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

    data_dir = _get_dataset_dir(dataset_name, data_dir=data_dir,
            verbose=verbose)
    sub_files = _fetch_files(data_dir, filenames, resume=resume,
                             verbose=verbose)

    fdescr = _get_dataset_descr(dataset_name)

    params = dict([('description', fdescr)] + list(zip(keys, sub_files)))
    return Bunch(**params)


def fetch_icbm152_2009(data_dir=None, url=None, resume=True, verbose=1):
    """Download and load the ICBM152 template (dated 2009)

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
        dictionary-like object, interest keys are:
        "t1", "t2", "t2_relax", "pd": anatomical images obtained with the
        given modality (resp. T1, T2, T2 relaxometry and proton
        density weighted). Values are file paths.
        "gm", "wm", "csf": segmented images, giving resp. gray matter,
        white matter and cerebrospinal fluid. Values are file paths.
        "eye_mask", "face_mask", "mask": use these images to mask out
        parts of mri images. Values are file paths.

    References
    ----------
    VS Fonov, AC Evans, K Botteron, CR Almli, RC McKinstry, DL Collins
    and BDCG, "Unbiased average age-appropriate atlases for pediatric studies",
    NeuroImage,Volume 54, Issue 1, January 2011

    VS Fonov, AC Evans, RC McKinstry, CR Almli and DL Collins,
    "Unbiased nonlinear average age-appropriate brain templates from birth
    to adulthood", NeuroImage, Volume 47, Supplement 1, July 2009, Page S102
    Organization for Human Brain Mapping 2009 Annual Meeting.

    DL Collins, AP Zijdenbos, WFC Baaré and AC Evans,
    "ANIMAL+INSECT: Improved Cortical Structure Segmentation",
    IPMI Lecture Notes in Computer Science, 1999, Volume 1613/1999, 210–223

    Notes
    -----
    For more information about this dataset's structure:
    http://www.bic.mni.mcgill.ca/ServicesAtlases/ICBM152NLin2009
    """
    if url is None:
        url = "http://www.bic.mni.mcgill.ca/~vfonov/icbm/2009/" \
              "mni_icbm152_nlin_sym_09a_nifti.zip"
    opts = {'uncompress': True}

    keys = ("csf", "gm", "wm",
            "pd", "t1", "t2", "t2_relax",
            "eye_mask", "face_mask", "mask")
    filenames = [(os.path.join("mni_icbm152_nlin_sym_09a", name), url, opts)
                 for name in ("mni_icbm152_csf_tal_nlin_sym_09a.nii",
                              "mni_icbm152_gm_tal_nlin_sym_09a.nii",
                              "mni_icbm152_wm_tal_nlin_sym_09a.nii",

                              "mni_icbm152_pd_tal_nlin_sym_09a.nii",
                              "mni_icbm152_t1_tal_nlin_sym_09a.nii",
                              "mni_icbm152_t2_tal_nlin_sym_09a.nii",
                              "mni_icbm152_t2_relx_tal_nlin_sym_09a.nii",

                              "mni_icbm152_t1_tal_nlin_sym_09a_eye_mask.nii",
                              "mni_icbm152_t1_tal_nlin_sym_09a_face_mask.nii",
                              "mni_icbm152_t1_tal_nlin_sym_09a_mask.nii")]

    dataset_name = 'icbm152_2009'
    data_dir = _get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    sub_files = _fetch_files(data_dir, filenames, resume=resume,
                             verbose=verbose)

    fdescr = _get_dataset_descr(dataset_name)

    params = dict([('description', fdescr)] + list(zip(keys, sub_files)))
    return Bunch(**params)


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
    data_dir = _get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    files_ = _fetch_files(data_dir, files, resume=resume,
                          verbose=verbose)

    fdescr = _get_dataset_descr(dataset_name)

    keys = ['rsn20', 'rsn10', 'rsn70', 'bm20', 'bm10', 'bm70']
    params = dict(zip(keys, files_))
    params['description'] = fdescr

    return Bunch(**params)


def fetch_msdl_atlas(data_dir=None, url=None, resume=True, verbose=1):
    """Download and load the MSDL brain atlas.

    Parameters
    ----------
    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    url: string, optional
        Override download URL. Used for test only (or if you setup a mirror of
        the data).

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        Dictionary-like object, the interest attributes are :
        - 'labels': str. Path to csv file containing labels.
        - 'maps': str. path to nifti file containing regions definition.

    References
    ----------
    :Download:
        https://team.inria.fr/parietal/files/2015/01/MSDL_rois.zip

    :Paper to cite:
        `Multi-subject dictionary learning to segment an atlas of brain
        spontaneous activity <http://hal.inria.fr/inria-00588898/en>`_
        Gaël Varoquaux, Alexandre Gramfort, Fabian Pedregosa, Vincent Michel,
        Bertrand Thirion. Information Processing in Medical Imaging, 2011,
        pp. 562-573, Lecture Notes in Computer Science.

    :Other references:
        `Learning and comparing functional connectomes across subjects
        <http://hal.inria.fr/hal-00812911/en>`_.
        Gaël Varoquaux, R.C. Craddock NeuroImage, 2013.

    """
    url = 'https://team.inria.fr/parietal/files/2015/01/MSDL_rois.zip'
    opts = {'uncompress': True}

    dataset_name = "msdl_atlas"
    files = [(os.path.join('MSDL_rois', 'msdl_rois_labels.csv'), url, opts),
             (os.path.join('MSDL_rois', 'msdl_rois.nii'), url, opts)]

    data_dir = _get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    files = _fetch_files(data_dir, files, resume=resume, verbose=verbose)
    fdescr = _get_dataset_descr(dataset_name)

    return Bunch(labels=files[0], maps=files[1], description=fdescr)


def fetch_harvard_oxford(atlas_name, data_dir=None, symmetric_split=False,
                        resume=True, verbose=1):
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
    dataset_name = 'harvard_oxford'
    data_dir = _get_dataset_dir(dataset_name, data_dir=data_dir,
                                env_vars=['FSL_DIR', 'FSLDIR'],
                                verbose=verbose)
    opts = {'uncompress': True}
    atlas_file = os.path.join('HarvardOxford',
                              'HarvardOxford-' + atlas_name + '.nii.gz')
    if atlas_name[0] == 'c':
        label_file = 'HarvardOxford-Cortical.xml'
    else:
        label_file = 'HarvardOxford-Subcortical.xml'

    atlas_img, label_file = _fetch_files(
        data_dir,
        [(atlas_file, url, opts), (label_file, url, opts)],
        resume=resume, verbose=verbose)

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


def load_mni152_template():
    """Load skullstripped 2mm version of the MNI152 originally distributed
    with FSL

    Returns
    -------
    mni152_template: nibabel object corresponding to the template


    References
    ----------

    VS Fonov, AC Evans, K Botteron, CR Almli, RC McKinstry, DL Collins and
    BDCG, Unbiased average age-appropriate atlases for pediatric studies,
    NeuroImage, Volume 54, Issue 1, January 2011, ISSN 1053–8119, DOI:
    10.1016/j.neuroimage.2010.07.033

    VS Fonov, AC Evans, RC McKinstry, CR Almli and DL Collins, Unbiased
    nonlinear average age-appropriate brain templates from birth to adulthood,
    NeuroImage, Volume 47, Supplement 1, July 2009, Page S102 Organization for
    Human Brain Mapping 2009 Annual Meeting, DOI: 10.1016/S1053-8119(09)70884-5

    """
    package_directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(package_directory, "data", "avg152T1_brain.nii.gz")

    # XXX Should we load the image here?
    return check_niimg(path)

