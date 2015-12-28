# *- encoding: utf-8 -*-
# Author: Ofer Groweiss
# License: simplified BSD

import glob
import os.path as op
import re

import numpy as np

from ...core.datasets import HttpDataset


class OpenFMriDataset(HttpDataset):
    """
    TODO: OpenFMriDataset docstring.
    """
    dependencies = (['numpy', 'scipy', 'sklearn', 'pandas', 'nibabel',
                    'nipy', 'nilearn'] + HttpDataset.dependencies)

    @staticmethod
    def get_subj_from_path(pth):
        """
        TODO: get_subj_from_path docstring.
        """
        match = re.match('.*(sub-[0-9]+).*', pth)
        if not match:
            return None
        else:
            return match.groups()[0]

    @staticmethod
    def get_task_from_path(pth):
        """
        TODO: get_task_from_path docstring.
        """
        match = re.match('.*sub-[0-9]+_task-([^_]+)_', pth)
        if not match:
            return None
        else:
            return match.groups()[0]

    @staticmethod
    def get_run_from_path(pth):
        """
        TODO: get_run_from_path docstring.
        """

        match = re.match('.*_(run[0-9]+)', pth)
        if not match:
            return None
        else:
            return match.groups()[0]

    def preprocess_files(self, func_files, anat_files=None, verbose=1):
        """
        TODO: preprocess_files docstring.
        """
        import pandas as pd
        import nibabel
        import nipy.modalities.fmri.design_matrix as dm
        from nilearn.image import index_img
        from nilearn.masking import compute_epi_mask
        from nipy.modalities.fmri.glm import FMRILinearModel
        from nipy.modalities.fmri.experimental_paradigm import (
            EventRelatedParadigm)

        def get_beta_filepath(func_file, cond):
            return func_file.replace('_bold.nii.gz', '_beta-%s.nii.gz' % cond)

        beta_files = []
        for fi, func_file in enumerate(func_files):
            # Don't re-do preprocessing.
            # beta_mask = func_file.replace('_bold.nii.gz', '_beta*.nii.gz')
            cond_file = func_file.replace('_bold.nii.gz', '_events.tsv')
            cond_data = pd.read_csv(cond_file, sep='\t')

            # Get condition info, to search if betas have been done.
            conditions = cond_data['trial_type'].tolist()
            all_conds = np.unique(conditions)
            all_beta_files = [get_beta_filepath(func_file, cond)
                              for cond in all_conds]
            # All betas are done.
            if np.all([op.exists(f) for f in all_beta_files]):
                beta_files += all_beta_files
                continue

            if verbose >= 0:
                print('Preprocessing file %d of %d' % (
                    fi + 1, len(func_files)))

            # Need to do regression.
            tr = cond_data['duration'].as_matrix().mean()
            onsets = cond_data['onset'].tolist()

            img = nibabel.load(func_file)
            n_scans = img.shape[3]
            frametimes = np.linspace(0, (n_scans - 1) * tr, n_scans)

            # Create the design matrix
            paradigm = EventRelatedParadigm(conditions, onsets)
            design_mat = dm.make_dmtx(frametimes, paradigm,
                                      drift_model='cosine',
                                      hfcut=n_scans, hrf_model='canonical')

            # Do the GLM
            mask_img = compute_epi_mask(img)
            fmri_glm = FMRILinearModel(img, design_mat.matrix, mask=mask_img)
            fmri_glm.fit(do_scaling=True, model='ar1')

            # Pull out the betas
            beta_hat = fmri_glm.glms[0].get_beta()  # Least-squares estimates
            mask = fmri_glm.mask.get_data() > 0

            # output beta images
            dim = design_mat.matrix.shape[1]
            beta_map = np.tile(mask.astype(np.float)[..., np.newaxis], dim)
            beta_map[mask] = beta_hat.T
            beta_image = nibabel.Nifti1Image(beta_map, fmri_glm.affine)
            beta_image.get_header()['descrip'] = ("Parameter estimates of "
                                                  "the localizer dataset")

            # Save beta images
            for ci, cond in enumerate(np.unique(conditions)):
                beta_cond_img = index_img(beta_image, ci)
                beta_filepath = get_beta_filepath(func_file, cond)
                nibabel.save(beta_cond_img, beta_filepath)
                beta_files.append(beta_filepath)

        return beta_files


class PoldrackEtal2001Dataset(OpenFMriDataset):
    """
    TODO: PoldrackEtal2001Dataset docstring.
    """
    dependencies = ['openfmri2bids'] + OpenFMriDataset.dependencies

    def fetch(self, n_subjects=1, preprocess_data=True,
              url=None, resume=True, force=False, verbose=1):
        from openfmri2bids.converter import convert

        # Prep the URLs
        if not op.exists(op.join(self.data_dir, 'ds052_BIDS')):
            url = 'http://openfmri.s3.amazonaws.com/tarballs/ds052_raw.tgz'
            opts = {'uncompress': True}
            files = [('ds052', url, opts)]
            files = self.fetcher.fetch(files, resume=resume, force=force,
                                       verbose=verbose)

            # Move around the files to BIDS format.
            convert(source_dir=op.join(self.data_dir, 'ds052'),
                    dest_dir=op.join(self.data_dir, 'ds052_BIDS'),
                    nii_handling='link')

        # Loop over subjects to extract files.
        anat_files = []
        func_files = []
        for subj_dir in glob.glob(op.join(self.data_dir,
                                          'ds052_BIDS', 'sub-*')):
            anat_files += glob.glob(op.join(subj_dir,
                                            'anatomy', '*_T1w_run*.nii.gz'))
            func_files += glob.glob(op.join(subj_dir, 'functional',
                                            '*_task-*_bold*.nii.gz'))

        if preprocess_data:
            func_files = self.preprocess_files(func_files,
                                               anat_files=anat_files)

        # return the data
        return dict(func=func_files, anat=anat_files)
