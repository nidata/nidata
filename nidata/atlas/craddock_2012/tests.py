from unittest import TestCase
from nidata.atlas import Craddock2012Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class Craddock2012DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = Craddock2012Dataset


class Craddock2012InstallTest(InstallTestMixin, TestCase):
    dataset_class = Craddock2012Dataset
