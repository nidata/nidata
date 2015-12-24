# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

import os
import os.path as op
import sys

import nibabel as nib
import numpy as np

from ...core.datasets import HttpDataset


class HaxbyEtal2011Dataset(HttpDataset):
    """
    TODO: Haxby needs a docstring
    """
    dependencies = ['h5py'] + HttpDataset.dependencies
    MAX_SUBJECTS = 10

    def fetch(self, n_subjects=10, resume=True, force=False, check=True,
              verbose=1):
        """data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        if n_subjects > self.MAX_SUBJECTS:
            raise ValueError('Max # subjects == %d' % self.MAX_SUBJECTS)

        processed_files = ['S%02d_func_mni.nii.gz' % subj_id
                           for subj_id in range(1, 1 + n_subjects)]
        processed_files.append('stims.csv')
        processed_files = [op.join(self.data_dir, f)
                           for f in processed_files]

        raw_files = ('http://data.pymvpa.org/datasets/'
                     'hyperalignment_tutorial_data/'
                     'hyperalignment_tutorial_data_2.4.hdf5.gz',)
        raw_files = self.fetcher.fetch(raw_files, resume=resume, force=force,
                                       check=check, verbose=verbose)

        if force or np.any([not op.exists(f) for f in processed_files]):
            # Import local version of pymvpa
            cur_dir = op.dirname(op.abspath(__file__))
            mvpa2_path = op.abspath(op.join(cur_dir, '..', '..', 'core',
                                            '_external', 'pymvpa'))
            sys.path = [mvpa2_path] + sys.path
            from mvpa2.base.hdf5 import h5load

            # Load the file and manipulate into expected form.
            ds_all = h5load(raw_files[0])
            for si, func_filename in enumerate(processed_files[:-1]):
                if not op.exists(op.dirname(func_filename)):
                    os.makedirs(op.dirname(func_filename))

                # Construct and save the image
                func_data = np.transpose(ds_all[si].O, [1, 2, 3, 0])
                func_affine = ds_all[si].a['imgaffine'].value
                func_hdr = ds_all[si].a['imghdr'].value
                img = nib.Nifti1Image(func_data, affine=func_affine,
                                      header=func_hdr)
                nib.save(img, func_filename)

            # Construct and save the stimuli
            value_arr = np.asarray([ds_all[0].T, ds_all[0].sa['chunks']])
            csv_cols = np.vstack([['stim', 'chunk'], value_arr.T])
            np.savetxt(processed_files[-1], csv_cols, delimiter=',', fmt='%s')

        return dict(
            raw_data=raw_files[0],
            func=processed_files[:-1],
            stim=processed_files[-1])
