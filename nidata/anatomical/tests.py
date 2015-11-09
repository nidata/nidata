"""
Test the datasets module
"""
# Author: Alexandre Abraham
# License: simplified BSD

import numpy as np

from nose import with_setup

from nidata.core import fetchers
from nidata.core._utils.testing import (assert_raises_regex)
from nidata.core._utils.compat import _basestring
from nidata.anatomical import datasets
from nidata.core.fetchers.tests.test_fetchers import (get_file_mock, setup_tmpdata, setup_mock,
                                        teardown_tmpdata, get_url_request,
                                        get_datadir, get_tmpdir)


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_oasis_vbm():
    local_url = "file://" + get_datadir()
    ids = np.asarray(['OAS1_%4d' % i for i in range(457)])
    ids = ids.view(dtype=[('ID', 'S9')])
    get_file_mock().add_csv('oasis_cross-sectional.csv', ids)

    # Disabled: cannot be tested without actually fetching covariates CSV file
    dataset = datasets.fetch_oasis_vbm(data_dir=get_tmpdir(), url=local_url,
                                       verbose=0)
    assert_equal(len(dataset.gray_matter_maps), 403)
    assert_equal(len(dataset.white_matter_maps), 403)
    assert_true(isinstance(dataset.gray_matter_maps[0], _basestring))
    assert_true(isinstance(dataset.white_matter_maps[0], _basestring))
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.data_usage_agreement, _basestring))
    assert_equal(len(get_url_request().urls), 3)

    dataset = datasets.fetch_oasis_vbm(data_dir=get_tmpdir(), url=local_url,
                                       dartel_version=False, verbose=0)
    assert_equal(len(dataset.gray_matter_maps), 415)
    assert_equal(len(dataset.white_matter_maps), 415)
    assert_true(isinstance(dataset.gray_matter_maps[0], _basestring))
    assert_true(isinstance(dataset.white_matter_maps[0], _basestring))
    assert_true(isinstance(dataset.ext_vars, np.recarray))
    assert_true(isinstance(dataset.data_usage_agreement, _basestring))
    assert_equal(len(get_url_request().urls), 4)
