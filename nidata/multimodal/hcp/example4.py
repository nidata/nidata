from nidata.multimodal import HcpDataset
from nilearn.plotting import plot_stat_map
from nilearn.image import mean_img, math_img
import matplotlib.pyplot as plt

# 'aws' == amazon web services also OK
dataset = HcpDataset(fetcher_type='aws')

# only fetch anatomical files.
files = dataset.fetch(n_subjects=2, data_types=['task'])

# Filter subject 2 only
nii_files = filter(lambda fil: fil and '100408' in fil and fil.endswith('_LR.nii.gz'), files)

tasks = ['emotion', 'gambling', 'language', 'motor', 'social', 'wm']

# Compute mean images
mean_imgs = dict()
for task in tasks:
    mean_imgs[task] = mean_img(filter(lambda fil: task.upper() in fil, nii_files)[0])


# Now make a matrix.
fh = plt.figure(figsize=(18, 10))
for ti1, task1 in enumerate(tasks):
    for ti2 in range(0, ti1 - 1):
        task2 = tasks[ti2]
        ax = fh.add_subplot(5, 5, (ti1 - 1) * 5 + ti2 + 1)
        img = math_img("img1 - img2", img1=mean_imgs[task1], img2=mean_imgs[task2])
        plot_stat_map(
            img,
            title='%s - %s' % (task1, task2),
            symmetric_cbar=True,
            black_bg=True,
            display_mode='yz',
            axes=ax)
plt.show()
# Print out a matrix
import pdb; pdb.set_trace()
