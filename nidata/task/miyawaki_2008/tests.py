from . import Miyawaki2008Dataset
from ...core._utils.testing import TestCaseWrapper


class Miyawaki2008Test(TestCaseWrapper.DownloadTest):
    dataset_class = Miyawaki2008Dataset
