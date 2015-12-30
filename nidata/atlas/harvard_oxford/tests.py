from unittest import TestCase

from nidata.atlas import HarvardOxfordDataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class HarvardOxfordTest(InstallThenDownloadTestMixin, TestCase):
    dataset_class = HarvardOxfordDataset

    def fetch(self, atlas_name='cort-maxprob-thr0-1mm', *args, **kwargs):
        super(HarvardOxfordTest, self).fetch(
            atlas_name=atlas_name, *args, **kwargs)
