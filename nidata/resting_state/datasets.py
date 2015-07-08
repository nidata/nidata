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
from ..core._utils.img import check_niimg, new_img_like
from ..core.fetchers import format_time, md5_sum_file, fetch_files, get_dataset_dir, get_dataset_descr


def fetch_nyu_rest(n_subjects=None, sessions=[1], data_dir=None, resume=True,
                   verbose=1):
    """Download and loads the NYU resting-state test-retest dataset.

    Parameters
    ----------
    n_subjects: int, optional
        The number of subjects to load. If None is given, all the
        subjects are used.

    sessions: iterable of int, optional
        The sessions to load. Load only the first session by default.

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        Dictionary-like object, the interest attributes are :
        'func': string list. Paths to functional images.
        'anat_anon': string list. Paths to anatomic images.
        'anat_skull': string. Paths to skull-stripped images.
        'session': numpy array. List of ids corresponding to images sessions.

    Notes
    ------
    This dataset is composed of 3 sessions of 26 participants (11 males).
    For each session, three sets of data are available:

    - anatomical:

      * anonymized data (defaced thanks to BIRN defacer)
      * skullstripped data (using 3DSkullStrip from AFNI)

    - functional

    For each participant, 3 resting-state scans of 197 continuous EPI
    functional volumes were collected :

    - 39 slices
    - matrix = 64 x 64
    - acquisition voxel size = 3 x 3 x 3 mm

    Sessions 2 and 3 were conducted in a single scan session, 45 min
    apart, and were 5-16 months after Scan 1.

    All details about this dataset can be found here :
    http://cercor.oxfordjournals.org/content/19/10/2209.full

    References
    ----------
    :Documentation:
        http://www.nitrc.org/docman/?group_id=274

    :Download:
        http://www.nitrc.org/frs/?group_id=274

    :Paper to cite:
        `The Resting Brain: Unconstrained yet Reliable
        <http://cercor.oxfordjournals.org/content/19/10/2209>`_
        Z. Shehzad, A.M.C. Kelly, P.T. Reiss, D.G. Gee, K. Gotimer,
        L.Q. Uddin, S.H. Lee, D.S. Margulies, A.K. Roy, B.B. Biswal,
        E. Petkova, F.X. Castellanos and M.P. Milham.

    :Other references:
        * `The oscillating brain: Complex and Reliable
          <http://dx.doi.org/10.1016/j.neuroimage.2009.09.037>`_
          X-N. Zuo, A. Di Martino, C. Kelly, Z. Shehzad, D.G. Gee,
          D.F. Klein, F.X. Castellanos, B.B. Biswal, M.P. Milham

        * `Reliable intrinsic connectivity networks: Test-retest
          evaluation using ICA and dual regression approach
          <http://dx.doi.org/10.1016/j.neuroimage.2009.10.080>`_,
          X-N. Zuo, C. Kelly, J.S. Adelstein, D.F. Klein,
          F.X. Castellanos, M.P. Milham

    """
    fa1 = 'http://www.nitrc.org/frs/download.php/1071/NYU_TRT_session1a.tar.gz'
    fb1 = 'http://www.nitrc.org/frs/download.php/1072/NYU_TRT_session1b.tar.gz'
    fa2 = 'http://www.nitrc.org/frs/download.php/1073/NYU_TRT_session2a.tar.gz'
    fb2 = 'http://www.nitrc.org/frs/download.php/1074/NYU_TRT_session2b.tar.gz'
    fa3 = 'http://www.nitrc.org/frs/download.php/1075/NYU_TRT_session3a.tar.gz'
    fb3 = 'http://www.nitrc.org/frs/download.php/1076/NYU_TRT_session3b.tar.gz'
    fa1_opts = {'uncompress': True,
                'move': os.path.join('session1', 'NYU_TRT_session1a.tar.gz')}
    fb1_opts = {'uncompress': True,
                'move': os.path.join('session1', 'NYU_TRT_session1b.tar.gz')}
    fa2_opts = {'uncompress': True,
                'move': os.path.join('session2', 'NYU_TRT_session2a.tar.gz')}
    fb2_opts = {'uncompress': True,
                'move': os.path.join('session2', 'NYU_TRT_session2b.tar.gz')}
    fa3_opts = {'uncompress': True,
                'move': os.path.join('session3', 'NYU_TRT_session3a.tar.gz')}
    fb3_opts = {'uncompress': True,
                'move': os.path.join('session3', 'NYU_TRT_session3b.tar.gz')}

    p_anon = os.path.join('anat', 'mprage_anonymized.nii.gz')
    p_skull = os.path.join('anat', 'mprage_skullstripped.nii.gz')
    p_func = os.path.join('func', 'lfo.nii.gz')

    subs_a = ['sub05676', 'sub08224', 'sub08889', 'sub09607', 'sub14864',
              'sub18604', 'sub22894', 'sub27641', 'sub33259', 'sub34482',
              'sub36678', 'sub38579', 'sub39529']
    subs_b = ['sub45463', 'sub47000', 'sub49401', 'sub52738', 'sub55441',
              'sub58949', 'sub60624', 'sub76987', 'sub84403', 'sub86146',
              'sub90179', 'sub94293']

    # Generate the list of files by session
    anat_anon_files = [
        [(os.path.join('session1', sub, p_anon), fa1, fa1_opts)
            for sub in subs_a]
        + [(os.path.join('session1', sub, p_anon), fb1, fb1_opts)
            for sub in subs_b],
        [(os.path.join('session2', sub, p_anon), fa2, fa2_opts)
            for sub in subs_a]
        + [(os.path.join('session2', sub, p_anon), fb2, fb2_opts)
            for sub in subs_b],
        [(os.path.join('session3', sub, p_anon), fa3, fa3_opts)
            for sub in subs_a]
        + [(os.path.join('session3', sub, p_anon), fb3, fb3_opts)
            for sub in subs_b]]

    anat_skull_files = [
        [(os.path.join('session1', sub, p_skull), fa1, fa1_opts)
            for sub in subs_a]
        + [(os.path.join('session1', sub, p_skull), fb1, fb1_opts)
            for sub in subs_b],
        [(os.path.join('session2', sub, p_skull), fa2, fa2_opts)
            for sub in subs_a]
        + [(os.path.join('session2', sub, p_skull), fb2, fb2_opts)
            for sub in subs_b],
        [(os.path.join('session3', sub, p_skull), fa3, fa3_opts)
            for sub in subs_a]
        + [(os.path.join('session3', sub, p_skull), fb3, fb3_opts)
            for sub in subs_b]]

    func_files = [
        [(os.path.join('session1', sub, p_func), fa1, fa1_opts)
            for sub in subs_a]
        + [(os.path.join('session1', sub, p_func), fb1, fb1_opts)
            for sub in subs_b],
        [(os.path.join('session2', sub, p_func), fa2, fa2_opts)
            for sub in subs_a]
        + [(os.path.join('session2', sub, p_func), fb2, fb2_opts)
            for sub in subs_b],
        [(os.path.join('session3', sub, p_func), fa3, fa3_opts)
            for sub in subs_a]
        + [(os.path.join('session3', sub, p_func), fb3, fb3_opts)
            for sub in subs_b]]

    max_subjects = len(subs_a) + len(subs_b)
    # Check arguments
    if n_subjects is None:
        n_subjects = len(subs_a) + len(subs_b)
    if n_subjects > max_subjects:
        warnings.warn('Warning: there are only %d subjects' % max_subjects)
        n_subjects = 25

    anat_anon = []
    anat_skull = []
    func = []
    session = []
    for i in sessions:
        if not (i in [1, 2, 3]):
            raise ValueError('NYU dataset session id must be in [1, 2, 3]')
        anat_anon += anat_anon_files[i - 1][:n_subjects]
        anat_skull += anat_skull_files[i - 1][:n_subjects]
        func += func_files[i - 1][:n_subjects]
        session += [i] * n_subjects

    dataset_name = 'nyu_rest'
    data_dir = get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    anat_anon = fetch_files(data_dir, anat_anon, resume=resume,
                             verbose=verbose)
    anat_skull = fetch_files(data_dir, anat_skull, resume=resume,
                              verbose=verbose)
    func = fetch_files(data_dir, func, resume=resume,
                        verbose=verbose)

    fdescr = get_dataset_descr(dataset_name)

    return Bunch(anat_anon=anat_anon, anat_skull=anat_skull, func=func,
                 session=session, description=fdescr)


