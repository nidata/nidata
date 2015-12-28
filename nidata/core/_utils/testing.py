"""Utilities for testing nilearn.
"""
# Author: Alexandre Abrahame, Philippe Gervais
# License: simplified BSD
import contextlib
import copy
import importlib
import os
import os.path as op
import re
import shutil
import subprocess
import sys
import tempfile
import warnings

from nose import SkipTest
from nose.tools import assert_equal, assert_true

from ..datasets import Dataset
from ..fetchers import Fetcher

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


class _DummyDataset(Dataset):
    def fetch(self, *args, **kwargs):
        return dict()


class _DummyFetcher(Fetcher):
    def fetch(self, files, *args, **kwargs):
        out_files = []
        for dest_filename, url, opts in self.reformat_files(files):
            dest_path = op.join(self.data_dir, dest_filename)
            dest_dir = op.dirname(dest_path)
            print(dest_filename, url, opts, dest_path)

            # Create output
            if not op.exists(dest_dir):
                os.makedirs(dest_dir)
            with open(dest_path, 'w') as fp:
                fp.write(url)
            out_files.append(dest_path)
        return out_files


class DownloadTestMixin(object):
    duration = 2
    time_step = 0.1

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.data_dir = op.join(self.tmp_dir,
                                op.basename(tempfile.mkstemp()[1]))

    def tearDown(self):
        if op.exists(self.data_dir):
            shutil.rmtree(self.data_dir)

    def fetch(self, *args, **kwargs):
        missing_dependencies = self.dataset_class.get_missing_dependencies()
        if len(missing_dependencies) > 0:
            raise SkipTest('Missing dependencies: %s' % (
                ','.join(self.dataset_class.dependencies)))

        dset = self.dataset_class(data_dir=self.data_dir)

        # Replace the fetcher (or fetch function itself)
        # to avoid actually getting files.
        if dset.fetcher is None:
            instancemethod = dset.fetch.__class__
            func = _DummyDataset.fetch
            if sys.version_info[0] > 2:
                dset.fetch = instancemethod(func, dset)
            else:
                func = func.__func__
                dset.fetch = instancemethod(func, dset, dset.__class)
        else:
            instancemethod = dset.fetcher.fetch.__class__
            func = _DummyFetcher.fetch
            if sys.version_info[0] > 2:
                dset.fetcher.fetch = instancemethod(
                    func, dset.fetcher)
            else:
                func = func.__func__
                dset.fetcher.fetch = instancemethod(
                    func, dset.fetcher, dset.fetcher.__class__)

        return dset.fetch(*args, **kwargs)

    def test_fetch_defaults(self):
        self.fetch()
        assert_true(op.exists(self.data_dir))


def create_virtualenv(venv_name, dir_path=None):
    dir_path = dir_path or tempfile.mkdtemp()
    old_args = sys.argv
    try:
        from virtualenv import main
        sys.argv = ['virtualenv', op.join(dir_path, venv_name)]
        main()
    finally:
        sys.argv = old_args
    print("Created virtualenv %s at %s" % (venv_name, dir_path))
    return dir_path


def activate_virtualenv(venv_name, dir_path):
    activate_path = op.join(dir_path, venv_name, 'bin', 'activate_this.py')
    with open(activate_path, 'r') as fp:
        exec(fp.read(), dict(__file__=activate_path))
    print("Activated virtualenv %s at %s" % (venv_name, dir_path))


class TestInVirtualEnvMixin(object):

    def setUp(self):
        # Store old variables
        self.environ = copy.deepcopy(os.environ)
        self.path = copy.deepcopy(sys.path)
        self.module_keys = copy.copy(list(sys.modules.keys()))
        self.prefix = sys.prefix
        self.real_prefix = getattr(sys, 'real_prefix', None)

        # Numpy and scipy are too difficult to install,
        #  so if they're in the old environment, link them
        #  to the new.
        add_paths = []
        for module_name in ['numpy', 'scipy', 'h5py']:
            try:
                mod = importlib.import_module(module_name)
                add_paths.append(op.dirname(op.dirname(mod.__file__)))
                print('Will add %s to path.' % module_name)
            except ImportError as ie:
                warnings.warn("%s is not installed, your test %s"
                              " may fail. (%s)" % (
                                  module_name, self.__class__.__name__, ie))

        # Create & activate virtual environment
        self.venv_name = self.__class__.__name__
        self.venv_path = create_virtualenv(self.venv_name)
        activate_virtualenv(self.venv_name, dir_path=self.venv_path)

        # Add paths
        sys.path = sys.path + add_paths

    def tearDown(self):
        # Remove the files
        if op.exists(self.venv_path):
            shutil.rmtree(self.venv_path)

        # Reset key variables.
        for key in self.environ:
            os.environ[key] = self.environ[key]
        sys.prefix = self.prefix
        if self.real_prefix:
            sys.real_prefix = self.real_prefix
        elif getattr(sys, 'real_prefix', None) is not None:
            del sys.real_prefix
        sys.path = self.path
        for key in copy.copy(list(sys.modules.keys())):
            if key not in self.module_keys:
                del sys.modules[key]


class InstallTestMixin(TestInVirtualEnvMixin):
    def test_install(self):
        # Make sure the environment is clean.
        out = subprocess.Popen(
            ['pip', 'list'], stdout=subprocess.PIPE).communicate()[0].decode()
        installed_mods = [lin.split(' ')[0] for lin in out.split('\n')]
        for dep in self.dataset_class.dependencies:
            if dep in ['numpy', 'scipy', 'h5py']:
                continue
            assert_true(dep not in installed_mods,
                        "Dependency '%s' is already installed.\n%s" % (
                            dep, installed_mods))

        # Now, instantiate the object
        self.dataset_class()

        # check dependencies now!
        assert_equal(0, len(self.dataset_class.get_missing_dependencies()),
                     ','.join(self.dataset_class.get_missing_dependencies()))


class InstallThenDownloadTestMixin(InstallTestMixin, DownloadTestMixin):
    def setUp(self):
        InstallTestMixin.setUp(self)

        # Instantiate the object to trigger the install.
        self.dataset_class()

        DownloadTestMixin.setUp(self)

    def tearDown(self):
        DownloadTestMixin.tearDown(self)
        InstallTestMixin.tearDown(self)

    def test_install(self):
        # check dependencies now!
        assert_equal(0, len(self.dataset_class.get_missing_dependencies()),
                     ','.join(self.dataset_class.get_missing_dependencies()))


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
