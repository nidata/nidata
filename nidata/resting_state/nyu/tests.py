from unittest import TestCase
from nidata.resting_state import NyuRestDataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class NyuRestDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = NyuRestDataset


class NyuRestInstallTest(InstallTestMixin, TestCase):
    dataset_class = NyuRestDataset
