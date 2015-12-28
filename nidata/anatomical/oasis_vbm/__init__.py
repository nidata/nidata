# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from ...core.datasets import NilearnDataset


class OasisVbmDataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_oasis_vbm'

    def fetch(self, n_subjects=None, dartel_version=True,
              url=None, resume=True, force=False, verbose=1):
        super(OasisVbmDataset, self).fetch(n_subjects=n_subjects,
                                           dartel_version=dartel_version,
                                           url=url, resume=resume,
                                           verbose=verbose)


def fetch_oasis_vbm(data_dir=None, n_subjects=None, dartel_version=True,
                    url=None, resume=True, verbose=1):
    return OasisVbmDataset(data_dir=data_dir) \
        .fetch(n_subjects=n_subjects, dartel_version=dartel_version, url=url,
               resume=resume, verbose=verbose)
