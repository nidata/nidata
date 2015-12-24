# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from ...core.datasets import NilearnDataset


class HarvardOxfordDataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_atlas_harvard_oxford'
    dependencies = ['scipy'] + NilearnDataset.dependencies


def fetch_harvard_oxford(atlas_name, data_dir=None, symmetric_split=False,
                         resume=True, verbose=1):
    return HarvardOxfordDataset(data_dir=data_dir) \
        .fetch(atlas_name=atlas_name, symmetric_split=symmetric_split,
               resume=resume, verbose=verbose)
