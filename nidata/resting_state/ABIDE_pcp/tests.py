from . import AbidePcpDataset
from ...core._utils.testing import TestCaseWrapper


class AbidePcpTest(TestCaseWrapper.DownloadTest):
    dataset_class = AbidePcpDataset
