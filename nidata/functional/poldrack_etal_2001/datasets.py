# *- encoding: utf-8 -*-
"""
Utilities to download functional MRI datasets
"""
# Author: Ofer Groweiss
# License: simplified BSD

import os

from sklearn.datasets.base import Bunch

from ...core.datasets import HttpDataset
from ...core.fetchers import readmd5_sum_file


class PoldrackEtal2001Dataset(HttpDataset):
  

    def fetch(self, n_subjects=1, url=None, resume=True, force=False, verbose=1):

		url = 'http://openfmri.s3.amazonaws.com/tarballs/ds052_raw.tgz'
		opts = {'uncompress': True}
		files = [('ds052', url, opts)]
		files = self.fetcher.fetch(files, resume=resume, force=force, verbose=verbose)
		anat_files_names = ['highres001.nii.gz','highres001_brain.nii.gz', 
					'highres001_brain_mask.nii.gz',
					'highres002.nii.gz', 'inplane001.nii.gz',
					'inplane001_brain.nii.gz']
		func_dirs = ['task001_run001','task001_run002','task002_run001','task002_run002']
		n_subjects = 14
		anat_files = [
				os.path.join('ds052','sub%03d' % i, 'anatomy', anat_file)
				for i in range(1, n_subjects+1)
				for anat_file in anat_files_names
				if not (i == 2 and anat_file == 'highres002.nii.gz') and not i==11
		]
		func_files = [
				os.path.join('ds052','sub%03d' % i, 'BOLD', func_dir, 'bold.nii.gz')
				for i in range(1, n_subjects+1)
				for func_dir in func_dirs
				if not i==11
		]
		# return the data
		return Bunch(func=func_files, anat = anat_files)


		
	
