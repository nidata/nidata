# *- encoding: utf-8 -*-
"""
Utilities to download NeuroImaging-based atlases
"""
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

from ...core.datasets import HttpDataset


class MNI152Dataset(HttpDataset):
    """Load skullstripped 2mm version of the MNI152 originally distributed
    with FSL

    Returns
    -------
    mni152_template: nibabel object corresponding to the template


    References
    ----------

    VS Fonov, AC Evans, K Botteron, CR Almli, RC McKinstry, DL Collins and
    BDCG, Unbiased average age-appropriate atlases for pediatric studies,
    NeuroImage, Volume 54, Issue 1, January 2011, ISSN 1053–8119, DOI:
    10.1016/j.neuroimage.2010.07.033

    VS Fonov, AC Evans, RC McKinstry, CR Almli and DL Collins, Unbiased
    nonlinear average age-appropriate brain templates from birth to adulthood,
    NeuroImage, Volume 47, Supplement 1, July 2009, Page S102 Organization for
    Human Brain Mapping 2009 Annual Meeting, DOI: 10.1016/S1053-8119(09)70884-5

    """
    def fetch(self, url=None, resume=True, verbose=1):
        files = (('avg152T1_brain.nii.gz',
                  'https://raw.githubusercontent.com/nilearn/nilearn/master/nilearn/data/avg152T1_brain.nii.gz',
                  {}),)
        return self.fetcher.fetch(files=files, force=not resume, verbose=verbose)


def fetch_mni152_template(data_dir=None, url=None, resume=True, verbose=1):
    return MNI152Dataset(data_dir=data_dir).fetch(url=url, resume=resume, verbose=verbose)
