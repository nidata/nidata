# *- encoding: utf-8 -*-
# Author: Ben Cipollini, Howard Zhang
# License: simplified BSD

import os

from ...core.datasets import Dataset
from ...core.fetchers import AmazonS3Fetcher, HttpFetcher


class HcpHttpFetcher(HttpFetcher):
    """TODO: HcpHttpFetcher docstring"""

    dependencies = ['requests'] + HttpFetcher.dependencies

    def __init__(self, data_dir=None, username=None, passwd=None):
        username = username or os.environ.get("NIDATA_HCP_USERNAME")
        passwd = passwd or os.environ.get("NIDATA_HCP_PASSWD")
        if username is None or passwd is None:
            raise ValueError("Must define NIDATA_HCP_USERNAME and "
                             "NIDATA_HCP_PASSWD environment variables, or "
                             "pass username and passwd arguments.")

        super(HcpHttpFetcher, self).__init__(data_dir=data_dir,
                                             username=username,
                                             passwd=passwd)
        self.jsession_id = None

    def fetch(self, files, force=False, resume=True, check=False, verbose=1):
        if self.jsession_id is None:
            # Log in to the website.
            import requests
            res = requests.post('https://db.humanconnectome.org/data/JSESSION',
                                data={},
                                auth=(self.username, self.passwd))
            res.raise_for_status()

            # Get the login information.
            self.jsession_id = res.cookies.get('JSESSIONID')
            if self.jsession_id is None:
                raise Exception('Failed to create HCP session.')
            self.username = self.passwd = None  # use session

        files = self.reformat_files(files)  # allows flexibility

        # Add the session header
        for tgt, src, opts in files:
            opts['cookies'] = opts.get('cookies', dict())
            opts['cookies'].update({'JSESSIONID': self.jsession_id})

        return super(HcpHttpFetcher, self).fetch(files=files, force=force,
                                                 resume=resume, check=check,
                                                 verbose=verbose)


