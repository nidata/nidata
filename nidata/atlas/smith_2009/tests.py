from . import Smith2009Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class Smith2009Test(DownloadTestMixin, TestCase):
    dataset_class = Smith2009Dataset
