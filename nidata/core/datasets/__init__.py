"""
"""
import inspect
import os

from ..objdep import DependenciesMeta


def get_dataset_descr(ds_path, ds_name):
    rst_path = os.path.join(ds_path, ds_name + '.rst')
    try:
        with open(rst_path) as rst_file:
            descr = rst_file.read()
    except IOError:
        print("Warning: Could not find dataset description (%s)." % rst_path)
        descr = ''

    return descr


def get_dataset_dir(dataset_name, data_dir=None, env_vars=[],
                    verbose=1):
    """ Create if necessary and returns data directory of given dataset.

    Parameters
    ----------
    dataset_name: string
        The unique name of the dataset.

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    env_vars: list of string, optional
        Add environment variables searched even if data_dir is not None.

    verbose: int, optional
        verbosity level (0 means no message).

    Returns
    -------
    data_dir: string
        Path of the given dataset directory.

    Notes
    -----
    This function retrieves the datasets directory (or data directory) using
    the following priority :
    1. the keyword argument data_dir
    2. the global environment variable NILEARN_SHARED_DATA
    3. the user environment variable NIDATA_PATH
    4. NIDATA_PATH in the user home folder
    """
    # We build an array of successive paths by priority
    paths = []

    # Search given environment variables
    for env_var in env_vars:
        env_data = os.getenv(env_var, '')
        paths.extend(env_data.split(':'))

    # Check data_dir which force storage in a specific location
    if data_dir is not None:
        paths = data_dir.split(':')
    else:
        global_data = os.getenv('NIDATA_SHARED_DATA')
        if global_data is not None:
            paths.extend(global_data.split(':'))

        local_data = os.getenv('NIDATA_PATH')
        if local_data is not None:
            paths.extend(local_data.split(':'))

        paths.append(os.path.expanduser('~/nidata_path'))

    if verbose > 2:
        print('Dataset search paths: %s' % paths)

    # Check if the dataset exists somewhere
    for path in paths:
        path = os.path.join(path, dataset_name)
        if os.path.islink(path):
            # Resolve path
            path = readlinkabs(path)
        if os.path.exists(path) and os.path.isdir(path):
            if verbose > 1:
                print('\nDataset found in %s\n' % path)
            return path

    # If not, create a folder in the first writeable directory
    errors = []
    for path in paths:
        path = os.path.join(path, dataset_name)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                if verbose > 0:
                    print('\nDataset created in %s\n' % path)
                return path
            except Exception as exc:
                short_error_message = getattr(exc, 'strerror', str(exc))
                errors.append('\n -{0} ({1})'.format(
                    path, short_error_message))

    raise OSError('Nilearn tried to store the dataset in the following '
                  'directories, but:' + ''.join(errors))


class Dataset(object):
    __metaclass__ = DependenciesMeta
    dependencies = []

    def __init__(self, data_dir=None):
        class_path = os.path.dirname(inspect.getfile(self.__class__))

        self.name = os.path.basename(class_path)
        self.modality = os.path.basename(os.path.dirname(class_path))  # assume
        self.description = get_dataset_descr(ds_path=class_path,
                                             ds_name=self.name)

        self.data_dir = get_dataset_dir(self.name, data_dir=data_dir)

        self.fetcher = getattr(self, 'fetcher', None)

    def fetch(self, n_subjects=1, force=False, check=False, verbose=1):
        raise NotImplementedError()


class HttpDataset(Dataset):
    def __init__(self, data_dir=None):
        """
        """
        from ..fetchers import HttpFetcher  # avoid circular import
        super(HttpDataset, self).__init__(data_dir=data_dir)
        self.fetcher = HttpFetcher(data_dir=self.data_dir)
