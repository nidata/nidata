# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from ...core.datasets import NilearnDataset


class Smith2009Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_atlas_smith_2009'


def fetch_smith_2009(data_dir=None, url=None, resume=True, verbose=1):
    return Smith2009Dataset(data_dir=data_dir) \
        .fetch(url=url, resume=resume, verbose=verbose)
