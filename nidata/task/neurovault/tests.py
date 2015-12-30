from unittest import TestCase

from nidata.task import NeuroVaultDataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class Miyawaki2008Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = NeuroVaultDataset
