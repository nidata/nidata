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
        """
        Parameters
        ----------
        process : boolean
            whether or not the data is processed or not
            can choose from True or False
        subj_id : String
            the id of the subject the files are on
        """
        files = []

        if not process:
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

            files += ['%s/release-notes/Diffusion_preproc.txt' % subj_id]
        return files

    def get_anat_files(self, process, subj_id, atlas, mni, property):
        """
        Parameters
        ----------
        atlas : String
            scope of surface data,
            can choose from native or fsaverage
        mni : boolean
            determines whether to use mninonlinear data or not,
            can choose from true or false
        property : String
            the chosen properties displayed in structural data files
            can choose from myelinmap, curvature, thickness
        process : boolean
            whether or not the data is processed or not
            can choose from True or False
        subj_id : String
            the id of the subject the files are on
        """
        files = []

        if not process:
            anat_path = '%s/unprocessed/3T' % subj_id

            files += ['%s/T1w_MPR1/%s_3T_AFI.nii.gz' % (anat_path, subj_id)]
            files += ['%s/T1w_MPR1/%s_3T_BIAS_32CH.nii.gz' % (anat_path, subj_id)]
            files += ['%s/T1w_MPR1/%s_3T_BIAS_BC.nii.gz' % (anat_path, subj_id)]
            files += ['%s/T1w_MPR1/%s_3T_FieldMap_Magnitude.nii.gz' % (anat_path, subj_id)]
            files += ['%s/T1w_MPR1/%s_3T_FieldMap_Phase.nii.gz' % (anat_path, subj_id)]
            files += ['%s/T1w_MPR1/%s_3T_T1w_MPR1.nii.gz' % (anat_path, subj_id)]

            files += ['%s/release-notes/Structural_unproc.txt' % subj_id]
        else:
            if not mni:
                if atlas == 'native':
                    anat_path = '%s/T1w/Native' % subj_id
                    if property == 'thickness':
                        files += ['%s/%s.L.midthickness.native.surf.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.midthickness.native.surf.gii' % (anat_path, subj_id)]
                elif atlas == 'fsaverage':
                    anat_path = '%s/T1w/fsaverage_LR32k' % subj_id
                    if property == 'thickness':
                        files += ['%s/%s.L.midthickness.32k_fs_LR.surf.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.midthickness.32k_fs_LR.surf.gii' % (anat_path, subj_id)]
            else:
                if atlas == 'native':
                    anat_path = '%s/MNINonLinear/Native' % subj_id
                    if property == 'thickness':
                        files += ['%s/%s.corrThickness.native.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.corrThickness.native.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.midthickness.native.surf.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.thickness.native.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.corrThickness.native.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.midthickness.native.surf.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.thickness.native.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.thickness.native.dscalar.nii' % (anat_path, subj_id)]
                    elif property == 'curvature':
                        files += ['%s/%s.curvature.native.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.curvature.native.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.curvature.native.shape.gii' % (anat_path, subj_id)]
                    elif property == 'myelinmap':
                        files += ['%s/%s.L.MyelinMap.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.MyelinMap_BC.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.SmoothedMyelinMap.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.SmoothedMyelinMap_BC.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.MyelinMap.native.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.MyelinMap_BC.native.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.MyelinMap.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.MyelinMap_BC.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.SmoothedMyelinMap.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.SmoothedMyelinMap_BC.native.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.SmoothedMyelinMap.native.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.SmoothedMyelinMap_BC.native.dscalar.nii' % (anat_path, subj_id)]
                elif atlas == 'fsaverage':
                    anat_path = '%s/MNINonLinear/fsaverage_LR32k' % subj_id
                    if property == 'thickness':
                        files += ['%s/%s.corrThickness.32k_fs_LR.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.corrThickness.32k_fs_LR.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.midthickness.32k_fs_LR.surf.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.thickness.32k_fs_LR.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.corrThickness.32k_fs_LR.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.midthickness.32k_fs_LR.surf.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.thickness.32k_fs_LR.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.thickness.32k_fs_LR.dscalar.nii' % (anat_path, subj_id)]
                    elif property == 'curvature':
                        files += ['%s/%s.curvature.32k_fs_LR.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.curvature.32k_fs_LR.shape.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.curvature.32k_fs_LR.shape.gii' % (anat_path, subj_id)]
                    elif property == 'myelinmap':
                        files += ['%s/%s.L.MyelinMap.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.MyelinMap_BC.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.SmoothedMyelinMap.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.L.SmoothedMyelinMap_BC.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.MyelinMap.32k_fs_LR.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.MyelinMap_BC.32k_fs_LR.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.MyelinMap.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.MyelinMap_BC.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.SmoothedMyelinMap.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.R.SmoothedMyelinMap_BC.32k_fs_LR.func.gii' % (anat_path, subj_id)]
                        files += ['%s/%s.SmoothedMyelinMap.32k_fs_LR.dscalar.nii' % (anat_path, subj_id)]
                        files += ['%s/%s.SmoothedMyelinMap_BC.32k_fs_LR.dscalar.nii' % (anat_path, subj_id)]

            files += ['%s/release-notes/Structural_preproc.txt' % subj_id]
        return files

    def get_rest_files(self, process, subj_id):
        """
        Parameters
        ----------
        process : boolean
            whether or not the data is processed or not
            can choose from True or False
        subj_id : String
            the id of the subject the files are on
        """
        files = []

        if not process:
            rest_path = '%s/unprocessed/3T' % subj_id

            files += ['%s/rfMRI_REST1_LR/%s_3T_BIAS_32CH.nii.gz' % (rest_path, subj_id)]
            files += ['%s/rfMRI_REST1_LR/%s_3T_BIAS_BC.nii.gz' % (rest_path, subj_id)]
            files += ['%s/rfMRI_REST1_LR/%s_3T_rfMRI_REST1_LR_SBRef.nii.gz' % (rest_path, subj_id)]
            files += ['%s/rfMRI_REST1_LR/%s_3T_rfMRI_REST1_LR.nii.gz' % (rest_path, subj_id)]
            files += ['%s/rfMRI_REST1_LR/%s_3T_SpinEchoFieldMap_LR.nii.gz' % (rest_path, subj_id)]
            files += ['%s/rfMRI_REST1_LR/%s_3T_SpinEchoFieldMap_RL.nii.gz' % (rest_path, subj_id)]
            files += ['%s/rfMRI_REST1_LR/LINKED_DATA/PHYSIO/%s_3T_rfMRI_REST1_LR_Physio_log.txt' % (rest_path, subj_id)]

            files += ['%s/release-notes/rfMRI_REST1_unproc.txt' % subj_id]
        else:
            rest_path = '%s/MNINonLinear/Results' % subj_id
            files += ['%s/rfMRI_REST1_LR/brainmask_fs.2.nii.gz' % rest_path]
            files += ['%s/rfMRI_REST1_LR/Movement_Regressors_dt.txt' % rest_path]
            files += ['%s/rfMRI_REST1_LR/Movement_Regressors.txt' % rest_path]
            files += ['%s/rfMRI_REST1_LR/Movement_AbsoluteRMS.txt' % rest_path]
            files += ['%s/rfMRI_REST1_LR/Movement_AbsoluteRMS_mean.txt' % rest_path]
            files += ['%s/rfMRI_REST1_LR/Movement_RelativeRMS.txt' % rest_path]
            files += ['%s/rfMRI_REST1_LR/Movement_RelativeRMS_mean.txt' % rest_path]
            files += ['%s/rfMRI_REST1_LR/rfMRI_REST1_LR_Atlas.dtseries.nii' % rest_path]
            files += ['%s/rfMRI_REST1_LR/rfMRI_REST1_LR_Jacobian.nii.gz' % rest_path]
            files += ['%s/rfMRI_REST1_LR/rfMRI_REST1_LR_SBRef.nii.gz' % rest_path]
            files += ['%s/rfMRI_REST1_LR/rfMRI_REST1_LR.nii.gz' % rest_path]
            files += ['%s/rfMRI_REST1_LR/rfMRI_REST1_LR_Physio_log.txt' % rest_path]
            files += ['%s/rfMRI_REST1_LR/RibbonVolumeToSurfaceMapping/goodvoxels.nii.gz' % rest_path]

            files += ['%s/release-notes/rfMRI_REST1_preproc.txt' % subj_id]
        return files

    def get_task_files(self, process, task, subj_id):
        """
        Parameters
        ----------
        task : String
            the type of activity for functional data,
            can choose from emotional, gambling, language, motor,
            relational, social, and workingmemory
        process : boolean
            whether or not the data is processed or not
            can choose from True or False
        subj_id : String
            the id of the subject the files are on
        """
        files = []

        if not process:
            func_path = '%s/unprocessed/3T' % subj_id

            files += ['%s/tfMRI/EMOTION_LR/%s_3T_BIAS_32CH.nii.gz' % (func_path, subj_id)]
            files += ['%s/tfMRI/EMOTION_LR/%s_3T_BIAS_BC.nii.gz' % (func_path, subj_id)]
            files += ['%s/tfMRI/EMOTION_LR/%s_3T_SpinEchoFieldMap_LR.nii.gz' % (func_path, subj_id)]
            files += ['%s/tfMRI/EMOTION_LR/%s_3T_SpinEchoFieldMap_RL.nii.gz' % (func_path, subj_id)]
            files += ['%s/tfMRI/EMOTION_LR/%s_3T_tfMRI_EMOTION_LR.nii.gz' % (func_path, subj_id)]
            files += ['%s/tfMRI/EMOTION_LR/%s_3T_tfMRI_EMOTION_LR_SBRef.nii.gz' % (func_path, subj_id)]
            files += ['%s/tfMRI/EMOTION_LR/LINKED_DATA/EPRIME/%s_3T_EMOTION_run2_TAB.txt' % (func_path, subj_id)]
            files += ['%s/tfMRI/EMOTION_LR/LINKED_DATA/EPRIME/EVs/EMOTION_Stats.csv' % (func_path)]
            files += ['%s/tfMRI/EMOTION_LR/LINKED_DATA/EPRIME/EVs/fear.txt' % (func_path)]
            files += ['%s/tfMRI/EMOTION_LR/LINKED_DATA/EPRIME/EVs/neut.txt' % (func_path)]
            files += ['%s/tfMRI/EMOTION_LR/LINKED_DATA/EPRIME/EVs/Sync.txt' % (func_path)]

            files += ['%s/release-notes/tfMRI_EMOTION_unproc.txt' % subj_id]
        else:
            if task == 'emotional':
                func_path = '%s/MNINonLinear/Results' % subj_id
                files += ['%s/tfMRI_EMOTION_LR/brainmask_fs.2.nii.gz' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/EMOTION_run2_TAB.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/Movement_Regressors_dt.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/Movement_Regressors.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/Movement_AbsoluteRMS.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/Movement_AbsoluteRMS_mean.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/Movement_RelativeRMS.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/Movement_RelativeRMS_mean.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/tfMRI_EMOTION_LR_Atlas.dtseries.nii' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/tfMRI_EMOTION_LR_Jacobian.nii.gz' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/tfMRI_EMOTION_LR_SBRef.nii.gz' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/tfMRI_EMOTION_LR.nii.gz' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/tfMRI_EMOTION_LR_Physio_log.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/tfMRI_EMOTION_LR_hp200_s4_level1.fsf' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/RibbonVolumeToSurfaceMapping/goodvoxels.nii.gz' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/EVs/EMOTION_Stats.csv' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/EVs/fear.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/EVs/neut.txt' % func_path]
                files += ['%s/tfMRI_EMOTION_LR/EVs/Sync.txt' % func_path]
                files += ['%s/tfMRI_EMOTION/tfMRI_EMOTION_hp200_s4_level2.fsf' % func_path]
                files += ['%s/release-notes/tfMRI_EMOTION_preproc.txt' % subj_id]
        return files

    def fetch(self, n_subjects=1, data_types=None,
              tasks=None, atlases=None, mnis=None, force=False, check=True, verbose=1,
              properties=None, process=None):
        """
        Parameters
        ----------
        n_subjects : int
            the number of subjects to fetch files from
        data_types : list
            the type of data to fetch,
            can choose from anat, diff, func, or rest
        tasks : list
            the type of activity for functional data,
            can choose from emotional, gambling, language, motor,
            relational, social, and workingmemory
        atlases : list
            scope of surface data,
            can choose from native or fsaverage
        mnis : list
            determines whether to use mninonlinear data or not,
            can choose from true or false
        properties : list
            the chosen properties displayed in structural data files
            can choose from myelinmap, curvature, thickness
        process : list
            whether or not the data is processed or not
            can choose from True or False
        """
        if data_types is None:
            data_types = ['anat', 'diff', 'func', 'rest']
        if tasks is None:
            tasks = ['emotional', 'gambling', 'language', 'motor',
                     'relational', 'social', 'workingmemory']
        if atlases is None:
            atlases = ['native', 'fsaverage']
        if mnis is None:
            mnis = [True, False]
        if properties is None:
            properties = ['myelinmap', 'curvature', 'thickness']
        if process is None:
            process = [True]

        subj_ids = self.get_subject_list(n_subjects=n_subjects)

        # Build a list of files to fetch
        src_files = []
        for subj_id in subj_ids[:n_subjects]:
            for data_type in data_types:
                if data_type == 'diff':
                    for pro in process:
                        src_files += self.get_diff_files(process=pro,
                                                         subj_id=subj_id)
                if data_type == 'anat':
                    for pro in process:
                        for atlas in atlases:
                            for mni in mnis:
                                for property in properties:
                                    src_files += self.get_anat_files(process=process,
                                                                     subj_id=subj_id,
                                                                     atlas=atlas,
                                                                     mni=mni,
                                                                     property=property)
                if data_type == 'rest':
                    for pro in process:
                        src_files += self.get_rest_files(process=process,
                                                         subj_id=subj_id)
                if data_type == 'func':
                    for pro in process:
                        for task in tasks:
                            src_files += self.get_task_files(process=process,
                                                             task=task,
                                                             subj_id=subj_id)
        # Massage paths, based on fetcher type.
        files = self.prepend(src_files)
        return files
