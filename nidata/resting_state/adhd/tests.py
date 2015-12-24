from . import AdhdRestDataset
from ...core._utils.testing import TestCaseWrapper


class AdhdRestTest(TestCaseWrapper.DownloadTest):
    dataset_class = AdhdRestDataset
