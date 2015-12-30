from nose.tools import assert_true
from unittest import TestCase

from nidata.anatomical import OasisVbmDataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class OasisVbmTest(InstallThenDownloadTestMixin, TestCase):
    dataset_class = OasisVbmDataset

    def test_doc(self):
        # doc should exist after instance creation.
        OasisVbmDataset()
        assert_true(len(OasisVbmDataset.__doc__) > 100)
