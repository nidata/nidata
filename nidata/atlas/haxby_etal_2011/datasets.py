"""
"""
from ...core.fetchers import HttpFetcher
from ...core.datasets import HttpDataset


class HaxbyEtal2011(HttpDataset):
    dependencies = ['h5py']  # ['pymvpa2']

    def fetch(self, n_subjects=1, resume=True, check=True, verbosity=1):
        """data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        files = (('hyperalignment_tutorial_data.hdf5.gz',
                  'http://data.pymvpa.org/datasets/hyperalignment_tutorial_data/hyperalignment_tutorial_data_2.4.hdf5.gz',
                  {}),)
        out_files = self.fetcher.fetch(files, force=not resume, check=check, verbosity=verbosity)

        import os
        import sys
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        mvpa2_path = os.path.abspath(os.path.join(cur_dir, '..', '..', 'core', '_external', 'pymvpa'))
        sys.path = [mvpa2_path] + sys.path
        from mvpa2.base.hdf5 import h5load
        return h5load(out_files[0])
