from . import MyConnectome2015Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class MyConnectome2015Test(DownloadTestMixin, TestCase):
    dataset_class = MyConnectome2015Dataset
