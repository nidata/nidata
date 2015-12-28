from unittest import TestCase
from nidata.atlas import ICBM152Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class ICBM152DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = ICBM152Dataset


class ICBM152InstallTest(InstallTestMixin, TestCase):
    dataset_class = ICBM152Dataset
