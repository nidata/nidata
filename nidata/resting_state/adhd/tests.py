from unittest import TestCase

from nidata.resting_state import AdhdRestDataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class AdhdRestTest(InstallThenDownloadTestMixin, TestCase):
    dataset_class = AdhdRestDataset
