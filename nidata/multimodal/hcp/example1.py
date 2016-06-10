import os

from nidata.multimodal import HcpDataset
# 'aws' == amazon web services also OK
dataset = HcpDataset(fetcher_type='aws')

# only fetch anatomical files.
files = dataset.fetch(n_subjects=1, data_types=['diff'])
for fil in files:
    print(fil)

import matplotlib
import matplotlib.pyplot as plt

import nibabel as nib

import dipy.reconst.dti as dti
import dipy.core.gradients as grad
gtab = grad.gradient_table(files[0], files[1])
data = nib.load(files[2]).get_data()
model = dti.TensorModel(gtab)

fit = model.fit(data)
plt.matshow(fit.fa[..., fit.fa.shape[-1]//2], cmap=matplotlib.cm.bone)
plt.show()
