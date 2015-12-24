# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from ...core.datasets import NilearnDataset


class MNI152Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.load_mni152_template'

    def fetch(self, verbose=0):
        return self.fetcher.fetch()  # doesn't take any params


def fetch_mni152_template(data_dir=None, url=None, resume=True, verbose=1):
    return MNI152Dataset(data_dir=data_dir) \
        .fetch(url=url, resume=resume, verbose=verbose)
