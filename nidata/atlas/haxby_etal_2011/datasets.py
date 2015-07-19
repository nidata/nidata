"""
"""
import os
import sys

import nibabel as nib
import numpy as np
from sklearn.datasets.base import Bunch

from ...core.fetchers import HttpFetcher
from ...core.datasets import HttpDataset


class HaxbyEtal2011Dataset(HttpDataset):
    dependencies = ['h5py']  # ['pymvpa2']
    MAX_SUBJECTS = 10

    def fetch(self, n_subjects=10, resume=True, force=False, check=True, verbose=1):
        """data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        if n_subjects > self.MAX_SUBJECTS:
            raise ValueError('Max # subjects == %d' % self.MAX_SUBJECTS)

        processed_files = ['S%02d_func_mni.nii.gz' % subj_id
                           for subj_id in range(1, 1 + n_subjects)]
        processed_files.append('stims.csv')
        processed_files = [os.path.join(self.data_dir, f)
                           for f in processed_files]

        raw_files = ('http://data.pymvpa.org/datasets/hyperalignment_tutorial_data/hyperalignment_tutorial_data_2.4.hdf5.gz',)
        raw_files = self.fetcher.fetch(raw_files, resume=resume, force=force,
                                       check=check, verbose=verbose)

        if force or np.any([not os.path.exists(f) for f in processed_files]):
            # Import local version of pymvpa
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            mvpa2_path = os.path.abspath(os.path.join(cur_dir, '..', '..', 'core', '_external', 'pymvpa'))
            sys.path = [mvpa2_path] + sys.path
            from mvpa2.base.hdf5 import h5load

            # Load the file and manipulate into expected form.
            ds_all = h5load(raw_files[0])
            for si, func_filename in enumerate(processed_files[:-1]):
                if not os.path.exists(os.path.dirname(func_filename)):
                    os.makedirs(os.path.dirname(func_filename))

                # Construct and save the image
                func_data = np.transpose(ds_all[si].O, [1, 2, 3, 0])
                func_affine = ds_all[si].a['imgaffine'].value
                func_hdr = ds_all[si].a['imghdr'].value
                img = nib.Nifti1Image(func_data, affine=func_affine)#, header=func_hdr)
                nib.save(img, func_filename)

            # Construct and save the stimuli
            value_arr = np.asarray([ds_all[0].T, ds_all[0].sa['chunks']])
            csv_cols = np.vstack([['stim', 'chunk'], value_arr.T])
            np.savetxt(processed_files[-1], csv_cols, delimiter=',', fmt='%s')

        return Bunch(
            raw_data=raw_files[0],
            func=processed_files[:-1],
            stim=processed_files[-1])
