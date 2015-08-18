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


class Laumann2015Dataset(HttpDataset):
# class [A CLASS]([A SUPER CLASS]) 

    def fetch(self, n_subjects=1, fetch_stimuli=False,
              url=None, resume=True, force=False, verbose=1):
    		# before the fetcher, construct URLS to download
			# Openfmri dataset ID ds000031
    		
    	files = [('ds031','https://s3.amazonaws.com/openfmri/tarballs/ds031_retinotopy.tgz', {'uncompress':False}),
    				 ]

    				 # ('ds109_raw.tgz','https://s3.amazonaws.com/openfmri/tarballs/ds031_retinotopy.tgz', {'uncompress':True}),
    				 # ('ds109_raw.tgz','https://s3.amazonaws.com/openfmri/tarballs/ds031_retinotopy.tgz', {'uncompress':True}),
    				 # ('ds109_raw.tgz','https://s3.amazonaws.com/openfmri/tarballs/ds031_retinotopy.tgz', {'uncompress':True}),
    				 # ('ds109_raw.tgz','https://s3.amazonaws.com/openfmri/tarballs/ds031_retinotopy.tgz', {'uncompress':True}),
    				 # ('ds109_raw.tgz','https://s3.amazonaws.com/openfmri/tarballs/ds031_retinotopy.tgz', {'uncompress':True}),
    				 # ]	
						

        files = self.fetcher.fetch(files, resume=resume, force=force, verbose=verbose)

            # return the data
        return Bunch(func=files[1], session_target=files[0], mask=files[2],
                         conditions_target=files[3])

