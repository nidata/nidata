# *- encoding: utf-8 -*-
# Author: Ofer Groweiss
# License: simplified BSD

from collections import OrderedDict

from ...core.datasets import AuthenticatedHttpDataset


class PINGDataset(AuthenticatedHttpDataset):
    """
    TODO: PING docstring.
    """
    dependencies = OrderedDict(
        [(mod, mod) for mod in (['requests', 'pandas'] +
                                AuthenticatedHttpDataset.dependencies)],
        ping='git+https://github.com/guruucsd/PING')
    USERNAME_ENV_VAR = 'PING_USERNAME'
    PASSWD_ENV_VAR = 'PING_PASSWORD'

    def fetch(self, n_subjects=1,
              url=None, resume=True, force=False, verbose=1):
        if not hasattr(self, 'dataset'):
            from ping.ping.data import PINGData
            self.dataset = PINGData(username=self.username, passwd=self.passwd,
                                    data_dir=self.data_dir)
        return self.dataset.data_dict
