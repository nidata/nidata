from . import Craddock2012Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class Craddock2012VbmTest(DownloadTestMixin, TestCase):
    dataset_class = Craddock2012Dataset
