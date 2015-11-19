"""
"""
from ...core.fetchers import AmazonS3Fetcher, HttpFetcher
from ...core.datasets import Dataset


class HcpHttpFetcher(HttpFetcher):
    dependencies = ['requests']

    def __init__(self, data_dir=None, username=None, passwd=None):
        super(HcpHttpFetcher, self).__init__(data_dir=data_dir, username=username, passwd=passwd)
        self.jsession_id = None
    def fetch(self, files, force=False, resume=True, check=False, verbose=1):
        if self.jsession_id is None:
            # Log in to the website.
            import requests
            resp = requests.post('https://db.humanconnectome.org/data/JSESSION',
                                 data={},
                                 auth=(self.username, self.passwd))
            resp.raise_for_status()

            # Get the login information.
            self.jsession_id = resp.cookies.get('JSESSIONID')
            if self.jsession_id is None:
                raise Exception('Failed to create HCP session.')
            self.username = self.passwd = None  # use session

        files = self.reformat_files(files)  # allows flexibility

        # Add the session header
        for tgt, src, opts in files:
            opts['cookies'] = opts.get('cookies', dict())
            opts['cookies'].update({'JSESSIONID': self.jsession_id})

        return super(HcpHttpFetcher, self).fetch(files=files, force=force, resume=resume, check=check, verbose=verbose)


