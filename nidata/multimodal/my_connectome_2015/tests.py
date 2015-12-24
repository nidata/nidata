from . import MyConnectome2015Dataset
from ...core._utils.testing import TestCaseWrapper


class MyConnectome2015Test(TestCaseWrapper.DownloadTest):
    dataset_class = MyConnectome2015Dataset
