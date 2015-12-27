from . import AdhdRestDataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class AdhdRestTest(DownloadTestMixin, TestCase):
    dataset_class = AdhdRestDataset
