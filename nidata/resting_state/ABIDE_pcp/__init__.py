# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import re

import numpy as np

from ...core._utils.compat import BytesIO
from ...core.datasets import HttpDataset
from ...core.fetchers import filter_columns


class AbidePcpDataset(HttpDataset):
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

    def fetch(self, n_subjects=None, pipeline='cpac',
              band_pass_filtering=False, global_signal_regression=False,
              derivatives=['func_preproc'],
              quality_checked=True, url=None, resume=True, force=False,
              verbose=1, **kwargs):
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
        path_csv = self.fetcher.fetch([(csv, url + '/' + csv, {})],
                                      resume=resume, force=force,
                                      verbose=verbose)[0]

        # Note: the phenotypic file contains string that contains comma which
        # mess up numpy array csv loading. This is why I do a pass to remove
        # the last field. This can be done simply with pandas but we don't
        #  want such dependency ATM.
        # pheno = pandas.read_csv(path_csv).to_records()
        with open(path_csv, 'r') as pheno_f:
            pheno = ['i' + pheno_f.readline()]

            # This regexp replaces commas between double quotes
            for line in pheno_f:
                pheno.append(re.sub(r',(?=[^"]*"(?:[^"]*"[^"]*")*[^"]*$)', ";",
                             line))

        # bytes (encode()) needed for python 2/3 compat with numpy
        pheno = '\n'.join(pheno).encode()
        pheno = BytesIO(pheno)
        pheno = np.recfromcsv(pheno, comments='$', case_sensitive=True)

        # First, filter subjects with no filename
        pheno = pheno[pheno['FILE_ID'] != b'no_filename']
        # Apply user defined filters
        user_filter = filter_columns(pheno, kwargs)
        pheno = pheno[user_filter]

        # Go into specific data folder and url
        url = '/'.join([url, 'Outputs', pipeline, strategy])

        # Get the files
        results = {}
        file_ids = [file_id.decode() for file_id in pheno['FILE_ID']]
        if n_subjects is not None:
            file_ids = file_ids[:n_subjects]
            pheno = pheno[:n_subjects]

        results['phenotypic'] = pheno
        for derivative in derivatives:
            ext = '.1D' if derivative.startswith('rois') else '.nii.gz'
            files = [(file_id + '_' + derivative + ext,
                      '/'.join([url, derivative,
                                file_id + '_' + derivative + ext]),
                      {}) for file_id in file_ids]
            files = self.fetcher.fetch(files, resume=resume, force=force,
                                       verbose=verbose)
            # Load derivatives if needed
            if ext == '.1D':
                files = [np.loadtxt(f) for f in files]
            results[derivative] = files
        return dict(**results)


def fetch_abide_pcp(data_dir=None, n_subjects=None, pipeline='cpac',
                    band_pass_filtering=False, global_signal_regression=False,
                    derivatives=['func_preproc'],
                    quality_checked=True, url=None, verbose=1, **kwargs):
    return AbidePcpDataset(data_dir=data_dir) \
        .fetch(n_subjects=n_subjects, pipeline=pipeline,
               band_pass_filtering=band_pass_filtering,
               global_signal_regression=global_signal_regression,
               derivatives=derivatives,
               quality_checked=quality_checked,
               url=url, verbose=verbose,
               **kwargs)
