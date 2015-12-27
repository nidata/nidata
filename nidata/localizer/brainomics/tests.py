from . import BrainomicsDataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class BrainomicsTest(DownloadTestMixin, TestCase):
    dataset_class = BrainomicsDataset

    def fetch(self, *args, **kwargs):
        super(BrainomicsTest, self).fetch(contrasts=['checkerboard'],
                                          *args, **kwargs)
