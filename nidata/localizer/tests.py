"""
Test the datasets module
"""
# Author: Alexandre Abraham
# License: simplified BSD

import numpy as np

from nose import with_setup

from nidata._utils.compat import _basestring
from nidata._utils.testing import (mock_request, wrap_chunk_read_,
                                   assert_raises_regex)
from nidata.localizer import datasets
from nidata.tests.test_fetchers import (get_file_mock, setup_tmpdata, setup_mock,
                                        teardown_tmpdata, get_url_request,
                                        get_datadir, get_tmpdir)


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_localizer_contrasts():
    local_url = "file://" + get_datadir()
    ids = np.asarray([('S%2d' % i).encode() for i in range(94)])
    ids = ids.view(dtype=[('subject_id', 'S3')])
    get_file_mock().add_csv('cubicwebexport.csv', ids)
    get_file_mock().add_csv('cubicwebexport2.csv', ids)

    # Disabled: cannot be tested without actually fetching covariates CSV file
    # All subjects
    dataset = datasets.fetch_localizer_contrasts(["checkerboard"],
                                                 data_dir=get_tmpdir(),
                                                 url=local_url,
                                                 verbose=0)
    assert_true(dataset.anats is None)
    assert_true(dataset.tmaps is None)
    assert_true(dataset.masks is None)
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_equal(dataset.ext_vars.size, 94)
    assert_equal(len(dataset.cmaps), 94)

    # 20 subjects
    dataset = datasets.fetch_localizer_contrasts(["checkerboard"],
                                                 n_subjects=20,
                                                 data_dir=get_tmpdir(),
                                                 url=local_url,
                                                 verbose=0)
    assert_true(dataset.anats is None)
    assert_true(dataset.tmaps is None)
    assert_true(dataset.masks is None)
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_equal(len(dataset.cmaps), 20)
    assert_equal(dataset.ext_vars.size, 20)

    # Multiple contrasts
    dataset = datasets.fetch_localizer_contrasts(
        ["checkerboard", "horizontal checkerboard"],
        n_subjects=20, data_dir=get_tmpdir(),
        verbose=0)
    assert_true(dataset.anats is None)
    assert_true(dataset.tmaps is None)
    assert_true(dataset.masks is None)
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_equal(len(dataset.cmaps), 20 * 2)  # two contrasts are fetched
    assert_equal(dataset.ext_vars.size, 20)

    # get_anats=True
    dataset = datasets.fetch_localizer_contrasts(["checkerboard"],
                                                 data_dir=get_tmpdir(),
                                                 url=local_url,
                                                 get_anats=True,
                                                 verbose=0)
    assert_true(dataset.masks is None)
    assert_true(dataset.tmaps is None)
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.anats[0], _basestring))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_equal(dataset.ext_vars.size, 94)
    assert_equal(len(dataset.anats), 94)
    assert_equal(len(dataset.cmaps), 94)

    # get_masks=True
    dataset = datasets.fetch_localizer_contrasts(["checkerboard"],
                                                 data_dir=get_tmpdir(),
                                                 url=local_url,
                                                 get_masks=True,
                                                 verbose=0)
    assert_true(dataset.anats is None)
    assert_true(dataset.tmaps is None)
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_true(isinstance(dataset.masks[0], _basestring))
    assert_equal(dataset.ext_vars.size, 94)
    assert_equal(len(dataset.cmaps), 94)
    assert_equal(len(dataset.masks), 94)

    # get_tmaps=True
    dataset = datasets.fetch_localizer_contrasts(["checkerboard"],
                                                 data_dir=get_tmpdir(),
                                                 url=local_url,
                                                 get_tmaps=True,
                                                 verbose=0)
    assert_true(dataset.anats is None)
    assert_true(dataset.masks is None)
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_true(isinstance(dataset.tmaps[0], _basestring))
    assert_equal(dataset.ext_vars.size, 94)
    assert_equal(len(dataset.cmaps), 94)
    assert_equal(len(dataset.tmaps), 94)

    # all get_*=True
    dataset = datasets.fetch_localizer_contrasts(["checkerboard"],
                                                 data_dir=get_tmpdir(),
                                                 url=local_url,
                                                 get_anats=True,
                                                 get_masks=True,
                                                 get_tmaps=True,
                                                 verbose=0)

    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.anats[0], _basestring))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_true(isinstance(dataset.masks[0], _basestring))
    assert_true(isinstance(dataset.tmaps[0], _basestring))
    assert_equal(dataset.ext_vars.size, 94)
    assert_equal(len(dataset.anats), 94)
    assert_equal(len(dataset.cmaps), 94)
    assert_equal(len(dataset.masks), 94)
    assert_equal(len(dataset.tmaps), 94)


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_localizer_calculation_task():
    local_url = "file://" + get_datadir()
    ids = np.asarray(['S%2d' % i for i in range(94)])
    ids = ids.view(dtype=[('subject_id', 'S3')])
    get_file_mock().add_csv('cubicwebexport.csv', ids)
    get_file_mock().add_csv('cubicwebexport2.csv', ids)

    # Disabled: cannot be tested without actually fetching covariates CSV file
    # All subjects
    dataset = datasets.fetch_localizer_calculation_task(data_dir=get_tmpdir(),
                                                        url=local_url,
                                                        verbose=0)
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_equal(dataset.ext_vars.size, 94)
    assert_equal(len(dataset.cmaps), 94)

    # 20 subjects
    dataset = datasets.fetch_localizer_calculation_task(n_subjects=20,
                                                        data_dir=get_tmpdir(),
                                                        url=local_url,
                                                        verbose=0)
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.cmaps[0], _basestring))
    assert_equal(dataset.ext_vars.size, 20)
    assert_equal(len(dataset.cmaps), 20)

