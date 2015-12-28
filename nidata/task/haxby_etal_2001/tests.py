from unittest import TestCase
from nidata.task import Haxby2001Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class Haxby2001DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = Haxby2001Dataset


class Haxby2001InstallTest(InstallTestMixin, TestCase):
    dataset_class = Haxby2001Dataset
