from . import BrainomicsDataset
from ...core._utils.testing import TestCaseWrapper


class BrainomicsTest(TestCaseWrapper.DownloadTest):
    dataset_class = BrainomicsDataset

    def fetch(self, *args, **kwargs):
        super(BrainomicsTest, self).fetch(contrasts=['checkerboard'],
                                          *args, **kwargs)
