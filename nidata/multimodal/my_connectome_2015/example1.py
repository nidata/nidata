# from [AN IMPORT PATH] import [A CLASS]
from nidata.multimodal import MyConnectome2015Dataset

# runs the member function 'fetch' from the class 'Laumann2015Dataset'
dataset = MyConnectome2015Dataset().fetch(data_types=['functional'],
                                          session_ids=range(2, 13))
print(dataset)

from nilearn.plotting import plot_anat
from nilearn.image import index_img
from matplotlib import pyplot as plt
plot_anat(index_img(dataset['functional'][0], 0))
plt.show()
