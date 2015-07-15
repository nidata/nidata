import matplotlib.pyplot as plt
import nibabel as nib
from nilearn.plotting import plot_stat_map
from nilearn.image import index_img

from nidata.atlas import HaxbyEtal2011Dataset

dset = HaxbyEtal2011Dataset().fetch(n_subjects=1)
func_img = nib.load(dset['func'][0])
plot_stat_map(index_img(func_img, 0))
plt.show()
