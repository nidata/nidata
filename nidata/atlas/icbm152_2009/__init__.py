# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD


from ...core.datasets import NilearnDataset


class ICBM152Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_icbm152_2009'

    def fetch(self, url=None, resume=True, verbose=1):
        super(ICBM152Dataset, self).fetch(data_dir=self.data_dir,
                                          url=url, resume=resume,
                                          verbose=verbose)


def fetch_icbm152_2009(data_dir=None, url=None, resume=True, verbose=1):
    return ICBM152Dataset(data_dir=data_dir) \
        .fetch(url=url, resume=resume, verbose=verbose)
