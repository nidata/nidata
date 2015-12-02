"""
"""

import contextlib
import collections
import os
import tarfile
import zipfile
import sys
import shutil
import time
import hashlib
import fnmatch
import warnings
import re
import base64
from functools import partial

import nibabel as nib
import numpy as np
from scipy import ndimage
from sklearn.datasets.base import Bunch

from .._utils.compat import _basestring, BytesIO, cPickle, _urllib, md5_hash
from .base import chunk_report, Fetcher


def movetree(src, dst):
    """Move an entire tree to another directory. Any existing file is
    overwritten"""
    names = os.listdir(src)

    # Create destination dir if it does not exist
    if not os.path.exists(dst):
        os.makedirs(dst)
    errors = []

    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname) and os.path.isdir(dstname):
                movetree(srcname, dstname)
                os.rmdir(srcname)
            else:
                shutil.move(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive movetree so that we can
        # continue with other files
        except Exception as err:
            errors.extend(err.args[0])
    if errors:
        raise Exception(errors)


def _tree(path, pattern=None, dictionary=False):
    """ Return a directory tree under the form of a dictionaries and list

    Parameters:
    -----------
    path: string
        Path browsed

    pattern: string, optional
        Pattern used to filter files (see fnmatch)

    dictionary: boolean, optional
        If True, the function will return a dict instead of a list
    """
    files = []
    dirs = [] if not dictionary else {}
    for file_ in os.listdir(path):
        file_path = os.path.join(path, file_)
        if os.path.isdir(file_path):
            if not dictionary:
                dirs.append((file_, _tree(file_path, pattern)))
            else:
                dirs[file_] = _tree(file_path, pattern)
        else:
            if pattern is None or fnmatch.fnmatch(file_, pattern):
                files.append(file_path)
    files = sorted(files)
    if not dictionary:
        return sorted(dirs) + files
    if len(dirs) == 0:
        return files
    if len(files) > 0:
        dirs['.'] = files
    return dirs


def _chunk_read_(response, local_file, chunk_size=8192, report_hook=None,
                 initial_size=0, total_size=None, verbose=1):
    """Download a file chunk by chunk and show advancement

    Parameters
    ----------
    response: _urllib.response.addinfourl
        Response to the download request in order to get file size

    local_file: file
        Hard disk file where data should be written

    chunk_size: int, optional
        Size of downloaded chunks. Default: 8192

    report_hook: bool
        Whether or not to show downloading advancement. Default: None

    initial_size: int, optional
        If resuming, indicate the initial size of the file

    total_size: int, optional
        Expected final size of download (None means it is unknown).

    verbose: int, optional
        verbosity level (0 means no message).

    Returns
    -------
    data: string
        The downloaded file.

    """
    if total_size is None:
        total_size = response.info().get('Content-Length', '110000000').strip()
    try:
        total_size = int(total_size) + initial_size
    except Exception as e:
        if verbose > 1:
            print("Warning: total size could not be determined.")
            if verbose > 2:
                print("Full stack trace: %s" % e)
        total_size = None
    bytes_so_far = initial_size

    t0 = time.time()
    while True:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            if report_hook:
                sys.stderr.write('\n')
            break

        local_file.write(chunk)
        if report_hook:
            chunk_report(bytes_so_far, total_size, initial_size, t0)

    return


def _uncompress_file(file_, delete_archive=True, verbose=1):
    """Uncompress files contained in a data_set.

    Parameters
    ----------
    file: string
        path of file to be uncompressed.

    delete_archive: bool, optional
        Whether or not to delete archive once it is uncompressed.
        Default: True

    verbose: int, optional
        verbosity level (0 means no message).

    Notes
    -----
    This handles zip, tar, gzip and bzip files only.
    """
    if verbose > 0:
        print('Extracting data from %s...' % file_)
    data_dir = os.path.dirname(file_)
    # We first try to see if it is a zip file
    try:
        filename, ext = os.path.splitext(file_)
        with open(file_, "rb") as fd:
            header = fd.read(4)
        processed = False
        if zipfile.is_zipfile(file_):
            z = zipfile.ZipFile(file_)
            z.extractall(data_dir)
            z.close()
            processed = True
        elif ext == '.gz' or header.startswith(b'\x1f\x8b'):
            import gzip
            gz = gzip.open(file_)
            if ext == '.tgz':
                filename = filename + '.tar'
            out = open(filename, 'wb')
            shutil.copyfileobj(gz, out, 8192)
            gz.close()
            out.close()

            # If file is .tar.gz, this will be handle in the next case
            if delete_archive:
                os.remove(file_)
            file_ = filename
            filename, ext = os.path.splitext(file_)
            processed = True

        if tarfile.is_tarfile(file_):
            with contextlib.closing(tarfile.open(file_, "r")) as tar:
                tar.extractall(path=data_dir)
            processed = True
        if not processed:
            raise IOError(
                    "[Uncompress] unknown archive file format: %s" % file_)
        if delete_archive:
            os.remove(file_)
        if verbose > 0:
            print('   ...done.')
    except Exception as e:
        if verbose > 0:
            print('Error uncompressing file: %s' % e)
        raise


def _fetch_file(url, data_dir, resume=True, overwrite=False,
                md5sum=None, username=None, passwd=None,
                handlers=None, headers=None, cookies=None, verbose=1):
    """Load requested file, downloading it if needed or requested.

    Parameters
    ----------
    url: string
        Contains the url of the file to be downloaded.

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    resume: bool, optional
        If true, try to resume partially downloaded files

    overwrite: bool, optional
        If true and file already exists, delete it.

    md5sum: string, optional
        MD5 sum of the file. Checked if download of the file is required

    username: string, optional
        Username used for HTTP authentication

    passwd: string, optional
        Password used for HTTP authentication

    handlers: list of BaseHandler, optional
        urllib handlers passed to urllib.request.build_opener. Used by
        advanced users to customize request handling.

    headers: dictionary, specifying headers

    cookies: dictionary, specifying cookies

    verbose: int, optional
        verbosity level (0 means no message).

    Returns
    -------
    files: string
        Absolute path of downloaded file.

    Notes
    -----
    If, for any reason, the download procedure fails, all downloaded files are
    removed.
    """
    if handlers is None:
        handlers = []
    if headers is None:
        headers = dict(),
    if cookies is None:
        cookies = dict()

    # Determine data path
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Determine filename using URL
    parse = _urllib.parse.urlparse(url)
    file_name = os.path.basename(parse.path)
    if file_name == '':
        file_name = md5_hash(parse.path)

    temp_file_name = file_name + ".part"
    full_name = os.path.join(data_dir, file_name)
    temp_full_name = os.path.join(data_dir, temp_file_name)
    if os.path.exists(full_name):
        if overwrite:
            os.remove(full_name)
        else:
            return full_name
    if os.path.exists(temp_full_name):
        if overwrite:
            os.remove(temp_full_name)
    t0 = time.time()
    local_file = None
    initial_size = 0

    try:
        # Download data
        if username:
            # Make sure we're secure, basic auth is unencrypted
            if parse.scheme and parse.scheme != 'https':
                raise ValueError('Specifying username currently requires using a secure (https) URL (%s).' % url)
            password_mgr = _urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, url, username, passwd)
            # Don't append, don't want to update caller's list with this!
            handlers = [_urllib.request.HTTPBasicAuthHandler(password_mgr)] + handlers
        url_opener = _urllib.request.build_opener(*handlers)

        # Prep the request (add headers, cookies)
        request = _urllib.request.Request(url)
        request.add_header('Connection', 'Keep-Alive')
        if cookies:
            if 'Cookie' in headers:
                headers['Cookie'] += ';'
            else:
                headers['Cookie'] = ''
            headers['Cookie'] += ';'.join(['%s=%s' % (k, v) for k, v in cookies.items()])
        for header_name, header_val in headers.items():
            request.add_header(header_name, header_val)

        if verbose > 0:
            displayed_url = url.split('?')[0] if verbose == 1 else url
            print('Downloading data from %s ...' % displayed_url)
        if not resume or not os.path.exists(temp_full_name):
            # Simple case: no resume
            data = url_opener.open(request)
            local_file = open(temp_full_name, "wb")
        else:
            # Complex case: download has been interrupted, we try to resume it.
            local_file_size = os.path.getsize(temp_full_name)
            # If the file exists, then only download the remainder
            request.add_header("Range", "bytes=%s-" % (local_file_size))
            try:
                data = url_opener.open(request)
                content_range = data.info().get('Content-Range')
                if (content_range is None or not content_range.startswith(
                        'bytes %s-' % local_file_size)):
                    raise IOError('Server does not support resuming')
            except Exception as ex:
                # A wide number of errors can be raised here. HTTPError,
                # URLError... I prefer to catch them all and rerun without
                # resuming.
                if verbose > 0:
                    print('Resuming failed, try to download the whole file.')
                return _fetch_file(
                    url, data_dir, resume=False, overwrite=overwrite,
                    md5sum=md5sum, username=username, passwd=passwd,
                    handlers=handlers, headers=headers, cookies=cookies,
                    verbose=verbose)
            else:
                local_file = open(temp_full_name, "ab")
                initial_size = local_file_size

        # Download the file.
        _chunk_read_(data, local_file, report_hook=(verbose > 0),
                     initial_size=initial_size, verbose=verbose)

        # temp file must be closed prior to the move
        if not local_file.closed:
            local_file.close()
        shutil.move(temp_full_name, full_name)
        dt = time.time() - t0
        if verbose > 0:
            print('...done. (%i seconds, %i min)' % (dt, dt // 60))
    except _urllib.error.HTTPError as e:
        if verbose > 0:
            print('Error while fetching file %s. Dataset fetching aborted.' %
                   (file_name))
        if verbose > 1:
            print("HTTP Error: %s, %s" % (e, url))
        raise
    except _urllib.error.URLError as e:
        if verbose > 0:
            print('Error while fetching file %s. Dataset fetching aborted.' %
                   (file_name))
        if verbose > 1:
            print("URL Error: %s, %s" % (e, url))
        raise
    finally:
        if local_file is not None and not local_file.closed:
            local_file.close()
    if md5sum is not None:
        if (md5_sum_file(full_name) != md5sum):
            raise ValueError("File %s checksum verification has failed."
                             " Dataset fetching aborted." % local_file)
    return full_name


def fetch_files(data_dir, files, resume=True, force=False, verbose=1, delete_archive=True):
    """Load requested dataset, downloading it if needed or requested.

    This function retrieves files from the hard drive or download them from
    the given urls. Note to developers: All the files will be first
    downloaded in a sandbox and, if everything goes well, they will be moved
    into the folder of the dataset. This prevents corrupting previously
    downloaded data. In case of a big dataset, do not hesitate to make several
    calls if needed.

    Parameters
    ----------
    dataset_name: string
        Unique dataset name

    files: list of (string, string, dict)
        List of files and their corresponding url. The dictionary contains
        options regarding the files. Options supported are 'uncompress' to
        indicates that the file is an archive, 'md5sum' to check the md5 sum of
        the file and 'move' if renaming the file or moving it to a subfolder is
        needed.

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    resume: bool, optional
        If true, try resuming download if possible

    mock: boolean, optional
        If true, create empty files if the file cannot be downloaded. Test use
        only.

    verbose: int, optional
        verbosity level (0 means no message).

    Returns
    -------
    files: list of string
        Absolute paths of downloaded files on disk
    """
    # We may be in a global read-only repository. If so, we cannot
    # download files.
    if not os.access(data_dir, os.W_OK):
        raise ValueError('Dataset files are missing but dataset'
                         ' repository is read-only. Contact your data'
                         ' administrator to solve the problem')

    # Create destination dirs
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    files_ = []
    for file_, url, opts in files:
        # There are two working directories here:
        # - data_dir is the destination directory of the dataset
        # - temp_dir is a temporary directory dedicated to this fetching call. All
        #   files that must be downloaded will be in this directory. If a corrupted
        #   file is found, or a file is missing, this working directory will be
        #   deleted.
        files_pickle = cPickle.dumps(url)
        files_md5 = hashlib.md5(files_pickle).hexdigest()
        temp_dir = os.path.join(data_dir, files_md5)

        # 3 possibilities:
        # - the file exists in data_dir, nothing to do.
        # - the file does not exists: we download it in temp_dir
        # - the file exists in temp_dir: this can happen if an archive has been
        #   downloaded. There is nothing to do

        # Target file in the data_dir
        target_file = os.path.join(data_dir, file_)

        if force or not os.path.exists(target_file):
            # if not os.path.exists(temp_target_dir):
            #     os.makedirs(temp_target_dir)
            # Fetch the file, if it doesn't already exist.
            fetched_file = _fetch_file(url, temp_dir,
                                       resume=resume,
                                       overwrite=force,
                                       verbose=verbose,
                                       md5sum=opts.get('md5sum'),
                                       username=opts.get('username'),
                                       passwd=opts.get('passwd'),
                                       handlers=opts.get('handlers', []),
                                       headers=opts.get('headers', dict()),
                                       cookies=opts.get('cookies', dict()))

            # First, uncompress.
            if opts.get('uncompress'):
                target_files = _uncompress_file(fetched_file, verbose=verbose, delete_archive=False)
            else:
                target_files = [fetched_file]

            if opts.get('move'):
                raise NotImplementedError('Move options has been removed. Sorry!')

                # XXX: here, move is supposed to be a dir, it can be a name
                move = os.path.join(temp_dir, opts['move'])

                if len(target_files) > 1:
                    target_files = [os.path.join(os.path.dirname(move),
                                         os.path.basename(f))
                                    for f in target_files]
                    # Do the move
                else:
                    if not os.path.exists(move_dir):
                        os.makedirs(move_dir)
                    shutil.move(fetched_file, move)
                    target_files = [move]
                temp_target_file = move

            # Let's examine our work
            if not os.path.exists(target_file):
                if os.path.exists(fetched_file):
                    target_dir = os.path.dirname(target_file)
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    shutil.move(fetched_file, target_file)
                else:
                    raise Exception("An error occurred while fetching %s; the expected target file cannot be found. (%s)\nDebug info: %s" % (
                        file_, target_file,
                        {'fetched_file': fetched_file, 'target_files': target_files}))

            if opts.get('uncompress') and delete_archive:
                os.remove(fetched_file)

            # If needed, move files from temps directory to final directory.
            if os.path.exists(temp_dir):
                #XXX We could only moved the files requested
                #XXX Movetree can go wrong
                movetree(temp_dir, data_dir)
                shutil.rmtree(temp_dir)

        files_.append(target_file)

    return files_


def copytree(src, dst, symlinks=False, ignore=None):
    import os
    import shutil
    import stat

    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
              pass # lchmod not available
        elif os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


class HttpFetcher(Fetcher):

    def __init__(self, data_dir=None, username=None, passwd=None):
        super(HttpFetcher, self).__init__(data_dir=data_dir)
        self.username = username
        self.passwd = passwd

    def fetch(self, files, force=False, resume=True, check=False, verbose=1, delete_archive=True):
        files = self.reformat_files(files)  # allows flexibility
        if self.username is not None:
            for tgt, src, opts in files:
                opts['username'] = opts.get('username', self.username)
                opts['passwd'] = opts.get('passwd', self.username)

        return fetch_files(self.data_dir, files, resume=resume, force=force, verbose=verbose, delete_archive=delete_archive)
