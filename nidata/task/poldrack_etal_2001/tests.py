from unittest import TestCase
from nidata.task import PoldrackEtal2001Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class PoldrackTestDataset(PoldrackEtal2001Dataset):
    def fetch(self, *args, **kwargs):
        kwargs['preprocess_data'] = False
        kwargs['convert'] = False


class PoldrackEtal2001Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = PoldrackTestDataset