class HcpDataset(Dataset):
    def __init__(self, data_dir=None, fetcher_type='http', profile_name=None, access_key=None, secret_access_key=None,
                 username=None, passwd=None):
        """fetcher_type: aws or XNAT"""
        super(HcpDataset, self).__init__(data_dir=data_dir)
        if fetcher_type == 'aws':
            self.fetcher = AmazonS3Fetcher(data_dir=self.data_dir,
                                           profile_name=profile_name,
                                           access_key=access_key,
                                           secret_access_key=secret_access_key)
        elif fetcher_type in ['http', 'xnat']:
            self.fetcher = HcpHttpFetcher(data_dir=self.data_dir,
                                          username=username,
                                          passwd=passwd)
        else:
            raise NotImplementedError(fetcher_type)

    def get_subject_list(self, n_subjects=500):
        """Get the list of subject IDs. Depends on the # of subjects,
        which also corresponds to other things (license agreement,
        type of data available, etc)"""
        return ['100307']  # 992774']

    def fetch(self, n_subjects=1, data_types=None, volume_types=None, force=False, check=True, verbose=1):
        """data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        if data_types is None:
            data_types = ['anat', 'diff', 'func', 'rest']
        if volume_types is None:
            volume_types = ['3T']  # fsaverage_LR32k, Native

        subj_ids = self.get_subject_list(n_subjects=n_subjects)

        def get_files(dat_type, vol_type):
            subj_path = '{subj_id}/experiments/{subj_id}_CREST/resources/{subj_id}_CREST/files'

            files = []
            if dat_type.startswith('http'):  # assume that absolute urls have been passed
                files.append(dat_type)

            elif vol_type == '3T':
                if dat_type == 'anat':
                    anat_path = '%s/unprocessed/3T' % subj_path
                    files += [('%s/%s' % (anat_path, fil)).format(stype=stype, subj_id=subj_id)
                              for stype in ['T1w_MPR1', 'T2w_SPC1']
                              for fil in [
                                  '{stype}/{subj_id}_3T_AFI.nii.gz',
                                  '{stype}/{subj_id}_3T_BIAS_32CH.nii.gz',
                                  '{stype}/{subj_id}_3T_BIAS_BC.nii.gz',
                                  '{stype}/{subj_id}_3T_FieldMap_Magnitude.nii.gz',
                                  '{stype}/{subj_id}_3T_FieldMap_Phase.nii.gz',
                                  '{stype}/{subj_id}_3T_{stype}.nii.gz',]]

                elif dat_type == 'diff':
                    diff_path = '%s/unprocessed/3T/Diffusion' % subj_path
                    files += [('%s/%s' % (diff_path, fil)).format(subj_id=subj_id, n_dirs=n_dirs)
                              for n_dirs in [95]  # 96? 97?
                              for fil in [
                                  '{subj_id}_3T_BIAS_32CH.nii.gz',
                                  '{subj_id}_3T_BIAS_BC.nii.gz',
                                  '{subj_id}_3T_DWI_dir{n_dirs}_LR.nii.gz',
                                  '{subj_id}_3T_DWI_dir{n_dirs}_LR.bval',
                                  '{subj_id}_3T_DWI_dir{n_dirs}_LR.bvec',
                                  '{subj_id}_3T_DWI_dir{n_dirs}_RL_SBRef.nii.gz']]

                elif dat_type == 'func':
                    rest_path = '%s/unprocessed/3T' % subj_path
                    files += [('%s/%s' % (rest_path, fil)).format(subj_id=subj_id, scan=scan, direction=direction)
                              for scan in ['EMOTION', 'GAMBLING', 'LANGUAGE', 'MOTOR', 'RELATIONAL', 'SOCIAL', 'WM']
                              for direction in ['LR', 'RL']
                              for fil in [
                                  'tfMRI_{scan}_{direction}/{subj_id}_3T_BIAS_32CH.nii.gz',
                                  'tfMRI_{scan}_{direction}/{subj_id}_3T_BIAS_BC.nii.gz',
                                  'tfMRI_{scan}_{direction}/{subj_id}_3T_tfMRI_{scan}_{direction}_SBRef.nii.gz',
                                  'tfMRI_{scan}_{direction}/{subj_id}_3T_tfMRI_{scan}_{direction}.nii.gz',
                                  'tfMRI_{scan}_{direction}/{subj_id}_3T_SpinEchoFieldMap_LR.nii.gz',
                                  'tfMRI_{scan}_{direction}/{subj_id}_3T_SpinEchoFieldMap_RL.nii.gz',]]

                elif dat_type == 'rest':
                    func_path = '%s/unprocessed/3T' % subj_path
                    files += [('%s/%s' % (func_path, fil)).format(subj_id=subj_id, scan=scan, direction=direction)
                              for scan in ['REST1', 'REST2']
                              for direction in ['LR', 'RL']
                              for fil in [
                                  'rfMRI_{scan}_{direction}/{subj_id}_3T_BIAS_32CH.nii.gz',
                                  'rfMRI_{scan}_{direction}/{subj_id}_3T_BIAS_BC.nii.gz',
                                  'rfMRI_{scan}_{direction}/{subj_id}_3T_rfMRI_{scan}_{direction}_SBRef.nii.gz',
                                  'rfMRI_{scan}_{direction}/{subj_id}_3T_rfMRI_{scan}_{direction}.nii.gz',
                                  'rfMRI_{scan}_{direction}/{subj_id}_3T_SpinEchoFieldMap_LR.nii.gz',
                                  'rfMRI_{scan}_{direction}/{subj_id}_3T_SpinEchoFieldMap_RL.nii.gz',]]

            else:
                raise NotImplementedError("Cannot (yet!) fetch '%s' files" % vol_type)

            return files

        # Build a list of files to fetch
        src_files = []
        for subj_id in subj_ids[:n_subjects]:
            for dat_type in data_types:
                for vol_type in volume_types:
                    src_files += get_files(dat_type=dat_type, vol_type=vol_type)

        # Massage paths, based on fetcher type.
        files = []
        for src_file in src_files:
            if isinstance(self.fetcher, HttpFetcher):
                files.append((src_file, 'https://db.humanconnectome.org/data/archive/projects/HCP_500/subjects/' + src_file))
            elif isinstance(self.fetcher, AmazonS3Fetcher):
                files.append((src_file, 'HCP/' + src_file))

        return self.fetcher.fetch(files, force=force, check=check, verbose=verbose)
