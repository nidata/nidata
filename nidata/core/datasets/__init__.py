"""
"""
from ..objdep import DependenciesMeta


class Dataset(object):
    __metaclass__ = DependenciesMeta
    dependencies = []

    def fetch(self, n_subjects=1, force=False, check=False, verbosity=1):
        raise NotImplementedError()
