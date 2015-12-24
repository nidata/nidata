from . import ICBM152Dataset
from ...core._utils.testing import TestCaseWrapper


class ICBM152Test(TestCaseWrapper.DownloadTest):
    dataset_class = ICBM152Dataset
