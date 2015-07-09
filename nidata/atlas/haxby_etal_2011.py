from ..core.fetchers import HttpFetcher
from ..core.datasets import Dataset


class HaxbyEtal2011(Dataset):
    dependencies = ['pymvpa2']

    def __init__(self):
        """
        """
        self.fetcher = HttpFetcher()

    def fetch(self, n_subjects=1, force=False, check=True, verbosity=1):
        """data_types is a list, can contain: anat, diff, func, rest, psyc, bgnd
        """
        files = (('hyperalignment_tutorial_data.hdf5.gz', 'http://data.pymvpa.org/datasets/hyperalignment_tutorial_data/hyperalignment_tutorial_data.hdf5.gz', {}))
        out_files = self.fetcher.fetch(files, force=force, check=check, verbosity=verbosity)

        from mvpa2.suite import h5load
        return h5load(out_files[0])
