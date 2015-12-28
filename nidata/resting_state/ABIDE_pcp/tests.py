from unittest import TestCase

from nidata.resting_state import AbidePcpDataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class AbidePcpTest(InstallThenDownloadTestMixin, TestCase):
    dataset_class = AbidePcpDataset
