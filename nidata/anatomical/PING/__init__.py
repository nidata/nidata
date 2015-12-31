# *- encoding: utf-8 -*-
# Author: Ofer Groweiss
# License: simplified BSD

import os
from collections import OrderedDict

from ...core.datasets import HttpDataset


class AuthenticatedHttpDataset(HttpDataset):
    USERNAME_ENV_VAR = None
    PASSWD_ENV_VAR = None

    def __init__(self, data_dir=None, username=None, passwd=None):
        if username is None and not os.environ.get(self.USERNAME_ENV_VAR):
            raise ValueError("username/passwd must be passed in, or %s/%s "
                             "environment variables must be set." % (
                                 self.USERNAME_ENV_VAR, self.PASSWD_ENV_VAR))
        self.username = username
        self.passwd = passwd
        super(AuthenticatedHttpDataset, self).__init__(data_dir=data_dir)


class PINGDataset(AuthenticatedHttpDataset):
    """
    TODO: PING docstring.
    """
    dependencies = OrderedDict(
        [(mod, mod) for mod in HttpDataset.dependencies],
        ping='git+https://github.com/guruucsd/PING')
    USERNAME_ENV_VAR = 'PING_USERNAME'
    PASSWD_ENV_VAR = 'PING_PASSWD'

    def fetch(self, n_subjects=1,
              url=None, resume=True, force=False, verbose=1):
        if not hasattr(self, 'dataset'):
            from ping.ping.data import PINGData
            self.dataset = PINGData(username=self.username, passwd=self.passwd,
                                    data_dir=self.data_dir)
        return self.dataset.data_dict
