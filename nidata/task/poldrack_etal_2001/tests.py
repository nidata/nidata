from unittest import TestCase
from nidata.task import PoldrackEtal2001Dataset
from nidata.core._utils.testing import DownloadTestMixin  # , InstallTestMixin


class PoldrackEtal2001DownloadTest(DownloadTestMixin, TestCase):
    dataset_class = PoldrackEtal2001Dataset

# Super-dependencies, so skip it for now.
# class PoldrackEtal2001InstallTest(InstallTestMixin, TestCase):
#     dataset_class = PoldrackEtal2001Dataset
