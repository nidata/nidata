import os
# activating a package

from nidata.functional.laumann_etal_2015.datasets import Laumann2015Dataset
# from [AN IMPORT PATH] import [A CLASS]

print (Laumann2015Dataset().fetch())
# runs the member function 'fetch' from the class 'Laumann2015Dataset'