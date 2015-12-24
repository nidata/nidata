# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD


from ...core.datasets import NilearnDataset


class Craddock2012Dataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_atlas_craddock_2012'

    def fetch(self, url=None, resume=True, verbose=1):
        super(Craddock2012Dataset, self).fetch(data_dir=self.data_dir,
                                               url=url, resume=resume,
                                               verbose=verbose)


def fetch_atlas_craddock_2012(data_dir=None, url=None, resume=True, verbose=1):
    return Craddock2012Dataset(data_dir=data_dir) \
        .fetch(url=url, resume=resume, verbose=verbose)
