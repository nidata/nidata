# *- encoding: utf-8 -*-
"""
Utilities to download NeuroImaging-based atlases
"""
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import numpy as np
from sklearn.datasets.base import Bunch

from ...core.datasets import HttpDataset


class Power2011Dataset(HttpDataset):
    """Download and load the Power et al. brain atlas composed of 264 ROIs.
    Returns
    -------
    data: sklearn.datasets.base.Bunch
        dictionary-like object, contains:
        - "rois": coordinates of 264 ROIs in MNI space
    References
    ----------
    Power, Jonathan D., et al. "Functional network organization of the human
    brain." Neuron 72.4 (2011): 665-678.
    """
    def fetch(self, resume=True, verbose=1):
        files = (('power_2011.csv',
                  'https://raw.githubusercontent.com/nilearn/nilearn/master/nilearn/data/power_2011.csv',
                  {}),)
        files = self.fetcher.fetch(files=files, force=not resume, verbose=verbose)
        return Bunch(rois=np.recfromcsv(files[0]))


def fetch_power_2011(data_dir=None, resume=True, verbose=False):
    return Power2011Dataset(data_dir=data_dir).fetch(resume=resume, verbose=verbose)
