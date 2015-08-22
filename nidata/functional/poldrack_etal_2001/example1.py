from nidata.functional.poldrack_etal_2001.datasets import PoldrackEtal2001Dataset
pold_dataset = PoldrackEtal2001Dataset()
data_dict = pold_dataset.fetch(preprocess_data=True)

