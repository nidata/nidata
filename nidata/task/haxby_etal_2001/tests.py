from . import Haxby2001Dataset
from ...core._utils.testing import TestCaseWrapper


class Haxby2001Test(TestCaseWrapper.DownloadTest):
    dataset_class = Haxby2001Dataset
