from unittest import TestCase
from nidata.atlas import Smith2009Dataset
from nidata.core._utils.testing import DownloadTestMixin, InstallTestMixin


class Smith2009DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = Smith2009Dataset


class Smith2009InstallTest(InstallTestMixin, TestCase):
    dataset_class = Smith2009Dataset
