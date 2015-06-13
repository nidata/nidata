"""
Test the datasets module
"""
# Author: Alexandre Abraham
# License: simplified BSD

import numpy as np

from nose import with_setup

from nidata.resting_state import datasets
from nidata.tests.test_fetchers import (get_file_mock, setup_tmpdata, setup_mock,
                                        teardown_tmpdata, get_url_request,
                                        get_datadir, get_tmpdir)


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_nyu_rest():
    # First session, all subjects
    nyu = datasets.fetch_nyu_rest(data_dir=get_tmpdir(), verbose=0)
    assert_equal(len(get_url_request().urls), 2)
    assert_equal(len(nyu.func), 25)
    assert_equal(len(nyu.anat_anon), 25)
    assert_equal(len(nyu.anat_skull), 25)
    assert_true(np.all(np.asarray(nyu.session) == 1))

    # All sessions, 12 subjects
    get_url_request().reset()
    nyu = datasets.fetch_nyu_rest(data_dir=get_tmpdir(), sessions=[1, 2, 3],
                                  n_subjects=12, verbose=0)
    # Session 1 has already been downloaded
    assert_equal(len(get_url_request().urls), 2)
    assert_equal(len(nyu.func), 36)
    assert_equal(len(nyu.anat_anon), 36)
    assert_equal(len(nyu.anat_skull), 36)
    s = np.asarray(nyu.session)
    assert_true(np.all(s[:12] == 1))
    assert_true(np.all(s[12:24] == 2))
    assert_true(np.all(s[24:] == 3))


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_adhd():
    local_url = "file://" + get_datadir()

    sub1 = [3902469, 7774305, 3699991]
    sub2 = [2014113, 4275075, 1019436,
            3154996, 3884955,   27034,
            4134561,   27018, 6115230,
              27037, 8409791,   27011]
    sub3 = [3007585, 8697774, 9750701,
              10064,   21019,   10042,
              10128, 2497695, 4164316,
            1552181, 4046678,   23012]
    sub4 = [1679142, 1206380,   23008,
            4016887, 1418396, 2950754,
            3994098, 3520880, 1517058,
            9744150, 1562298, 3205761, 3624598]
    subs = np.asarray(sub1 + sub2 + sub3 + sub4)
    subs = subs.view(dtype=[('Subject', '<i8')])
    get_file_mock().add_csv('ADHD200_40subs_motion_parameters_and_phenotypics.csv',
                      subs)

    adhd = datasets.fetch_adhd(data_dir=get_tmpdir(), url=local_url,
                               n_subjects=12, verbose=0)
    assert_equal(len(adhd.func), 12)
    assert_equal(len(adhd.confounds), 12)
    assert_equal(len(get_url_request().urls), 2)


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_abide_pcp():
    local_url = "file://" + get_datadir()
    ids = [('50%03d' % i).encode() for i in range(800)]
    filenames = ['no_filename'] * 800
    filenames[::2] = ['filename'] * 400
    pheno = np.asarray(list(zip(ids, filenames)), dtype=[('subject_id', int),
                                                         ('FILE_ID', 'U11')])
    # pheno = pheno.T.view()
    get_file_mock().add_csv('Phenotypic_V1_0b_preprocessed1.csv', pheno)

    # All subjects
    dataset = datasets.fetch_abide_pcp(data_dir=get_tmpdir(), url=local_url,
                                       quality_checked=False, verbose=0)
    assert_equal(len(dataset.func_preproc), 400)

