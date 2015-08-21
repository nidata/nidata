import os
import nibabel
import sys
from matplotlib import pyplot as plt  # we need to call plt.show()
from nilearn.plotting import plot_stat_map
from nilearn.image import mean_img
from sklearn.datasets.base import Bunch
import os
import pandas as pd
import numpy as np
from nilearn.masking import compute_epi_mask
from nilearn.plotting import plot_roi
from nilearn.input_data import NiftiMasker

sys.path.append('E:/gitclone/nidata/')

from nidata.functional.my_dataset.datasets import MyDatasets

data_dict = MyDatasets().fetch()
pc_dir = 'C:\Users\oferg_000/nidata_path\my_dataset'
func_dirs = ['task001_run001','task001_run002','task002_run001','task002_run002']
n_subjects = 14
num_sec = 468
model_dict = dict()
for func_dir in func_dirs:
	for j in range(1,3):
		model_files = [
				os.path.join(pc_dir,'ds052','sub%03d' % i, 'model\model001\onsets', func_dir, 'cond%03d.txt' % j)
				for i in range(1, n_subjects+1)			
				if not i==11
		]
		model_dict[func_dir+'_cond%d' %j] =  model_files
#print(model_dict.keys())
n_scans = 128
tr = 2.4
# input paradigm information
#frametimes = np.linspace(0, (n_scans - 1) * tr, n_scans)
#print frametimes
# conditions are 0 1 0 1 0 1 ...
#conditions = np.arange(20) % 2
#print conditions
#model_dict = Bunch(model = model_files)



for func_dir in func_dirs:
	for model_i in model_dict[func_dir+'_cond1']:
		cond1 = pd.read_csv(model_i, sep='\t', header=None)
		cond2 = pd.read_csv(model_i[:-5]+'2.txt', sep='\t', header=None)
		cond1 = cond1[0].as_matrix().tolist()
		cond2 = cond2[0].as_matrix().tolist()
		cnd_c1 = 0
		cnd_c2 = 0
		conditions = np.zeros(len(cond1)+len(cond2))
		for counter in range(0,len(cond1)+len(cond2)-1):
			if cond1[cnd_c1] < cond2[cnd_c2]:
				conditions[counter] = 1
				cnd_c1 += 1
			else:
				conditions[counter] = 2
				cnd_c2 += 1
		print conditions

	#cond1 = pd.read_csv(model_dict[func_dir+'_cond1'], sep='\t', header=None)
	#cond2 = pd.read_csv(model_dict[func_dir+'_cond2'], sep='\t', header=None)
	
	"""

	"""
	
	
	
"""
for func_dir in func_dirs:
	for j in range
for model_i in model_dict['task001_run001_cond1']:
	vari2 = pd.read_csv(model_i, sep='\t', header=None)
	print vari2[0].as_matrix().tolist()


counter = 0
for func_file in data_dict['func']:
	counter += 1
	if counter < 2:
		img = nibabel.load(os.path.join(pc_dir,func_file))
		mask_img = compute_epi_mask(img)
		plot_roi(mask_img, mean_img(img))	
plt.show()
#	plot_stat_map(mean_img(img))	
#plt.show()
	#print(img.get_data().shape)
#for anat_file in data_dict['anat']:
#	img = nibabel.load(os.path.join(pc_dir,anat_file))
#	plot_stat_map(mean_img(img))
#plt.show()
#print(data_dict.keys())
"""

