# *- encoding: utf-8 -*-
# Author: Alison Campbell, Ben Cipollini
# License: simplified BSD

import glob
import os.path as op
from collections import defaultdict


from ...core.datasets import HttpDataset


class MyConnectome2015Dataset(HttpDataset):
    """
    TODO: MyConnectome2015Dataset docsring

    A data loader utility for downloading fMRI data from OpenfMRI.org

    Adapted by: Alison Campbell
    """

    def fetch(self, data_types=None, session_ids=None,
              resume=True, force=False, verbose=1):
            # before the fetcher, construct URLS to download
            # Openfmri dataset ID ds000031

        if data_types is None:
            data_types = ['functional', 'retinotopy', 'diffusion',
                          'resting_state', 'pilot']
        elif isinstance(data_types, dict):
            session_ids = data_types.get('functional', session_ids)
            data_types = data_types.keys()

        all_session_ids = dict(
            pilot=range(2, 13),
            functional=range(14, 104),
            resting_state=[105],
            diffusion=[106],
            retinotopy=['retinotopy'])

        if session_ids is None:
            session_ids = []
            for data_type in data_types:
                session_ids += all_session_ids[data_type]

        # First, construct the relevant urls
        files = []
        opts = {'uncompress': True}
        base_url = 'https://s3.amazonaws.com/openfmri/tarballs/'

        if 'resting_state' in data_types:
            files += [('ds031/sub00001/ses105',
                       base_url + 'ds031_ses105.tgz', opts)]
        if 'diffusion' in data_types:
            files += [('ds031/sub00001/ses106',
                       base_url + 'ds031_ses106.tgz', opts)]
        if 'retinotopy' in data_types:
            files += [('ds031/sub00001/retinotopy',
                       base_url + 'ds031_retinotopy.tgz', opts)]
        if 'functional' in data_types:
            sess_to_file_map = {
                'ds031_pilot_set.tgz': range(2, 12),
                'ds031_set01.tgz': range(13, 25),
                'ds031_set02.tgz': range(25, 37),
                'ds031_set03.tgz': range(37, 49),
                'ds031_set04.tgz': range(49, 61),
                'ds031_set05.tgz': range(61, 73),
                'ds031_set06.tgz': range(73, 85),
                'ds031_set07.tgz': range(85, 98),
                'ds031_set08.tgz': range(98, 105), }
            for zip_file, sess_range in sess_to_file_map.items():
                if set(session_ids).intersection(set(sess_range)):
                    uncompressed_dir = 'ds031/sub00001/ses%03d' % sess_range[0]
                    remote_url = base_url + zip_file
                    files += [(uncompressed_dir, remote_url, opts)]

        # Now, fetch the files.
        self.fetcher.fetch(files, resume=resume, force=force, verbose=verbose,
                           delete_archive=False)

        # Group the data according to modality.
        out_dict = defaultdict(lambda: [])
        for session_path in glob.glob(op.join(self.data_dir, 'ds031',
                                              'sub00001', 'ses*')):
            session_dirname = op.basename(session_path)
            if (session_dirname not in session_ids and
                    int(session_dirname[3:]) not in session_ids):
                continue

            for data_type in data_types:
                data_type_path = op.join(session_path, data_type)
                if not op.exists(data_type_path):
                    continue

                for img_path in glob.glob(op.join(data_type_path, '*.nii.gz')):
                    out_dict[data_type].append(img_path)

        # return the data
        return dict(**dict(out_dict))
