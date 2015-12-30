from unittest import TestCase, skipIf
from nidata.task import PoldrackEtal2001Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class PoldrackTestDataset(PoldrackEtal2001Dataset):
    def fetch(self, *args, **kwargs):
        kwargs['preprocess_data'] = False
        kwargs['convert'] = False


@skipIf(True, 'test')
class PoldrackEtal2001Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = PoldrackTestDataset
