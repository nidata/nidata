# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from ...core.datasets import NilearnDataset


class Yeo2011Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_atlas_yeo_2011'


def fetch_yeo_2011_atlas(data_dir=None, url=None, resume=True, verbose=1):
    return Yeo2011Dataset(data_dir=data_dir) \
        .fetch(url=url, resume=resume, verbose=verbose)
