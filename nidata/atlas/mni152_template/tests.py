from . import MNI152Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class MNI152Test(DownloadTestMixin, TestCase):
    dataset_class = MNI152Dataset
