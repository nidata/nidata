# from [AN IMPORT PATH] import [A CLASS]
from nidata.functional.my_connectome_2015.datasets import MyConnectome2015Dataset

# runs the member function 'fetch' from the class 'Laumann2015Dataset'
dataset = MyConnectome2015Dataset().fetch(n_sessions=5)

from nilearn.plotting import plot_anat
plot_anat()