import sys

import unittest

from . import HaxbyEtal2011Dataset
from ...core._utils.testing import TestCaseWrapper


@unittest.skipIf(sys.version_info[0] > 2, "pymvpa does not support Python 3")
class HaxbyEtal2011Test(TestCaseWrapper.DownloadTest):
    dataset_class = HaxbyEtal2011Dataset
