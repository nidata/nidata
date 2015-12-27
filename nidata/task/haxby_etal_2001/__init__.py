# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD


from ...core.datasets import NilearnDataset


class Haxby2001Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_haxby'
    nilearn_name = 'haxby_2001'


def fetch_haxby_simple(data_dir=None, url=None, resume=True, verbose=1):
    dset = Haxby2001Dataset(data_dir=data_dir, simple=True)
    return dset.fetch(url=url, resume=resume, verbose=verbose)


def fetch_haxby(data_dir=None, n_subjects=1, fetch_stimuli=False,
                url=None, resume=True, verbose=1):
    dset = Haxby2001Dataset(data_dir=data_dir, simple=False)
    return dset.fetch(n_subjects=n_subjects, fetch_stimuli=fetch_stimuli,
                      url=url, resume=resume, verbose=verbose)
