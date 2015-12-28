from unittest import TestCase

from nidata.task import Miyawaki2008Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class Miyawaki2008DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = Miyawaki2008Dataset


class Miyawaki2008InstallTest(InstallTestMixin, TestCase):
    dataset_class = Miyawaki2008Dataset
