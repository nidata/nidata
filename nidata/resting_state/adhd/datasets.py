# *- encoding: utf-8 -*-
"""
Utilities to download resting state MRI datasets
"""
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import numpy as np
from sklearn.datasets.base import Bunch

from ...core.datasets import HttpDataset


class AdhdRestDataset(HttpDataset):
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
    def fetch(self, n_subjects=None, url=None, resume=True, verbose=1):

        if url is None:
            url = 'https://www.nitrc.org/frs/download.php/'

        # Preliminary checks and declarations
        ids = ['0010042', '0010064', '0010128', '0021019', '0023008', '0023012',
               '0027011', '0027018', '0027034', '0027037', '1019436', '1206380',
               '1418396', '1517058', '1552181', '1562298', '1679142', '2014113',
               '2497695', '2950754', '3007585', '3154996', '3205761', '3520880',
               '3624598', '3699991', '3884955', '3902469', '3994098', '4016887',
               '4046678', '4134561', '4164316', '4275075', '6115230', '7774305',
               '8409791', '8697774', '9744150', '9750701']
        nitrc_ids = range(7782, 7822)
        max_subjects = len(ids)
        if n_subjects is None:
            n_subjects = max_subjects
        if n_subjects > max_subjects:
            warnings.warn('Warning: there are only %d subjects' % max_subjects)
            n_subjects = max_subjects
        ids = ids[:n_subjects]
        nitrc_ids = nitrc_ids[:n_subjects]

        opts = dict(uncompress=True)

        # First, get the metadata
        phenotypic = ('ADHD200_40subs_motion_parameters_and_phenotypics.csv',
                      url + '7781/adhd40_metadata.tgz', opts)

        phenotypic = self.fetcher.fetch([phenotypic], resume=resume,
                                 verbose=verbose)[0]

        # Load the csv file
        phenotypic = np.genfromtxt(phenotypic, names=True, delimiter=',',
                                   dtype=None)

        # Keep phenotypic information for selected subjects
        int_ids = np.asarray(ids, dtype=int)
        phenotypic = phenotypic[[np.where(phenotypic['Subject'] == i)[0][0]
                                 for i in int_ids]]

        # Download dataset files

        archives = [url + '%i/adhd40_%s.tgz' % (ni, ii)
                    for ni, ii in zip(nitrc_ids, ids)]
        functionals = ['data/%s/%s_rest_tshift_RPI_voreg_mni.nii.gz' % (i, i)
                       for i in ids]
        confounds = ['data/%s/%s_regressors.csv' % (i, i) for i in ids]

        raise NotImplementedError('When tar file is extracted, data live in a subdirectory and must be moved.')
        functionals = self.fetcher.fetch(
            zip(functionals, archives, (opts,) * n_subjects),
            resume=resume, verbose=verbose)

        confounds = self.fetcher.fetch(
            zip(confounds, archives, (opts,) * n_subjects),
            resume=resume, verbose=verbose)

        return Bunch(func=functionals, confounds=confounds,
                     phenotypic=phenotypic)


def fetch_adhd(n_subjects=None, data_dir=None, url=None, resume=True,
               verbose=1):
    return AdhdRestDataset(data_dir=data_dir).fetch(n_subjects=n_subjects,
                                                    url=url, resume=resume,
                                                    verbose=verbose)
