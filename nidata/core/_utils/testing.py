"""Utilities for testing nilearn.
"""
# Author: Alexandre Abrahame, Philippe Gervais
# License: simplified BSD
import contextlib
import os
import os.path as op
import re
import shutil
import sys
import tempfile
import time
import warnings

from nose import SkipTest
from nose.tools import assert_true

from .threads import KThread
from ..objdep import get_missing_dependencies


try:
    from nose.tools import assert_raises_regex
except ImportError:
    # For Py 2.7
    try:
        from nose.tools import assert_raises_regexp as assert_raises_regex
    except ImportError:
        # for Py 2.6
        def assert_raises_regex(expected_exception, expected_regexp,
                                callable_obj=None, *args, **kwargs):
            """Helper function to check for message patterns in exceptions"""

            not_raised = False
            try:
                callable_obj(*args, **kwargs)
                not_raised = True
            except Exception as e:
                error_message = str(e)
                if not re.compile(expected_regexp).search(error_message):
                    raise AssertionError("Error message should match pattern "
                                         "%r. %r does not." %
                                         (expected_regexp, error_message))
            if not_raised:
                raise AssertionError("Should have raised %r" %
                                     expected_exception(expected_regexp))

try:
    from sklearn.utils.testing import assert_warns
except ImportError:
    # sklearn.utils.testing.assert_warns new in scikit-learn 0.14
    def assert_warns(warning_class, func, *args, **kw):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore", warning_class)
            output = func(*args, **kw)
        return output


class DownloadTestMixin(object):
    duration = 2
    time_step = 0.1

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.data_dir = op.join(self.tmp_dir,
                                op.basename(tempfile.mkstemp()[1]))
        missing_dependencies = get_missing_dependencies(
            self.dataset_class.dependencies)
        if len(missing_dependencies) > 0:
            raise SkipTest

    def tearDown(self):
        if op.exists(self.data_dir):
            shutil.rmtree(self.data_dir)

    def fetch(self, *args, **kwargs):
        dset = self.dataset_class(data_dir=self.data_dir)
        return dset.fetch(*args, **kwargs)

    def test_me(self):
        if getattr(self, 'dataset_class', None) is None:
            raise SkipTest

        def wrapper_fn():
            try:
                self.fetch(verbose=0)
            except Exception as e:
                self.exception = e
                raise

        def test_func(*args, **kwargs):
            assert_true(op.exists(self.data_dir))

        self.exception = None
        thread = KThread(target=wrapper_fn, args=(), kwargs={})
        thread.start()

        wait_time = self.duration
        while thread.is_alive() and wait_time > 0:  # busy waiting
            time.sleep(min(wait_time, self.time_step))
            wait_time -= self.time_step

        if thread.is_alive():
            thread.kill()
        assert_true(self.exception is None, str(self.exception))


@contextlib.contextmanager
def write_tmp_imgs(*imgs, **kwargs):
    """Context manager for writing Nifti images.

    Write nifti images in a temporary location, and remove them at the end of
    the block.

    Parameters
    ==========
    imgs: Nifti1Image
        Several Nifti images. Every format understood by nibabel.save is
        accepted.

    create_files: bool
        if True, imgs are written on disk and filenames are returned. If
        False, nothing is written, and imgs is returned as output. This is
        useful to test the two cases (filename / Nifti1Image) in the same
        loop.

    Returns
    =======
    filenames: string or list of
        filename(s) where input images have been written. If a single image
        has been given as input, a single string is returned. Otherwise, a
        list of string is returned.
    """
    valid_keys = set(("create_files",))
    input_keys = set(kwargs.keys())
    invalid_keys = input_keys - valid_keys
    if len(invalid_keys) > 0:
        raise TypeError("%s: unexpected keyword argument(s): %s" %
                        (sys._getframe().f_code.co_name,
                         " ".join(invalid_keys)))
    create_files = kwargs.get("create_files", True)

    if create_files:
        filenames = []
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            for img in imgs:
                _, filename = tempfile.mkstemp(prefix="nilearn_",
                                               suffix=".nii",
                                               dir=None)
                filenames.append(filename)
                img.to_filename(filename)

        if len(imgs) == 1:
            yield filenames[0]
        else:
            yield filenames

        for filename in filenames:
            os.remove(filename)
    else:  # No-op
        if len(imgs) == 1:
            yield imgs[0]
        else:
            yield imgs


# Backport: On some nose versions, assert_less_equal is not present
try:
    from nose.tools import assert_less_equal
except ImportError:
    def assert_less_equal(a, b):
        if a > b:
            raise AssertionError("%f is not less than %f" % (a, b))
