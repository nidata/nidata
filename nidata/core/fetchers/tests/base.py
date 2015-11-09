import contextlib
import functools
import inspect
import os
import re
import sys
import tempfile
import warnings
import copy

import numpy as np
import scipy.signal
from sklearn.utils import check_random_state
import scipy.linalg
import nibabel

from ..http_fetcher import fetch_files
from ..._utils.compat import _basestring, _urllib


class MockRequest(object):
    def __init__(self, url):
        self.url = url

    def add_header(*args):
        pass


class MockOpener(object):
    def __init__(self):
        pass

    def open(self, request):
        return request.url


class mock_request(object):
    def __init__(self):
        """Object that mocks the urllib (future) module to store downloaded filenames.

        `urls` is the list of the files whose download has been
        requested.
        """
        self.urls = set()

    def reset(self):
        self.urls = set()

    def Request(self, url):
        self.urls.add(url)
        return MockRequest(url)

    def build_opener(self, *args, **kwargs):
        return MockOpener()


def wrap_chunk_read_(_chunk_read_):
    def mock_chunk_read_(response, local_file, initial_size=0, chunk_size=8192,
                         report_hook=None, verbose=0):
        if not isinstance(response, _basestring):
            return _chunk_read_(response, local_file,
                                initial_size=initial_size,
                                chunk_size=chunk_size,
                                report_hook=report_hook, verbose=verbose)
        return response
    return mock_chunk_read_


def mock_chunk_read_raise_error_(response, local_file, initial_size=0,
                                 chunk_size=8192, report_hook=None,
                                 verbose=0):
    raise _urllib.errors.HTTPError("url", 418, "I'm a teapot", None, None)


class FetchFilesMock (object):
    _mockfetch_files = functools.partial(fetch_files, mock=True)

    def __str__(self):
        return ':'.join(self.csv_files.values())

    def __unicode__(self):
        return u':'.join(self.csv_files.values())

    def __init__(self):
        """Create a mock that can fill a CSV file if needed
        """
        self.csv_files = {}

    def add_csv(self, filename, content):
        self.csv_files[filename] = content

    def __call__(self, *args, **kwargs):
        """Load requested dataset, downloading it if needed or requested.

        For test purpose, instead of actually fetching the dataset, this
        function creates empty files and return their paths.
        """
        filenames = self._mockfetch_files(*args, **kwargs)
        # Fill CSV files with given content if needed
        for fname in filenames:
            basename = os.path.basename(fname)
            if basename in self.csv_files:
                array = self.csv_files[basename]

                # np.savetxt does not have a header argument for numpy 1.6
                # np.savetxt(fname, array, delimiter=',', fmt="%s",
                #            header=','.join(array.dtype.names))
                # We need to add the header ourselves
                with open(fname, 'wb') as f:
                    header = '# {0}\n'.format(','.join(array.dtype.names))
                    f.write(header.encode())
                    np.savetxt(f, array, delimiter=',', fmt='%s')

        return filenames
