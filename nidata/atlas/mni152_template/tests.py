from unittest import TestCase

from nidata.atlas import MNI152Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class MNI152Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = MNI152Dataset
