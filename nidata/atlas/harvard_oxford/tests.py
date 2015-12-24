from . import HarvardOxfordDataset
from ...core._utils.testing import TestCaseWrapper


class HarvardOxfordTest(TestCaseWrapper.DownloadTest):
    dataset_class = HarvardOxfordDataset

    def fetch(self, *args, **kwargs):
        super(HarvardOxfordTest, self).fetch(
            atlas_name='cort-maxprob-thr0-1mm', *args, **kwargs)
