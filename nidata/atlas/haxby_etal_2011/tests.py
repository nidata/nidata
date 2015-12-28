import sys

import unittest
from unittest import TestCase

from nidata.atlas import HaxbyEtal2011Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


@unittest.skipIf(sys.version_info[0] > 1, "pymvpa does not support Python 3")
class HaxbyEtal2011DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = HaxbyEtal2011Dataset


@unittest.skipIf(sys.version_info[0] > 1, "pymvpa does not support Python 3")
class HaxbyEtal2011InstallTest(InstallTestMixin, TestCase):
    dataset_class = HaxbyEtal2011Dataset
