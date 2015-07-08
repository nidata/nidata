from ..core.fetchers import AmazonS3Fetcher
from ..core.datasets import Dataset


class HcpDataset(Dataset):
    def __init__(self, fetcher_type='aws', profile_name=None, access_key=None, secret_access_key=None):
        """fetcher_type: aws or XNAT"""
        if fetcher_type == 'aws':
            self.fetcher = AmazonS3Fetcher(profile_name=profile_name,
                                           access_key=access_key,
                                           secret_access_key=secret_access_key)
        else:
            raise NotImplementedError(fetcher_type)

    def get_subject_list(self, n_subjects=500):
        """Get the list of subject IDs. Depends on the # of subjects,
        which also corresponds to other things (license agreement,
        type of data available, etc)"""
        return ['992774']

    def fetch(self, n_subjects=1, data_types=None, force=False, check=True, verbosity=1):
        """data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        subj_ids = self.get_subject_list(n_subjects=n_subjects)

        # Build a list of files to fetch
        files = []
        for subj_id in subj_ids[:n_subjects]:
            for dtype in (data_types or ['anat', 'diff', 'func', 'rest']):
                if dtype == 'diff':
                    files += zip(['hcp/dwi_lr.nii.gz', 'hcp/dwi_lr.bval', 'hcp/dwi_lr.bvec'],
                                 ['HCP/%(subj_id)s/unprocessed/3T/Diffusion/%(subj_id)s_3T_DWI_dir95_LR.nii.gz' % {'subj_id': subj_id},
                                  'HCP/%(subj_id)s/unprocessed/3T/Diffusion/%(subj_id)s_3T_DWI_dir95_LR.bval'   % {'subj_id': subj_id},
                                  'HCP/%(subj_id)s/unprocessed/3T/Diffusion/%(subj_id)s_3T_DWI_dir95_LR.bvec'   % {'subj_id': subj_id}],
                                 [{}, {}, {}])
                else:
                    raise NotImplementedError()

        return self.fetcher.fetch(files, force=force, check=check, verbosity=verbosity)
