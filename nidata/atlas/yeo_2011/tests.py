from . import Yeo2011Dataset
from ...core._utils.testing import TestCaseWrapper


class Yeo2011Test(TestCaseWrapper.DownloadTest):
    dataset_class = Yeo2011Dataset
