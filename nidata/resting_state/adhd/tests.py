from nidata.resting_state import AdhdRestDataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class AdhdRestDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = AdhdRestDataset


class AdhdRestInstallTest(InstallTestMixin, TestCase):
    dataset_class = AdhdRestDataset
