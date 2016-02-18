import os
if os.environ.get('NIDATA_HCP_USERNAME') is None:
    raise Exception("Must define NIDATA_USERNAME and NIDATA_HCP_PASSWD "
                    "environment variables, or pass username & passwd "
                    " to HcpDataset() below.")

from nidata.multimodal import HcpDataset
# 'aws' == amazon web services also OK
dataset = HcpDataset(fetcher_type='http')

# only fetch anatomical files.
files = dataset.fetch(n_subjects=1, data_types=['anat'])
for fil in files:
    print fil
