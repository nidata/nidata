# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD


from ...core.datasets import NilearnDataset


class AdhdRestDataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_adhd'


def fetch_adhd(n_subjects=None, data_dir=None, url=None, resume=True,
               verbose=1):
    return AdhdRestDataset(data_dir=data_dir).fetch(n_subjects=n_subjects,
                                                    url=url, resume=resume,
                                                    verbose=verbose)
