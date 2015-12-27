from . import ICBM152Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class ICBM152Test(DownloadTestMixin, TestCase):
    dataset_class = ICBM152Dataset
