from unittest import TestCase
from nidata.localizer import BrainomicsDataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class BrainomicsDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = BrainomicsDataset

    def fetch(self, contrasts=('checkerboard',), *args, **kwargs):
        super(BrainomicsDownloadTest, self).fetch(
            contrasts=contrasts, *args, **kwargs)


class BrainomicsTest(InstallTestMixin, TestCase):
    dataset_class = BrainomicsDataset
