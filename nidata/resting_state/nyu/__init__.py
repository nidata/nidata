# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD


from ...core.datasets import NilearnDataset


class NyuRestDataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_nyu_rest'


def fetch_nyu_rest(n_subjects=None, sessions=[1], data_dir=None, resume=True,
                   verbose=1):
    return NyuRestDataset(data_dir=data_dir).fetch(n_subjects=n_subjects,
                                                   sessions=sessions,
                                                   resume=resume,
                                                   verbose=verbose)
