from . import HaxbyEtal2011Dataset
from ...core._utils.testing import TestCaseWrapper


class HaxbyEtal2011Test(TestCaseWrapper.DownloadTest):
    dataset_class = HaxbyEtal2011Dataset
