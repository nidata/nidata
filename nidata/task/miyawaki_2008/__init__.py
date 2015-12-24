# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD


from ...core.datasets import NilearnDataset


class Miyawaki2008Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_miyawaki2008'


def fetch_miyawaki2008(data_dir=None, url=None, resume=True, verbose=1):
    return Miyawaki2008Dataset(data_dir=data_dir).fetch(url=url,
                                                        resume=resume,
                                                        verbose=verbose)
