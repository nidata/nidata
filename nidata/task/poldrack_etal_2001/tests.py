from . import PoldrackEtal2001Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class PoldrackEtal2001Test(DownloadTestMixin, TestCase):
    dataset_class = PoldrackEtal2001Dataset
