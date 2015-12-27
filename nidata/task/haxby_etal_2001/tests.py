from . import Haxby2001Dataset
from unittest import TestCase
from nidata.core._utils.testing import DownloadTestMixin


class Haxby2001Test(DownloadTestMixin, TestCase):
    dataset_class = Haxby2001Dataset
