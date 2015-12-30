from unittest import TestCase

from nidata.resting_state import NyuRestDataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class NyuRestTest(InstallThenDownloadTestMixin, TestCase):
    dataset_class = NyuRestDataset
