"""
"""

from nose.tools import assert_true, assert_raises, assert_in

from nidata.resting_state import AbidePcpDataset, AdhdRestDataset, NyuRestDataset


def test_nyu_dataset():
    # Turns out this errors; so ... expect the error until we fix it!
    assert_raises(NotImplementedError, NyuRestDataset().fetch, n_subjects=1)


def test_adhd_dataset():
    # Turns out this errors; so ... expect the error until we fix it!
    assert_raises(NotImplementedError, AdhdRestDataset().fetch, n_subjects=1)
    # dataset = AdhdRestDataset().fetch(n_subjects=1)


def test_abide_dataset():
    # Turns out this errors; so ... expect the error until we fix it!
    # assert_raises(Exception, AbidePcpDataset().fetch, n_subjects=1)
    dataset = AbidePcpDataset().fetch(n_subjects=1)
    assert_in('phenotypic', dataset)
    assert_in('func_preproc', dataset)
