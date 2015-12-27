from . import OasisVbmDataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class OasisVbmTest(DownloadTestMixin, TestCase):
    dataset_class = OasisVbmDataset