def fetch_adhd(n_subjects=None, data_dir=None, url=None, resume=True,
               verbose=1):
    """Download and load the ADHD resting-state dataset.

    Parameters
    ----------
    n_subjects: int, optional
        The number of subjects to load. If None is given, all the
        40 subjects are used.

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
         - 'func': Paths to functional resting-state images
         - 'phenotypic': Explanations of preprocessing steps
         - 'confounds': CSV files containing the nuisance variables

    References
    ----------
    :Download:
        ftp://www.nitrc.org/fcon_1000/htdocs/indi/adhd200/sites/ADHD200_40sub_preprocessed.tgz

    """

    if url is None:
        url = 'http://connectir.projects.nitrc.org'
    f1 = url + '/adhd40_p1.tar.gz'
    f2 = url + '/adhd40_p2.tar.gz'
    f3 = url + '/adhd40_p3.tar.gz'
    f4 = url + '/adhd40_p4.tar.gz'
    f1_opts = {'uncompress': True}
    f2_opts = {'uncompress': True}
    f3_opts = {'uncompress': True}
    f4_opts = {'uncompress': True}

    fname = '%s_rest_tshift_RPI_voreg_mni.nii.gz'
    rname = '%s_regressors.csv'

    # Subjects ID per file
    sub1 = ['3902469', '7774305', '3699991']
    sub2 = ['2014113', '4275075', '1019436', '3154996', '3884955', '0027034',
            '4134561', '0027018', '6115230', '0027037', '8409791', '0027011']
    sub3 = ['3007585', '8697774', '9750701', '0010064', '0021019', '0010042',
            '0010128', '2497695', '4164316', '1552181', '4046678', '0023012']
    sub4 = ['1679142', '1206380', '0023008', '4016887', '1418396', '2950754',
            '3994098', '3520880', '1517058', '9744150', '1562298', '3205761',
            '3624598']
    subs = sub1 + sub2 + sub3 + sub4

    subjects_funcs = \
        [(os.path.join('data', i, fname % i), f1, f1_opts) for i in sub1] + \
        [(os.path.join('data', i, fname % i), f2, f2_opts) for i in sub2] + \
        [(os.path.join('data', i, fname % i), f3, f3_opts) for i in sub3] + \
        [(os.path.join('data', i, fname % i), f4, f4_opts) for i in sub4]

    subjects_confounds = \
        [(os.path.join('data', i, rname % i), f1, f1_opts) for i in sub1] + \
        [(os.path.join('data', i, rname % i), f2, f2_opts) for i in sub2] + \
        [(os.path.join('data', i, rname % i), f3, f3_opts) for i in sub3] + \
        [(os.path.join('data', i, rname % i), f4, f4_opts) for i in sub4]

    phenotypic = [('ADHD200_40subs_motion_parameters_and_phenotypics.csv', f1,
        f1_opts)]

    max_subjects = len(subjects_funcs)
    # Check arguments
    if n_subjects is None:
        n_subjects = max_subjects
    if n_subjects > max_subjects:
        warnings.warn('Warning: there are only %d subjects' % max_subjects)
        n_subjects = max_subjects

    subs = subs[:n_subjects]
    subjects_funcs = subjects_funcs[:n_subjects]
    subjects_confounds = subjects_confounds[:n_subjects]

    dataset_name = 'adhd'
    data_dir = get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    subjects_funcs = fetch_files(data_dir, subjects_funcs, resume=resume,
                                  verbose=verbose)
    subjects_confounds = fetch_files(data_dir, subjects_confounds,
            resume=resume, verbose=verbose)
    phenotypic = fetch_files(data_dir, phenotypic, resume=resume,
                              verbose=verbose)[0]

    fdescr = get_dataset_descr(dataset_name)

    # Load phenotypic data
    phenotypic = np.genfromtxt(phenotypic, names=True, delimiter=',',
                               dtype=None)
    # Keep phenotypic information for selected subjects
    isubs = np.asarray(subs, dtype=int)
    phenotypic = phenotypic[[np.where(phenotypic['Subject'] == i)[0][0]
                             for i in isubs]]

    return Bunch(func=subjects_funcs, confounds=subjects_confounds,
                 phenotypic=phenotypic, description=fdescr)



