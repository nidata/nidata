from unittest import TestCase

from nidata.atlas import Yeo2011Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class Yeo2011Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = Yeo2011Dataset
