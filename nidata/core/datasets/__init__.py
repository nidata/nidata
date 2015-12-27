"""
"""
import inspect
import os
import os.path as op

from six import with_metaclass

from ..objdep import DependenciesMeta


def readlinkabs(link):
    """
    Return an absolute path for the destination
    of a symlink
    """
    path = os.readlink(link)
    if op.isabs(path):
        return path
    return op.join(op.dirname(link), path)


def get_dataset_descr(ds_path, ds_name):
    rst_path = op.join(ds_path, ds_name + '.rst')
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

        paths.append(op.expanduser('~/nidata_path'))

    if verbose > 2:
        print('Dataset search paths: %s' % paths)

    # Check if the dataset exists somewhere
    for path in paths:
        path = op.join(path, dataset_name)
        if op.islink(path):
            # Resolve path
            path = readlinkabs(path)
        if op.exists(path) and op.isdir(path):
            if verbose > 1:
                print('\nDataset found in %s\n' % path)
            return path

    # If not, create a folder in the first writeable directory
    errors = []
    for path in paths:
        path = op.join(path, dataset_name)
        if not op.exists(path):
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


class Dataset(with_metaclass(DependenciesMeta, object)):
    dependencies = []

    def __init__(self, data_dir=None):
        class_path = op.dirname(inspect.getfile(self.__class__))

        self.name = op.basename(class_path)
        self.modality = op.basename(op.dirname(class_path))  # assume
        self.description = get_dataset_descr(ds_path=class_path,
                                             ds_name=self.name)

        self.data_dir = get_dataset_dir(self.name, data_dir=data_dir)
        self.fetcher = getattr(self, 'fetcher', None)  # set to *something*.

    def clean_data_directory(self):
        """ Function that guarantees a data directory."""

        if os.path.exists(self.data_dir):
            os.remove(self.data_dir)
        os.makedirs(self.data_dir)

    def fetch(self, force=False, verbose=1, *args, **kwargs):
        if force:
            self.clean_data_directory()
        return self.fetcher.fetch(verbose=verbose, *args, **kwargs)


class FetcherFunctionMeta(DependenciesMeta):
    """ Define fetcher_function; it will reset class docstring."""

    def __new__(cls, name, parents, props):
        new_cls = DependenciesMeta.__new__(cls=cls, name=name, parents=parents,
                                           props=props)
        if hasattr(new_cls, 'fetcher_function'):
            # Create a fetcher just to parse off the docs.
            from ..fetchers import FetcherFunctionFetcher
            try:
                fetcher = FetcherFunctionFetcher(new_cls.fetcher_function)
            except:
                pass  # won't be able to have docs for that function...
            else:
                new_cls.__doc__ = fetcher.__doc__
        return new_cls


class FetcherFunctionDataset(with_metaclass(FetcherFunctionMeta, Dataset)):

    def __init__(self, data_dir=None):
        super(FetcherFunctionDataset, self).__init__(data_dir=data_dir)
        from ..fetchers import FetcherFunctionFetcher
        self.fetcher = FetcherFunctionFetcher(self.fetcher_function)


class NilearnDataset(FetcherFunctionDataset):
    dependencies = ['nilearn'] + FetcherFunctionDataset.dependencies


class NistatsDataset(FetcherFunctionDataset):
    dependencies = ['nistats'] + FetcherFunctionDataset.dependencies


class HttpDataset(Dataset):
    def __init__(self, data_dir=None):
        """
        """
        from ..fetchers import HttpFetcher  # avoid circular import
        super(HttpDataset, self).__init__(data_dir=data_dir)
        self.fetcher = HttpFetcher(data_dir=self.data_dir)
