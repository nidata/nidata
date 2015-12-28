from unittest import TestCase
from nidata.multimodal import MyConnectome2015Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class MyConnectomeDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = MyConnectome2015Dataset


class MyConnectomeInstallTest(InstallTestMixin, TestCase):
    dataset_class = MyConnectome2015Dataset
