"""
"""

import os
import time
import warnings
from functools import partial

import boto
import numpy as np

from . import _chunk_report_


def test_cb(cur_bytes, total_bytes, t0=None, **kwargs):
    return _chunk_report_(bytes_so_far=cur_bytes, total_size=total_bytes, initial_size=0, t0=t0)


def aws_fetcher(data_dir, files, access_key=None, secret_access_key=None, profile_name=None, force=True):
    if profile_name is not None:
        s3 = boto.connect_s3(profile_name=profile_name)
    elif access_key is not None and secret_access_key is not None:
        s3 = boto.connect_s3(access_key, secret_access_key)


    bucket_names = np.unique([opts.get('bucket') for f, rk, opts in files])
    for bucket_name in bucket_names:  # loop over bucket names for efficiency.
        if bucket_name:
            buck = s3.get_bucket(bucket_name)
        else:
            buck = s3.get_all_buckets()[0]

        files_ = []
        for file_, remote_key, opts in files:
            if opts.get('bucket') != bucket_name:
                continue
            target_file = os.path.join(data_dir, file_)
            key = buck.get_key(remote_key)
            if not key:
                warnings.warn('Failed to find key: %s' % remote_key)
                files_.append(None)
            elif force or not os.path.exists(target_file):
                with open(target_file, 'wb') as fp:
                    key.get_contents_to_file(fp, cb=partial(test_cb, t0=time.time()), num_cb=None)
                files_.append(target_file)
    return files_
