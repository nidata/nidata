from unittest import TestCase

from nidata.atlas import Smith2009Dataset
from nidata.core._utils.testing import InstallThenDownloadTestMixin


class Smith2009Test(InstallThenDownloadTestMixin, TestCase):
    dataset_class = Smith2009Dataset
