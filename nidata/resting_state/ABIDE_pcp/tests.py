from unittest import TestCase
from nidata.resting_state import AbidePcpDataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class AbidePcpDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = AbidePcpDataset


class AbidePcpInstallTest(InstallTestMixin, TestCase):
    dataset_class = AbidePcpDataset
