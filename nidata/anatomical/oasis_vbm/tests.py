from . import OasisVbmDataset
from ...core._utils.testing import TestCaseWrapper


class OasisVbmTest(TestCaseWrapper.DownloadTest):
    dataset_class = OasisVbmDataset
