# *- encoding: utf-8 -*-
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD


from ...core.datasets import HttpDataset


class Smith2009Dataset(HttpDataset):

    """Download and load the Smith ICA and BrainMap atlas (dated 2009)

    Parameters
    ----------
    data_dir: string, optional
        Path of the data directory. Use to forec data storage in a non-
        standard location. Default: None (meaning: default)
    url: string, optional
        Download URL of the dataset. Overwrite the default URL.

    Returns
    -------
    data: dict
        dictionary-like object, contains:
        - 20-dimensional ICA, Resting-FMRI components:
            - all 20 components (rsn20)
            - 10 well-matched maps from these, as shown in PNAS paper (rsn10)

        - 20-dimensional ICA, BrainMap components:
            - all 20 components (bm20)
            - 10 well-matched maps from these, as shown in PNAS paper (bm10)

        - 70-dimensional ICA, Resting-FMRI components (rsn70)

        - 70-dimensional ICA, BrainMap components (bm70)


    References
    ----------

    S.M. Smith, P.T. Fox, K.L. Miller, D.C. Glahn, P.M. Fox, C.E. Mackay, N.
    Filippini, K.E. Watkins, R. Toro, A.R. Laird, and C.F. Beckmann.
    Correspondence of the brain's functional architecture during activation and
    rest. Proc Natl Acad Sci USA (PNAS), 106(31):13040-13045, 2009.

    A.R. Laird, P.M. Fox, S.B. Eickhoff, J.A. Turner, K.L. Ray, D.R. McKay, D.C
    Glahn, C.F. Beckmann, S.M. Smith, and P.T. Fox. Behavioral interpretations
    of intrinsic connectivity networks. Journal of Cognitive Neuroscience, 2011

    Notes
    -----
    For more information about this dataset's structure:
    http://www.fmrib.ox.ac.uk/analysis/brainmap+rsns/
    """
    def fetch(self, url=None, resume=True, verbose=1):
        if url is None:
            url = "http://www.fmrib.ox.ac.uk/analysis/brainmap+rsns/"

        files = [('rsn20.nii.gz', url + 'rsn20.nii.gz', {}),
                 ('PNAS_Smith09_rsn10.nii.gz',
                     url + 'PNAS_Smith09_rsn10.nii.gz', {}),
                 ('rsn70.nii.gz', url + 'rsn70.nii.gz', {}),
                 ('bm20.nii.gz', url + 'bm20.nii.gz', {}),
                 ('PNAS_Smith09_bm10.nii.gz',
                     url + 'PNAS_Smith09_bm10.nii.gz', {}),
                 ('bm70.nii.gz', url + 'bm70.nii.gz', {}),
                 ]

        files_ = self.fetcher.fetch(files, force=not resume,
                                    verbose=verbose)

        keys = ['rsn20', 'rsn10', 'rsn70', 'bm20', 'bm10', 'bm70']
        params = dict(zip(keys, files_))

        return dict(**params)


def fetch_smith_2009(data_dir=None, url=None, resume=True, verbose=1):
    return Smith2009Dataset(data_dir=data_dir) \
        .fetch(url=url, resume=resume, verbose=verbose)
