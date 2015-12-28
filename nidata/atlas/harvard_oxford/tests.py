from unittest import TestCase
from nidata.atlas import HarvardOxfordDataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class HarvardOxfordDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = HarvardOxfordDataset

    def fetch(self, atlas_name='cort-maxprob-thr0-1mm', *args, **kwargs):
        super(HarvardOxfordDownloadTest, self).fetch(
            atlas_name=atlas_name, *args, **kwargs)


class HarvardOxfordInstallTest(InstallTestMixin, TestCase):
    dataset_class = HarvardOxfordDataset
