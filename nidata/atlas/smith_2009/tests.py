from . import Smith2009Dataset
from ...core._utils.testing import TestCaseWrapper


class Smith2009Test(TestCaseWrapper.DownloadTest):
    dataset_class = Smith2009Dataset
