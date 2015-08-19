"""
A data loader utility for downloading fMRI data from OpenfMRI.org

Adapted by: Alison Campbell
"""

# *- encoding: utf-8 -*-
"""
Utilities to download functional MRI datasets
"""
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import os

from sklearn.datasets.base import Bunch

from ...core.datasets import HttpDataset
from ...core.fetchers import readmd5_sum_file


class MyConnectome2015Dataset(HttpDataset):
# class [A CLASS]([A SUPER CLASS]) 

    def fetch(self, n_sessions=None, get_retinotopy=True, get_pilot=True,
              get_diffusion=True, get_resting_state=True,
              resume=True, force=False, verbose=1):
    		# before the fetcher, construct URLS to download
			# Openfmri dataset ID ds000031
    		
        # First, construct the relevant urls
        files = []
        opts = {'uncompress': True}
        base_url = 'https://s3.amazonaws.com/openfmri/tarballs/'

        if n_sessions >= 0 or n_sessions is None:  # this file: 13-24
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if n_sessions >= 13 or n_sessions is None:  # this file: 25-36
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if n_sessions >= 25 or n_sessions is None:  # this file: 37-48
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if n_sessions >= 37 or n_sessions is None:  # this file: 49-60
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if n_sessions >= 49 or n_sessions is None:  # this file: 61-72
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if n_sessions >= 61 or n_sessions is None:  # this file: 73-84
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if n_sessions >= 73 or n_sessions is None:  # this file: 85-97
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if n_sessions >= 86 or n_sessions is None:  # this file: 98-104
            files += [('ds031_set01', base_url + 'ds031_set01.tgz', opts)]
        if get_pilot:
            files += [('ds031_pilot_set', base_url + 'ds031_pilot_set.tgz', opts)]
        if get_resting_state:
            files += [('ds031_ses105', base_url + 'ds031_ses105.tgz', opts)]
        if get_diffusion:
            files += [('ds031_ses106', base_url + 'ds031_ses106.tgz', opts)]
        if get_retinotopy:
            files += [('ds031_retinotopy', base_url + 'ds031_retinotopy.tgz', opts)]

        # Now, fetch the files.
        files = self.fetcher.fetch(files, resume=resume, force=force, verbose=verbose)

        # Group the data according to modality.

        # return the data
        return Bunch(func=files[1], session_target=files[0], mask=files[2],
                         conditions_target=files[3])

