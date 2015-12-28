from unittest import TestCase
from nidata.atlas import Power2011Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class Power2011DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = Power2011Dataset


class Power2011InstallTest(InstallTestMixin, TestCase):
    dataset_class = Power2011Dataset
