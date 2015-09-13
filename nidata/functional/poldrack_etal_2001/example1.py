from matplotlib import pyplot as plt

import nibabel as nb
import nireg as nr
from nidata.functional.poldrack_etal_2001.datasets import PoldrackEtal2001Dataset
from nilearn.plotting import plot_stat_map
from nipy.labs.viz import cm

pold_dataset = PoldrackEtal2001Dataset()
data_dict = pold_dataset.fetch(preprocess_data=True)
print data_dict['anat'][0:2]
print data_dict['func'][0:2]

func = nb.load(data_dict['func'][0])
anat = nb.load(data_dict['anat'][0])

reg = nr.HistogramRegistration(func, anat)
trns = reg.optimize('rigid')
func_trans = nr.resample(func, trns.inv(), reference=anat)

fh = plt.figure()
plot_stat_map(func,
              cmap=cm.hot_black_bone,
              black_bg=True,
              vmax=100., alpha=0.9,
              title='Before rigid registration',
              bg_img=anat,
              axes=fh.add_subplot(2, 1, 1))
plot_stat_map(func_trans,
              cmap=cm.hot_black_bone,
              black_bg=True,
              vmax=100., alpha=0.9,
              title='After rigid registration',
              bg_img=anat,
              axes=fh.add_subplot(2, 1, 2))
plt.show()