class HcpDataset(Dataset):
    """TODO: HcpDataset docstring"""

    def __init__(self, data_dir=None, fetcher_type='http', profile_name='hcp',
                 access_key=None, secret_access_key=None,
                 username=None, passwd=None):
        """fetcher_type: aws or XNAT"""
        super(HcpDataset, self).__init__(data_dir=data_dir)
        self.fetcher_type = fetcher_type
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

    def prepend(self, src_files):
        """
        Prepends the proper absolute url to a list of files, based on fetcher type.

        Parameters
        ----------

        src_files: list of str
            uncompleted urls without the prepended fetcher type


        Returns
        -------

        list of fully qualified urls
        """
        files = []
        for src_file in src_files:
            if isinstance(self.fetcher, HttpFetcher):
                files.append((src_file, 'https://db.humanconnectome.org/data/'
                                        'archive/projects/HCP_900/subjects/' +
                                        src_file))
            elif isinstance(self.fetcher, AmazonS3Fetcher):
                files.append((src_file, 'HCP/' + src_file))
        return files

    def get_subject_list(self, n_subjects=None):
        """
        Get the list of subject IDs. Depends on the # of subjects,
        which also corresponds to other things (license agreement,
        type of data available, etc)
        """
        subj_file_info = (('S900.txt', 900),
                          ('S500.txt', 500),
                          ('U100.txt', 100))

        fil = None
        errs = dict()
        # Loop until we retreive a file that's good.
        for fname, nsubj in subj_file_info:
            try:
                fil = self.fetcher.fetch(
                    files=self.prepend([fname]), verbose=0)[0]
                with open(fil, 'r') as fp:
                    data = fp.read()

                # Make sure it's a good file.
                subject_ids = data.split('\n')
                subject_ids = filter(lambda sid: sid != '',
                                     [sid.strip() for sid in subject_ids])
                if subject_ids < nsubj:
                    os.remove(fil)  # corrupt
                    raise ValueError("Removed corrupt file %s" % fil)
                else:
                    break
            except Exception as e:
                errs[fname] = e
                continue

        # Completed the loop. Make sure we succeeded,
        # and that what's requested is possible.
        if fil is None:
            raise Exception("Failed to fetch subject list from any file. "
                            "Error details: %s" % errs)
        if n_subjects > nsubj:
            raise IndexError("Subjects number requested is too high. Please "
                             "enter a number <= %d." % nsubj)

        return subject_ids[:n_subjects]

    def get_diff_files(self, process, subj_id):
        files = []

        if process == False:
            diff_path = '%s/unprocessed/3T/Diffusion' % subj_id
            files += ['%s/%s_3T_BIAS_32CH.nii.gz' % (diff_path, subj_id)]
            files += ['%s/%s_3T_BIAS_BC.nii.gz' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_LR_SBRef.nii.gz' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_LR.bval' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_LR.bvec' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_LR.nii.gz' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_RL_SBRef.nii.gz' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_RL.bval' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_RL.bvec' % (diff_path, subj_id)]
            files += ['%s/%s_3T_DWI_dir95_RL.nii.gz' % (diff_path, subj_id)]
            files += ['%s/release-notes/Diffusion_unproc.txt' % subj_id]
        else:
            diff_path = '%s/T1w/Diffusion' % subj_id
            files += ['%s/bvals' % diff_path]
            files += ['%s/bvecs' % diff_path]
            files += ['%s/data.nii.gz' % diff_path]
        return files


    def get_files(self, data_type, volume_type, process, subj_id):
        assert subj_id is not None and subj_id != ''

        files = []

        if 'diff' in data_type:
            files = self.get_diff_files(process, subj_id);
        return files


    """def get_files(self, data_type, volume_type, subj_id):
        assert subj_id is not None and subj_id != ''

        if self.fetcher_type == 'aws':
            # S3 bucket specific layout
            subj_path = '{subj_id}'
        else:  # xnat/http
            subj_path = ('{subj_id}/experiments/{subj_id}_CREST/resources/'
                         '{subj_id}_CREST/files')

        files = []

        if volume_type == '3T' and data_type == 'anat':
            anat_path = '%s/unprocessed/3T' % subj_path
            files += [('%s/%s' % (anat_path, fil))
                      .format(stype=stype, subj_id=subj_id)
                      for stype in ['T1w_MPR1', 'T2w_SPC1']
                      for fil in [
                          '{stype}/{subj_id}_3T_AFI.nii.gz',
                          '{stype}/{subj_id}_3T_BIAS_32CH.nii.gz',
                          '{stype}/{subj_id}_3T_BIAS_BC.nii.gz',
                          '{stype}/{subj_id}_3T_FieldMap_Magnitude.nii.gz',
                          '{stype}/{subj_id}_3T_FieldMap_Phase.nii.gz',
                          '{stype}/{subj_id}_3T_{stype}.nii.gz']]

        elif volume_type == '3T' and data_type == 'diff':
            diff_path = '%s/unprocessed/3T/Diffusion' % subj_path
            files += [('%s/%s' % (diff_path, fil))
                      .format(subj_id=subj_id, n_dirs=n_dirs)
                      for n_dirs in [95]  # 96? 97?
                      for fil in [
                          '{subj_id}_3T_BIAS_32CH.nii.gz',
                          '{subj_id}_3T_BIAS_BC.nii.gz',
                          '{subj_id}_3T_DWI_dir{n_dirs}_LR.nii.gz',
                          '{subj_id}_3T_DWI_dir{n_dirs}_LR.bval',
                          '{subj_id}_3T_DWI_dir{n_dirs}_LR.bvec',
                          '{subj_id}_3T_DWI_dir{n_dirs}_RL_SBRef.nii.gz']]

        elif volume_type == '3T' and data_type == 'func':
            rest_path = '%s/unprocessed/3T' % subj_path
            files += [('%s/tfMRI_{scan}_{direction}/%s' % (rest_path, fil))
                      .format(subj_id=subj_id, scan=scan, direction=direction)
                      for scan in ['EMOTION', 'GAMBLING', 'LANGUAGE', 'MOTOR',
                                   'RELATIONAL', 'SOCIAL', 'WM']
                      for direction in ['LR', 'RL']
                      for fil in [
                          '{subj_id}_3T_BIAS_32CH.nii.gz',
                          '{subj_id}_3T_BIAS_BC.nii.gz',
                          '{subj_id}_3T_tfMRI_{scan}_{direction}_SBRef.nii.gz',
                          '{subj_id}_3T_tfMRI_{scan}_{direction}.nii.gz',
                          '{subj_id}_3T_SpinEchoFieldMap_LR.nii.gz',
                          '{subj_id}_3T_SpinEchoFieldMap_RL.nii.gz']]

        elif volume_type == '3T' and data_type == 'rest':
            func_path = '%s/unprocessed/3T' % subj_path
            files += [('%s/rfMRI_{scan}_{direction}/%s' % (func_path, fil))
                      .format(subj_id=subj_id, scan=scan, direction=direction)
                      for scan in ['REST1', 'REST2']
                      for direction in ['LR', 'RL']
                      for fil in [
                          '{subj_id}_3T_BIAS_32CH.nii.gz',
                          '{subj_id}_3T_BIAS_BC.nii.gz',
                          '{subj_id}_3T_rfMRI_{scan}_{direction}_SBRef.nii.gz',
                          '{subj_id}_3T_rfMRI_{scan}_{direction}.nii.gz',
                          '{subj_id}_3T_SpinEchoFieldMap_LR.nii.gz',
                          '{subj_id}_3T_SpinEchoFieldMap_RL.nii.gz']]

        else:
            raise NotImplementedError("Cannot (yet!) fetch '%s' files" % (
                volume_type))
        return files"""

    def fetch(self, n_subjects=1, data_types=None, volume_types=None,
              force=False, check=True, verbose=1, process = None):
        """
        TODO: fetch docstring
        data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        if data_types is None:
            data_types = ['anat', 'diff', 'func', 'rest']
        if volume_types is None:
            volume_types = ['3T']  # fsaverage_LR32k, Native
        if process is None:
            process = [True, False]

        subj_ids = self.get_subject_list(n_subjects=n_subjects)

        # Build a list of files to fetch
        src_files = []
        for subj_id in subj_ids[:n_subjects]:
            for data_type in data_types:
                for volume_type in volume_types:
                    for pro in process:
                        src_files += self.get_files(data_type=data_type,
                                                volume_type=volume_type,
                                                process=pro,
                                                subj_id=subj_id)

        # Massage paths, based on fetcher type.
        files = self.prepend(src_files)
        return self.fetcher.fetch(files, force=force, check=check,
                                  verbose=verbose)
