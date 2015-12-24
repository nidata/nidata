# *- encoding: utf-8 -*-
# Author: Ben Cipollini
# License: simplified BSD


from ...core.datasets import NilearnDataset


class AbidePcpDataset(NilearnDataset):
    fetcher_function = 'nilearn.datasets.fetch_abide_pcp'


def fetch_abide_pcp(data_dir=None, n_subjects=None, pipeline='cpac',
                    band_pass_filtering=False, global_signal_regression=False,
                    derivatives=['func_preproc'],
                    quality_checked=True, url=None, verbose=1, **kwargs):
    return AbidePcpDataset(data_dir=data_dir) \
        .fetch(n_subjects=n_subjects, pipeline=pipeline,
               band_pass_filtering=band_pass_filtering,
               global_signal_regression=global_signal_regression,
               derivatives=derivatives,
               quality_checked=quality_checked,
               url=url, verbose=verbose,
               **kwargs)