def fetch_abide_pcp(data_dir=None, n_subjects=None, pipeline='cpac',
                    band_pass_filtering=False, global_signal_regression=False,
                    derivatives=['func_preproc'],
                    quality_checked=True, url=None, verbose=1, **kwargs):
    """ Fetch ABIDE dataset

    Fetch the Autism Brain Imaging Data Exchange (ABIDE) dataset wrt criteria
    that can be passed as parameter. Note that this is the preprocessed
    version of ABIDE provided by the preprocess connectome projects (PCP).

    Parameters
    ----------

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    n_subjects: int, optional
        The number of subjects to load. If None is given,
        all 94 subjects are used.

    pipeline: string, optional
        Possible pipelines are "ccs", "cpac", "dparsf" and "niak"

    band_pass_filtering: boolean, optional
        Due to controversies in the literature, band pass filtering is
        optional. If true, signal is band filtered between 0.01Hz and 0.1Hz.

    global_signal_regression: boolean optional
        Indicates if global signal regression should be applied on the
        signals.

    derivatives: string list, optional
        Types of downloaded files. Possible values are: alff, degree_binarize,
        degree_weighted, dual_regression, eigenvector_binarize,
        eigenvector_weighted, falff, func_mask, func_mean, func_preproc, lfcd,
        reho, rois_aal, rois_cc200, rois_cc400, rois_dosenbach160, rois_ez,
        rois_ho, rois_tt, and vmhc. Please refer to the PCP site for more
        details.

    quality_checked: boolean, optional
        if true (default), restrict the list of the subjects to the one that
        passed quality assessment for all raters.

    kwargs: parameter list, optional
        Any extra keyword argument will be used to filter downloaded subjects
        according to the CSV phenotypic file. Some examples of filters are
        indicated below.

    SUB_ID: list of integers in [50001, 50607], optional
        Ids of the subjects to be loaded.

    DX_GROUP: integer in {1, 2}, optional
        1 is autism, 2 is control

    DSM_IV_TR: integer in [0, 4], optional
        O is control, 1 is autism, 2 is Asperger, 3 is PPD-NOS,
        4 is Asperger or PPD-NOS

    AGE_AT_SCAN: float in [6.47, 64], optional
        Age of the subject

    SEX: integer in {1, 2}, optional
        1 is male, 2 is female

    HANDEDNESS_CATEGORY: string in {'R', 'L', 'Mixed', 'Ambi'}, optional
        R = Right, L = Left, Ambi = Ambidextrous

    HANDEDNESS_SCORE: integer in [-100, 100], optional
        Positive = Right, Negative = Left, 0 = Ambidextrous

    Notes
    -----
    Code and description of preprocessing pipelines are provided on the
    `PCP website <http://preprocessed-connectomes-project.github.io/>`.

    References
    ----------
    Nielsen, Jared A., et al. "Multisite functional connectivity MRI
    classification of autism: ABIDE results." Frontiers in human neuroscience
    7 (2013).
    """

    # Parameter check
    for derivative in derivatives:
        if derivative not in [
                'alff', 'degree_binarize', 'degree_weighted',
                'dual_regression', 'eigenvector_binarize',
                'eigenvector_weighted', 'falff', 'func_mask', 'func_mean',
                'func_preproc', 'lfcd', 'reho', 'rois_aal', 'rois_cc200',
                'rois_cc400', 'rois_dosenbach160', 'rois_ez', 'rois_ho',
                'rois_tt', 'vmhc']:
            raise KeyError('%s is not a valid derivative' % derivative)

    strategy = ''
    if not band_pass_filtering:
        strategy += 'no'
    strategy += 'filt_'
    if not global_signal_regression:
        strategy += 'no'
    strategy += 'global'

    # General file: phenotypic information
    dataset_name = 'ABIDE_pcp'
    data_dir = get_dataset_dir(dataset_name, data_dir=data_dir,
                                verbose=verbose)
    if url is None:
        url = ('https://s3.amazonaws.com/fcp-indi/data/Projects/'
               'ABIDE_Initiative')

    if quality_checked:
        kwargs['qc_rater_1'] = 'OK'
        kwargs['qc_anat_rater_2'] = ['OK', 'maybe']
        kwargs['qc_func_rater_2'] = ['OK', 'maybe']
        kwargs['qc_anat_rater_3'] = 'OK'
        kwargs['qc_func_rater_3'] = 'OK'

    # Fetch the phenotypic file and load it
    csv = 'Phenotypic_V1_0b_preprocessed1.csv'
    path_csv = fetch_files(data_dir, [(csv, url + '/' + csv, {})],
                            verbose=verbose)[0]

    # Note: the phenotypic file contains string that contains comma which mess
    # up numpy array csv loading. This is why I do a pass to remove the last
    # field. This can be
    # done simply with pandas but we don't want such dependency ATM
    # pheno = pandas.read_csv(path_csv).to_records()
    with open(path_csv, 'r') as pheno_f:
        pheno = ['i' + pheno_f.readline()]

        # This regexp replaces commas between double quotes
        for line in pheno_f:
            pheno.append(re.sub(r',(?=[^"]*"(?:[^"]*"[^"]*")*[^"]*$)', ";", line))

    # bytes (encode()) needed for python 2/3 compat with numpy
    pheno = '\n'.join(pheno).encode()
    pheno = BytesIO(pheno)
    pheno = np.recfromcsv(pheno, comments='$', case_sensitive=True)

    # First, filter subjects with no filename
    pheno = pheno[pheno['FILE_ID'] != b'no_filename']
    # Apply user defined filters
    user_filter = _filter_columns(pheno, kwargs)
    pheno = pheno[user_filter]

    # Go into specific data folder and url
    data_dir = os.path.join(data_dir, pipeline, strategy)
    url = '/'.join([url, 'Outputs', pipeline, strategy])

    # Get the files
    results = {}
    file_ids = [file_id.decode() for file_id in pheno['FILE_ID']]
    if n_subjects is not None:
        file_ids = file_ids[:n_subjects]
        pheno = pheno[:n_subjects]

    results['description'] = get_dataset_descr(dataset_name)
    results['phenotypic'] = pheno
    for derivative in derivatives:
        ext = '.1D' if derivative.startswith('rois') else '.nii.gz'
        files = [(file_id + '_' + derivative + ext,
                  '/'.join([url, derivative,
                            file_id + '_' + derivative + ext]),
                  {}) for file_id in file_ids]
        files = fetch_files(data_dir, files, verbose=verbose)
        # Load derivatives if needed
        if ext == '.1D':
            files = [np.loadtxt(f) for f in files]
        results[derivative] = files
    return Bunch(**results)
