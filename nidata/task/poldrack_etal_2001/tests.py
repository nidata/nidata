from . import PoldrackEtal2001Dataset
from ...core._utils.testing import TestCaseWrapper


class PoldrackEtal2001Test(TestCaseWrapper.DownloadTest):
    dataset_class = PoldrackEtal2001Dataset
