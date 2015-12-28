from unittest import TestCase
from nidata.atlas import Yeo2011Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class Yeo2011DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = Yeo2011Dataset


class Yeo2011InstallTest(InstallTestMixin, TestCase):
    dataset_class = Yeo2011Dataset
