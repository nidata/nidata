import os

import unittest
from nose.tools import assert_raises
from unittest import TestCase

from nidata.multimodal import HcpDataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


@unittest.skipIf(os.environ.get('NIDATA_HCP_USERNAME') is None,
                 "Authentication required.")
class HcpDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = HcpDataset


class HcpFailDownloadTest(unittest.TestCase):
    @unittest.skipIf(os.environ.get('NIDATA_HCP_USERNAME') is not None,
                     "Authentication required.")
    def test_error(self):
        assert_raises(ValueError, HcpDataset, fetcher_type='http')


class HcpInstallTest(InstallTestMixin, TestCase):
    dataset_class = HcpDataset
