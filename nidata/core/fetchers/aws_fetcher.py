"""
"""

import os
import time
import warnings
from functools import partial

import nibabel as nib
import numpy as np

from .base import chunk_report, Fetcher


def test_cb(cur_bytes, total_bytes, t0=None, **kwargs):
    return chunk_report(bytes_so_far=cur_bytes, total_size=total_bytes, initial_size=0, t0=t0)


class AmazonS3Fetcher(Fetcher):
    dependencies = ['boto']

    def __init__(self, data_dir=None, access_key=None, secret_access_key=None, profile_name=None):
        if not (profile_name or (access_key and secret_access_key)):
            raise ValueError('profile_name or access_key / secret_access_key must be provided.')
        super(AmazonS3Fetcher, self).__init__(data_dir=data_dir)
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.profile_name = profile_name

    def fetch(self, files, force=False, check=False, verbose=1):
        assert self.profile_name or (self.access_key and self.secret_access_key)

        files = Fetcher.reformat_files(files)  # allows flexibility
        import boto
        if self.profile_name is not None:
            s3 = boto.connect_s3(profile_name=self.profile_name)
        elif self.access_key is not None and self.secret_access_key is not None:
            s3 = boto.connect_s3(self.access_key, self.secret_access_key)

        bucket_names = np.unique([opts.get('bucket') for f, rk, opts in files])
        files_ = []
        for bucket_name in bucket_names:  # loop over bucket names: efficient
            if bucket_name:  # bucket requested
                buck = s3.get_bucket(bucket_name)
            else:  # default to first bucket
                buck = s3.get_all_buckets()[0]

            for file_, remote_key, opts in files:
                if opts.get('bucket') != bucket_name:
                    continue  # get all files from the current bucket only.
                target_file = os.path.join(self.data_dir, file_)
                key = buck.get_key(remote_key)
                if not key:
                    warnings.warn('Failed to find key: %s' % remote_key)
                    files_.append(None)
                else:
                    do_download = force or not os.path.exists(target_file)
                    try:
                        do_download = do_download or (check and nib.load(target_file).get_data() is not None)
                    except IOError as ioe:
                        if verbose > 0:
                            print("Warning: %s corrupted, re-downloading (Error=%s)" % (target_file, ioe))
                        do_download = True

                    if do_download:
                        # Ensure destination directory exists
                        destination_dir = os.path.dirname(target_file)
                        if not os.path.isdir(destination_dir):
                            if verbose > 0:
                                print("Creating base directory %s" % destination_dir)
                            os.makedirs(destination_dir)

                        if verbose > 0:
                            print("Downloading [%s]/%s to %s." % (
                                bucket_name or 'default bucket',
                                remote_key,
                                target_file))
                        with open(target_file, 'wb') as fp:
                            key.get_contents_to_file(fp, cb=partial(test_cb, t0=time.time()), num_cb=None)

                    files_.append(target_file)
        return files_
