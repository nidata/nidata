# *- encoding: utf-8 -*-
"""
Utilities to download NeuroImaging datasets
"""
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import collections
import hashlib
import os
import os.path as op
import sys
import time

import numpy as np
from six import string_types

from ..objdep import ClassWithDependencies


def format_time(t):
    if t > 60:
        return "%4.1fmin" % (t / 60.)
    else:
        return " %5.1fs" % (t)


def md5_sum_file(path):
    """ Calculates the MD5 sum of a file.
    """
    with open(path, 'rb') as f:
        m = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            m.update(data)
    return m.hexdigest()


def readmd5_sum_file(path):
    """ Reads a MD5 checksum file and returns hashes as a dictionary.
    """
    with open(path, "r") as f:
        hashes = {}
        while True:
            line = f.readline()
            if not line:
                break
            h, name = line.rstrip().split('  ', 1)
            hashes[name] = h
    return hashes


def _filter_column(array, col, criteria):
    """ Return index array matching criteria

    Parameters
    ----------

    array: numpy array with columns
        Array in which data will be filtered

    col: string
        Name of the column

    criteria: integer (or float), pair of integers, string or list of these
        if integer, select elements in column matching integer
        if a tuple, select elements between the limits given by the tuple
        if a string, select elements that match the string
    """
    # Raise an error if the column does not exist. This is the only way to
    # test it across all possible types (pandas, recarray...)
    try:
        array[col]
    except:
        raise KeyError('Filtering criterion %s does not exist' % col)

    if (not isinstance(criteria, string_types) and
        not isinstance(criteria, bytes) and
        not isinstance(criteria, tuple) and
            isinstance(criteria, collections.Iterable)):

        filter = np.zeros(array.shape[0], dtype=np.bool)
        for criterion in criteria:
            filter = np.logical_or(filter,
                                   _filter_column(array, col, criterion))
        return filter

    if isinstance(criteria, tuple):
        if len(criteria) != 2:
            raise ValueError("An interval must have 2 values")
        if criteria[0] is None:
            return array[col] <= criteria[1]
        if criteria[1] is None:
            return array[col] >= criteria[0]
        filter = array[col] <= criteria[1]
        return np.logical_and(filter, array[col] >= criteria[0])

    return array[col] == criteria


def filter_columns(array, filters, combination='and'):
    """ Return indices of recarray entries that match criteria.

    Parameters
    ----------

    array: numpy array with columns
        Array in which data will be filtered

    filters: list of criteria
        See _filter_column

    combination: string, optional
        String describing the combination operator. Possible values are "and"
        and "or".
    """
    if combination == 'and':
        fcomb = np.logical_and
        mask = np.ones(array.shape[0], dtype=np.bool)
    elif combination == 'or':
        fcomb = np.logical_or
        mask = np.zeros(array.shape[0], dtype=np.bool)
    else:
        raise ValueError('Combination mode not known: %s' % combination)

    for column in filters:
        mask = fcomb(mask, _filter_column(array, column, filters[column]))
    return mask


def chunk_report(bytes_so_far, total_size, initial_size, t0):
    """Show downloading percentage.

    Parameters
    ----------
    bytes_so_far: int
        Number of downloaded bytes

    total_size: int
        Total size of the file (may be 0/None, depending on download method).

    t0: int
        The time in seconds (as returned by time.time()) at which the
        download was resumed / started.

    initial_size: int
        If resuming, indicate the initial size of the file.
        If not resuming, set to zero.
    """

    if not total_size:
        sys.stderr.write("Downloaded %d of ? bytes\r" % (bytes_so_far))

    else:
        # Estimate remaining download time
        total_percent = float(bytes_so_far) / total_size

        current_download_size = bytes_so_far - initial_size
        bytes_remaining = total_size - bytes_so_far
        dt = time.time() - t0
        download_rate = current_download_size / max(1e-8, float(dt))
        # Minimum rate of 0.01 bytes/s, to avoid dividing by zero.
        time_remaining = bytes_remaining / max(0.01, download_rate)

        # Trailing whitespace is to erase extra char when message length
        # varies
        sys.stderr.write(
            "Downloaded %d of %d bytes (%0.2f%%, %s remaining)  \r"
            % (bytes_so_far, total_size, total_percent * 100,
               format_time(time_remaining)))


class Fetcher(ClassWithDependencies):
    dependencies = []

    def __init__(self, data_dir=None, verbose=1):
        self.data_dir = data_dir or os.environ.get('NIDATA_PATH',
                                                   'nidata_data')
        if verbose > 0 and not op.exists(self.data_dir):
            print("Files will be downloaded to %s" % self.data_dir)

    @classmethod
    def reformat_files(cls, files):
        """ Takes an iterable, and puts into the expected format of
        a tuple if triplet tuples."""

        common_path = None  # src base
        out_files = []
        for fil in files:
            if isinstance(fil, string_types):
                if len(files) == 1:
                    common_prefix = op.dirname(fil) + '/'
                elif common_path is None:
                    common_prefix = op.commonprefix(files)
                if fil[len(common_prefix):][0] != '/':
                    common_path = op.dirname(common_prefix) + '/'
                else:
                    common_path = common_prefix
                out_files.append((fil[len(common_path):], fil, dict()))
            elif not isinstance(fil, collections.Iterable):
                raise ValueError("Unexpected format: %s" % str(fil))
            elif len(fil) == 2:  # assume src, dest
                out_files.append((fil[0], fil[1], dict()))
            elif len(fil) == 3:
                out_files.append(fil)
            else:
                raise ValueError("Unexpected format: %s" % str(fil))
        return out_files

    def fetch(self, files, force=False, check=False, verbose=1):
        raise NotImplementedError()
