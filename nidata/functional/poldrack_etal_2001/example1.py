# import the world
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
from nipy.labs.viz import plot_map, cm
from nilearn.input_data import NiftiMasker
from nilearn.image import index_img
import nipy.modalities.fmri.design_matrix as dm
#from nipy.labs.utils.simul_multisubject_fmri_dataset import surrogate_4d_dataset
from nipy.modalities.fmri.glm import GeneralLinearModel
from nipy.modalities.fmri.glm import FMRILinearModel
from nipy.modalities.fmri.experimental_paradigm import EventRelatedParadigm
sys.path.append('E:/gitclone/nidata/')
np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})
from nidata.functional.poldrack_etal_2001.datasets import PoldrackEtal2001Dataset

# fetch fmri data
data_dict = PoldrackEtal2001Dataset().fetch()
#### BUILD MODEL MATRIX
pc_dir = 'C:/Users/oferg_000/nidata_path/my_dataset'
pc_dir = '/Users/bcipolli/datasets/poldrack_etal_2001'

func_dirs = ['task001_run001','task001_run002','task002_run001','task002_run002']
n_subjects = 14
func_file_dict = dict()
# build dictionary for different scans
model_dict = dict()
for func_dir in func_dirs:
	func_file = filter(lambda pth: func_dir in pth, data_dict['func'])
	func_file_dict[func_dir] = func_file
	for j in range(1,3):
		model_files = [
				os.path.join(pc_dir,'ds052','sub%03d' % i, 'model/model001/onsets', func_dir, 'cond%03d.txt' % j)
				for i in range(1, n_subjects+1)			
				if not i==11
		]
		model_dict[func_dir+'_cond%d' %j] =  model_files
# scan params		
n_scans = 225
tr = 2
hrf_model = 'canonical'
frametimes = np.linspace(0, (n_scans - 1) * tr, n_scans)
# build design matrix and compute GLM
for func_dir in func_dirs:
	for model_i,func_i in zip(model_dict[func_dir+'_cond1'],func_file_dict[func_dir]):
		cond1 = pd.read_csv(model_i, sep='\t', header=None)
		cond2 = pd.read_csv(model_i[:-5]+'2.txt', sep='\t', header=None)
		cond1 = cond1[0].as_matrix().tolist()
		cond2 = cond2[0].as_matrix().tolist()
		onsets = np.sort(cond1+cond2)
		cond1_q = cond1
		cond2_q = cond2
		num_cond = len(cond1)+len(cond2)
		conditions = np.zeros((num_cond,),  dtype=np.int)
		cnd_c1 = cond1_q.pop(0)	
		cnd_c2 = cond2_q.pop(0)	
		for counter in range(0,num_cond):
			if  cnd_c1 < cnd_c2:
				conditions[counter] = 1
				cnd_c1 = 100000
				if cond1_q != []:
					cnd_c1 = cond1_q.pop(0)
			else:
				conditions[counter] = 2
				cnd_c2 = 100000
				if cond2_q != []:	
					cnd_c2 = cond2_q.pop(0)				
		paradigm = EventRelatedParadigm(conditions, onsets)
		design_mat = dm.make_dmtx(frametimes, paradigm, drift_model='cosine', hfcut=n_scans, hrf_model=hrf_model)
		img = nibabel.load(os.path.join(pc_dir,func_i))
		mask_img = compute_epi_mask(img)
		fmri_glm = FMRILinearModel(img, design_mat.matrix, mask=mask_img)
		fmri_glm.fit(do_scaling=True, model = 'ar1')
		
		beta_hat = fmri_glm.glms[0].get_beta()  # Least-squares estimates of the beta
		variance_hat = fmri_glm.glms[0].get_mse()  # Estimates of the variance
		mask = fmri_glm.mask.get_data() > 0
		# output beta images
		dim = design_mat.matrix.shape[1]
		beta_map = np.tile(mask.astype(np.float)[..., np.newaxis], dim)
		beta_map[mask] = beta_hat.T
		beta_image = nibabel.Nifti1Image(beta_map, fmri_glm.affine)
		beta_image.get_header()['descrip'] = ('Parameter estimates of the localizer dataset')

		# import pdb; pdb.set_trace()
		
		# Create a snapshots of the variance image contrasts
		for ci in [0, 1]:
			plot_stat_map(index_img(beta_image, ci),
					 cmap=cm.hot_black_bone,
					 black_bg=True,
					 vmax=100., alpha=0.9,
					 title='Beta %d map' % ci)
		plt.show()
		
"""
fig = plt.figure(figsize=(10, 6))
ax = fig.gca()
design_mat.show(ax=ax)
ax.set_title('Block-related design matrix', fontsize=12)
plt.show()
"""
		


	
	
	
	


"""
counter = 0
for func_file in data_dict['func']:
	counter += 1
	if counter < 2:
		img = nibabel.load(os.path.join(pc_dir,func_file))
		print img
		mask_img = compute_epi_mask(img)
		plot_roi(mask_img, mean_img(img))		
plt.show()
"""
#	plot_stat_map(mean_img(img))	
#plt.show()
	#print(img.get_data().shape)
#for anat_file in data_dict['anat']:
#	img = nibabel.load(os.path.join(pc_dir,anat_file))
#	plot_stat_map(mean_img(img))
#plt.show()
#print(data_dict.keys())


