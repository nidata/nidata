from unittest import TestCase

from nidata.task import Miyawaki2008Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class Miyawaki2008Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = Miyawaki2008Dataset
