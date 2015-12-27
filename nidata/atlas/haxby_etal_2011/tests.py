import sys

import unittest

from . import HaxbyEtal2011Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


@unittest.skipIf(sys.version_info[0] > 2, "pymvpa does not support Python 3")
class HaxbyEtal2011Test(DownloadTestMixin, TestCase):
    dataset_class = HaxbyEtal2011Dataset
