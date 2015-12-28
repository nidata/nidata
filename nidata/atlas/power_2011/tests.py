from unittest import TestCase

from nidata.atlas import Power2011Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class Power2011Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = Power2011Dataset
