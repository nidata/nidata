"""
"""
from ...core.fetchers import HttpFetcher
from ...core.datasets import Dataset


class HaxbyEtal2011(Dataset):
    dependencies = ['h5py']  # ['pymvpa2']

    def __init__(self, data_dir=None):
        """
        """
        super(HaxbyEtal2011, self).__init__(data_dir=data_dir)
        self.fetcher = HttpFetcher(data_dir=data_dir)

    def fetch(self, n_subjects=1, force=False, check=True, verbosity=1):
        """data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        files = (('hyperalignment_tutorial_data.hdf5.gz',
                  'http://data.pymvpa.org/datasets/hyperalignment_tutorial_data/hyperalignment_tutorial_data.hdf5.gz',
                  {}),)
        out_files = self.fetcher.fetch(files, force=force, check=check, verbosity=verbosity)

        import os
        import sys
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        mvpa2_path = os.path.abspath(os.path.join(cur_dir, '..', '..', 'core', '_external', 'pymvpa'))
        sys.path = [mvpa2_path] + sys.path
        from mvpa2.base.hdf5 import h5load
        return h5load(out_files[0])
