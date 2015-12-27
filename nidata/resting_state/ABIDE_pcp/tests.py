from . import AbidePcpDataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class AbidePcpTest(DownloadTestMixin, TestCase):
    dataset_class = AbidePcpDataset
