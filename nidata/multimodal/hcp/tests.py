import os

import unittest
from nose.tools import assert_raises

from . import HcpDataset
from ...core._utils.testing import TestCaseWrapper


@unittest.skipIf(os.environ.get('NIDATA_HCP_USERNAME') is None,
                 "Authentication required.")
class HcpTest(TestCaseWrapper.DownloadTest):
    dataset_class = HcpDataset


class HcpFailTest(unittest.TestCase):
    @unittest.skipIf(os.environ.get('NIDATA_HCP_USERNAME') is not None,
                     "Authentication required.")
    def test_error(self):
        assert_raises(ValueError, HcpDataset, fetcher_type='http')
