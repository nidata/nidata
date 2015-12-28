from unittest import TestCase
from nidata.atlas import MNI152Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class MNI152DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = MNI152Dataset


class MNI152InstallTest(InstallTestMixin, TestCase):
    dataset_class = MNI152Dataset
