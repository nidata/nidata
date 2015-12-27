from . import Power2011Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class Power2011Test(DownloadTestMixin, TestCase):
    dataset_class = Power2011Dataset
