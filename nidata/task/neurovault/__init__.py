# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from collections import OrderedDict

import numpy as np

from ...core.datasets import NilearnDataset


class NeuroVaultDataset(NilearnDataset):
    dependencies = OrderedDict(
        [(mod, mod) for mod in NilearnDataset.dependencies],
        nilearn=('git+git://github.com/bcipolli/'
                 'nilearn@neurovault-downloader#egg=nilearn'))  # override
    fetcher_function = 'nilearn.datasets.fetch_neurovault'


def fetch_neurovault(max_images=np.inf,
                     query_server=True,
                     fetch_terms=False,
                     exclude_unpublished=False,
                     exclude_known_bad_images=True,
                     collection_ids=(),
                     image_ids=(), image_type=None, map_types=(),
                     collection_filters=(), image_filters=(),
                     data_dir=None, url="http://neurovault.org/api",
                     resume=True, overwrite=False, verbose=2):

    return NeuroVaultDataset(data_dir=data_dir).fetch(
        max_images=max_images, query_server=query_server,
        fetch_terms=fetch_terms, exclude_unpublished=exclude_unpublished,
        exclude_known_bad_images=exclude_known_bad_images,
        collection_ids=collection_ids, image_ids=image_ids,
        image_type=image_type, map_types=map_types,
        collection_filters=collection_filters, image_filters=image_filters,
        url=url, resume=resume, overwrite=overwrite, verbose=verbose)
