from . import OasisVbmDataset
from ...core._utils.testing import DownloadTest


class OasisVbmTest(DownloadTest):
    dataset_class = OasisVbmDataset
