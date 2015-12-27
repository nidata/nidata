from . import Yeo2011Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class Yeo2011Test(DownloadTestMixin, TestCase):
    dataset_class = Yeo2011Dataset
