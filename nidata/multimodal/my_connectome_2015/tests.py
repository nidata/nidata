from unittest import TestCase

from nidata.multimodal import MyConnectome2015Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class MyConnectome2015Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = MyConnectome2015Dataset
