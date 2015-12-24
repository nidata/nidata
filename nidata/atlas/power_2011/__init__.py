# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from ...core.datasets import NilearnDataset


class Power2011Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_atlas_power_2011'

    def fetch(self, verbose=0):
        return self.fetcher.fetch()  # doesn't take any params


def fetch_power_2011(data_dir=None, url=None, resume=True, verbose=1):
    return Power2011Dataset(data_dir=data_dir) \
        .fetch(url=url, resume=resume, verbose=verbose)
