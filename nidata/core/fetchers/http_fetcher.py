"""
"""

import os
import time
import warnings
from functools import partial

import nibabel as nib
import numpy as np

from .base import fetch_files, Fetcher


class HttpFetcher(Fetcher):
    dependencies = ['requests']

    def fetch(self, files, force=False, resume=True, check=False, verbose=1):
        files = Fetcher.reformat_files(files)  # allows flexibility

        return fetch_files(self.data_dir, files, resume=not force, verbose=verbose)
