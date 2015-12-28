from unittest import TestCase

from nidata.atlas import Craddock2012Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class Craddock2012Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = Craddock2012Dataset
