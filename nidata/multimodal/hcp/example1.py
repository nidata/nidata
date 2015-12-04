import os

from nidata.multimodal import HcpDataset

if os.environ.get('NIDATA_USERNAME') is None:
    raise Exception("Must define NIDATA_USERNAME & NIDATA_PASSWD environment "
                    "variables, or pass username & password to 'fetch' below.")

print(HcpDataset().fetch(n_subjects=1, data_types=['anat']))
