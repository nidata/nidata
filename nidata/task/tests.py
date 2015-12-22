"""
Test the datasets module
"""
# Author: Alexandre Abraham
# License: simplified BSD

import os
import os.path as op
from nose import with_setup

from nidata.core import fetchers
from nidata.core._utils.compat import _basestring
from nidata.core._utils.testing import (assert_raises_regex)
from nidata.functional import datasets
from nidata.core.fetchers.tests.test_fetchers import (get_file_mock, setup_tmpdata, setup_mock,
                                        teardown_tmpdata, get_url_request,
                                        get_datadir, get_tmpdir)


@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_haxby_simple():
    local_url = "file://" + op.join(get_datadir(), "pymvpa-exampledata.tar.bz2")
    haxby = datasets.fetch_haxby_simple(data_dir=get_tmpdir(), url=local_url,
                                        verbose=0)
    datasetdir = op.join(get_tmpdir(), 'haxby2001_simple', 'pymvpa-exampledata')
    for key, file in [
            ('session_target', 'attributes.txt'),
            ('func', 'bold.nii.gz'),
            ('mask', 'mask.nii.gz'),
            ('conditions_target', 'attributes_literal.txt')]:
        assert_equal(haxby[key], op.join(datasetdir, file))
        assert_true(op.exists(op.join(datasetdir, file)))


@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fail_fetch_haxby_simple():
    # Test a dataset fetching failure to validate sandboxing
    local_url = "file://" + op.join(get_datadir(), "pymvpa-exampledata.tar.bz2")
    datasetdir = op.join(get_tmpdir(), 'haxby2001_simple', 'pymvpa-exampledata')
    os.makedirs(datasetdir)
    # Create a dummy file. If sandboxing is successful, it won't be overwritten
    dummy = open(op.join(datasetdir, 'attributes.txt'), 'w')
    dummy.write('stuff')
    dummy.close()

    path = 'pymvpa-exampledata'

    opts = {'uncompress': True}
    files = [
            (op.join(path, 'attributes.txt'), local_url, opts),
            # The following file does not exists. It will cause an abortion of
            # the fetching procedure
            (op.join(path, 'bald.nii.gz'), local_url, opts)
    ]

    assert_raises(IOError, fetchers.fetch_files,
            op.join(get_tmpdir(), 'haxby2001_simple'), files,
            verbose=0)
    dummy = open(op.join(datasetdir, 'attributes.txt'), 'r')
    stuff = dummy.read(5)
    dummy.close()
    assert_equal(stuff, 'stuff')


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_haxby():
    for i in range(1, 6):
        haxby = datasets.fetch_haxby(data_dir=get_tmpdir(), n_subjects=i,
                                     verbose=0)
        assert_equal(len(get_url_request().urls), 1 + (i == 1))  # subject_data + md5
        assert_equal(len(haxby.func), i)
        assert_equal(len(haxby.anat), i)
        assert_equal(len(haxby.session_target), i)
        assert_equal(len(haxby.mask_vt), i)
        assert_equal(len(haxby.mask_face), i)
        assert_equal(len(haxby.mask_house), i)
        assert_equal(len(haxby.mask_face_little), i)
        assert_equal(len(haxby.mask_house_little), i)
        get_url_request().reset()


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_miyawaki2008():
    dataset = datasets.fetch_miyawaki2008(data_dir=get_tmpdir(), verbose=0)
    assert_equal(len(dataset.func), 32)
    assert_equal(len(dataset.label), 32)
    assert_true(isinstance(dataset.mask, _basestring))
    assert_equal(len(dataset.mask_roi), 38)
    assert_equal(len(get_url_request().urls), 1)

