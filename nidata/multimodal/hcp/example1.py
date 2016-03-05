import os

from nidata.multimodal import HcpDataset
# 'aws' == amazon web services also OK
dataset = HcpDataset(fetcher_type='aws', profile_name='hcp')

# only fetch anatomical files.
files = dataset.fetch(n_subjects=1, data_types=['diff'])
for fil in files:
    print fil
