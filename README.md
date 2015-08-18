## nidata - neuroimaging dataset download and formatting

[![Join the chat at https://gitter.im/nidata/nidata](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/nidata/nidata?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


### Goals

The goal of this tool is to offer a simple interface for downloading, storing, and getting access to neuroimaging datasets.  We want to:
* Decrease the amount of time spent by data scientists in accessing new datasets
* Decrease the difficulty of scientists in sharing their data with the world
* Increase the visibility of available data


### Data types

The types of data we wish to expose include:
* MRI / fMRI / rsMRI / dMRI
* EEG / ERP / MEG / ECoG


### Known data sources

Not all data sources have been implemented. Our list of known data sources can be found here:
https://github.com/nidata/nidata/wiki/Data-sources

Current data sources will be available via the website, when implemented:
http://nidata.github.io/

### Dependencies

`nidata` is tested in Python 2.6, 2.7, and 3.4. The only package-level dependency is pip.

Individual datasets may have package dependencies for downloads or examples. If so, `nidata` attempts to install them via pip. These packages include:
* [nilearn](https://github.com/nilearn/nilearn/) - Machine learning for neuroimaging, contains generic download tools and logic for accessing fMRI datasets
* [nibabel](https://github.com/nibabel/nibabel/) - Tools for accessing many formats of MRI data


### Installation

`sudo pip install git+https://github.com/nidata/nidata`


### Usage

To run an example,
`python nidata/multimodal/hcp/example1.py`

To download data,
```python
from nidata.multimodal import HcpDataset
HcpDataset().fetch(n_subjects=1)

```


