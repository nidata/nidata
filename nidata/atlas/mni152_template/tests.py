from . import MNI152Dataset
from ...core._utils.testing import TestCaseWrapper


class MNI152Test(TestCaseWrapper.DownloadTest):
    dataset_class = MNI152Dataset
