from . import HarvardOxfordDataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class HarvardOxfordTest(DownloadTestMixin, TestCase):
    dataset_class = HarvardOxfordDataset

    def fetch(self, *args, **kwargs):
        super(HarvardOxfordTest, self).fetch(
            atlas_name='cort-maxprob-thr0-1mm', *args, **kwargs)
