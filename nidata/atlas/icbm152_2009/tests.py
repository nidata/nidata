from unittest import TestCase

from nidata.atlas import ICBM152Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class ICBM152Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = ICBM152Dataset
