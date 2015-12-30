from unittest import TestCase

from nidata.task import Haxby2001Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class Haxby2001Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = Haxby2001Dataset
