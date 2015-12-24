from . import Power2011Dataset
from ...core._utils.testing import TestCaseWrapper


class Power2011Test(TestCaseWrapper.DownloadTest):
    dataset_class = Power2011Dataset
