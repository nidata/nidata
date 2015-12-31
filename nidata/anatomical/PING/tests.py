import os

import unittest
from nose.tools import assert_raises
from unittest import TestCase

from nidata.anatomical import PINGDataset
from nidata.core._utils.testing import (DownloadTestMixin, InstallTestMixin)


@unittest.skipIf(os.environ.get('NIDATA_PING_USERNAME') is None,
                 "Authentication required.")
class PINGDownloadTest(DownloadTestMixin, TestCase):
    dataset_class = PINGDataset


class PINGFailDownloadTest(unittest.TestCase):
    @unittest.skipIf(os.environ.get('NIDATA_PING_USERNAME') is not None,
                     "Authentication required.")
    def test_error(self):
        assert_raises(ValueError, PINGDataset)


class PINGDatasetWithDummyCredentials(PINGDataset):
    # For testing http dependency installation
    def __init__(self):
        super(PINGDatasetWithDummyCredentials, self).__init__(
            username='dummy', passwd='dummy')


class PINGInstallTest(InstallTestMixin, TestCase):
    dataset_class = PINGDatasetWithDummyCredentials
