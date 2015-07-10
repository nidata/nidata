"""
"""
import os

from ..objdep import DependenciesMeta


def get_dataset_descr(ds_path, ds_name):
    fname = ds_name

    try:
        with open(os.path.join(ds_path, fname + '.rst'))\
                as rst_file:
            descr = rst_file.read()
    except IOError:
        print("Warning: Could not find dataset description.")
        descr = ''

    return descr


class Dataset(object):
    __metaclass__ = DependenciesMeta
    dependencies = []

    def __init__(self):
        self.name = os.path.basename(__file__)

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.description = get_dataset_descr(ds_path=cur_dir,
                                             ds_name=self.name)

    def fetch(self, n_subjects=1, force=False, check=False, verbosity=1):
        raise NotImplementedError()
