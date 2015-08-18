import sys
sys.path.append('E:/gitclone/nidata/')
from nidata.functional.my_dataset.datasets import MyDatasets

print(MyDatasets().fetch())
