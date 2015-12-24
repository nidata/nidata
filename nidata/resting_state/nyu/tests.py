from . import NyuRestDataset
from ...core._utils.testing import TestCaseWrapper


class NyuRestTest(TestCaseWrapper.DownloadTest):
    dataset_class = NyuRestDataset
