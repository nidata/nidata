# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD

from ...core.datasets import NilearnDataset


class BrainomicsDataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_localizer_contrasts'


def fetch_localizer_calculation_task(n_subjects=None, data_dir=None, url=None,
                                     verbose=1):
    """Fetch calculation task contrast maps from the localizer.

    This function is only a caller for the fetch_localizer_contrasts in order
    to simplify examples reading and understanding.
    The 'calculation (auditory and visual cue)' contrast is used.

    Parameters
    ----------
    n_subjects: int, optional
        The number of subjects to load. If None is given,
        all 94 subjects are used.

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location.

    url: string, optional
        Override download URL. Used for test only (or if you setup a mirror of
        the data).

    verbose: int, optional
        verbose level (0 means no message).

    Returns
    -------
    data: dict
        Dictionary-like object, the interest attributes are :
        'cmaps': string list
            Paths to nifti contrast maps

    """
    data = fetch_localizer_contrasts(["calculation (auditory and visual cue)"],
                                     n_subjects=n_subjects,
                                     get_tmaps=False, get_masks=False,
                                     get_anats=False, data_dir=data_dir,
                                     url=url, resume=True, verbose=verbose)
    data.pop('tmaps')
    data.pop('masks')
    data.pop('anats')
    return data


def fetch_localizer_contrasts(contrasts, n_subjects=None, get_tmaps=False,
                              get_masks=False, get_anats=False,
                              data_dir=None, url=None, resume=True, verbose=1):
    return BrainomicsDataset(data_dir=data_dir).fetch(contrasts=contrasts,
                                                      n_subjects=n_subjects,
                                                      get_tmaps=get_tmaps,
                                                      get_masks=get_masks,
                                                      get_anats=get_anats,
                                                      url=url,
                                                      resume=resume,
                                                      verbose=verbose)
