from unittest import TestCase

from nidata.task import NeuroVaultDataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class NeuroVaultDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = NeuroVaultDataset


class NeuroVaultInstallTest(InstallTestMixin, TestCase):
    dataset_class = NeuroVaultDataset
