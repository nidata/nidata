from . import Craddock2012Dataset
from ...core._utils.testing import TestCaseWrapper


class Craddock2012VbmTest(TestCaseWrapper.DownloadTest):
    dataset_class = Craddock2012Dataset
