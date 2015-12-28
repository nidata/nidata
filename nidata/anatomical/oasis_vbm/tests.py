from unittest import TestCase
from nidata.anatomical import OasisVbmDataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class OasisVbmDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = OasisVbmDataset


class OasisVbmInstallTest(InstallTestMixin, TestCase):
    dataset_class = OasisVbmDataset
