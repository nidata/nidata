from . import NyuRestDataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class NyuRestTest(DownloadTestMixin, TestCase):
    dataset_class = NyuRestDataset
