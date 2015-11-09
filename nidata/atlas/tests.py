"""
Test the datasets module
"""
# Author: Alexandre Abraham
# License: simplified BSD

import os
import numpy as np

import nibabel
from nose import with_setup

from nidata.core._utils.compat import _basestring
from nidata.core._utils.testing import assert_raises_regex
from nidata.atlas import datasets
from nidata.core.fetchers.tests.test_fetchers import (get_file_mock, setup_tmpdata, setup_mock,
                                        teardown_tmpdata, get_url_request,
                                        get_tmpdir)


@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fail_fetch_harvard_oxford():
    # specify non-existing atlas item
    assert_raises_regex(ValueError, 'Invalid atlas name',
                        datasets.fetch_harvard_oxford, 'not_inside')

    # specify existing atlas item
    target_atlas = 'cort-maxprob-thr0-1mm'
    target_atlas_fname = 'HarvardOxford-' + target_atlas + '.nii.gz'

    HO_dir = os.path.join(get_tmpdir(), 'harvard_oxford')
    os.mkdir(HO_dir)
    nifti_dir = os.path.join(HO_dir, 'HarvardOxford')
    os.mkdir(nifti_dir)

    target_atlas_nii = os.path.join(nifti_dir, target_atlas_fname)
    datasets.load_mni152_template().to_filename(target_atlas_nii)

    dummy = open(os.path.join(HO_dir, 'HarvardOxford-Cortical.xml'), 'w')
    dummy.write("<?xml version='1.0' encoding='us-ascii'?> "
                "<metadata>"
                "</metadata>")
    dummy.close()

    out_nii, arr = datasets.fetch_harvard_oxford(target_atlas, data_dir=get_tmpdir())

    assert_true(isinstance(nibabel.load(out_nii), nibabel.Nifti1Image))
    assert_true(isinstance(arr, np.ndarray))
    assert_true(len(arr) > 0)


# Smoke tests for the rest of the fetchers


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_craddock_2012_atlas():
    bunch = datasets.fetch_craddock_2012_atlas(data_dir=get_tmpdir(), verbose=0)

    keys = ("scorr_mean", "tcorr_mean",
            "scorr_2level", "tcorr_2level",
            "random")
    filenames = [
            "scorr05_mean_all.nii.gz",
            "tcorr05_mean_all.nii.gz",
            "scorr05_2level_all.nii.gz",
            "tcorr05_2level_all.nii.gz",
            "random_all.nii.gz",
    ]
    assert_equal(len(get_url_request().urls), 1)
    for key, fn in zip(keys, filenames):
        assert_equal(bunch[key], os.path.join(get_tmpdir(), 'craddock_2012', fn))


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_smith_2009_atlas():
    bunch = datasets.fetch_smith_2009(data_dir=get_tmpdir(), verbose=0)

    keys = ("rsn20", "rsn10", "rsn70",
            "bm20", "bm10", "bm70")
    filenames = [
            "rsn20.nii.gz",
            "PNAS_Smith09_rsn10.nii.gz",
            "rsn70.nii.gz",
            "bm20.nii.gz",
            "PNAS_Smith09_bm10.nii.gz",
            "bm70.nii.gz",
    ]

    assert_equal(len(get_url_request().urls), 6)
    for key, fn in zip(keys, filenames):
        assert_equal(bunch[key], os.path.join(get_tmpdir(), 'smith_2009', fn))


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_msdl_atlas():
    dataset = datasets.fetch_msdl_atlas(data_dir=get_tmpdir(), verbose=0)
    assert_true(isinstance(dataset.labels, _basestring))
    assert_true(isinstance(dataset.maps, _basestring))
    assert_equal(len(get_url_request().urls), 1)


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_icbm152_2009():
    dataset = datasets.fetch_icbm152_2009(data_dir=get_tmpdir(), verbose=0)
    assert_true(isinstance(dataset.csf, _basestring))
    assert_true(isinstance(dataset.eye_mask, _basestring))
    assert_true(isinstance(dataset.face_mask, _basestring))
    assert_true(isinstance(dataset.gm, _basestring))
    assert_true(isinstance(dataset.mask, _basestring))
    assert_true(isinstance(dataset.pd, _basestring))
    assert_true(isinstance(dataset.t1, _basestring))
    assert_true(isinstance(dataset.t2, _basestring))
    assert_true(isinstance(dataset.t2_relax, _basestring))
    assert_true(isinstance(dataset.wm, _basestring))
    assert_equal(len(get_url_request().urls), 1)


@with_setup(setup_mock)
@with_setup(setup_tmpdata, teardown_tmpdata)
def test_fetch_yeo_2011_atlas():
    dataset = datasets.fetch_yeo_2011_atlas(data_dir=get_tmpdir(), verbose=0)
    assert_true(isinstance(dataset.anat, _basestring))
    assert_true(isinstance(dataset.colors_17, _basestring))
    assert_true(isinstance(dataset.colors_7, _basestring))
    assert_true(isinstance(dataset.thick_17, _basestring))
    assert_true(isinstance(dataset.thick_7, _basestring))
    assert_true(isinstance(dataset.thin_17, _basestring))
    assert_true(isinstance(dataset.thin_7, _basestring))
    assert_equal(len(get_url_request().urls), 1)


def test_load_mni152_template():
    # All subjects
    template_nii = datasets.load_mni152_template()
    assert_equal(template_nii.shape, (91, 109, 91))
    assert_equal(template_nii.get_header().get_zooms(), (2.0, 2.0, 2.0))

