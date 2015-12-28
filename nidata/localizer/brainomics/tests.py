from unittest import TestCase

from nidata.localizer import BrainomicsDataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class BrainomicsTest(InstallThenDownloadTestMixin, TestCase):
    dataset_class = BrainomicsDataset

    def fetch(self, contrasts=('checkerboard',), *args, **kwargs):
        super(BrainomicsTest, self).fetch(
            contrasts=contrasts, *args, **kwargs)
