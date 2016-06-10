# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 1
_version_micro = ''  # use '' for first of series, number for 1 and above
_version_extra = 'dev'

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: MIT License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

# Description should be a one-liner:
description = "nidata: curated access to neuroimaging data"
# Long description will go up on the pypi page
long_description = """

Nidata
======


License
=======
``nidata`` is licensed under the terms of the MIT license. See the file
"LICENSE" for information on the history of this software, terms & conditions
for usage, and a DISCLAIMER OF ALL WARRANTIES.

All trademarks referenced herein are property of their respective holders.

Copyright (c) 2015, nidata contributors.
"""

NAME = "nidata"
MAINTAINER = "Ben Cipollini"
MAINTAINER_EMAIL = "bcipolli@ucsd.edu"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://github.com/nidata/nidata"
DOWNLOAD_URL = ""
LICENSE = "MIT"
AUTHOR = "Ben Cipollini "
AUTHOR_EMAIL = "bcipolli@ucsd.edu"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGES = ['nidata',
            'nidata.anatomical',
            'nidata.atlas',
            'nidata.core',
            'nidata.core._external',
            'nidata.core._utils',
            'nidata.diffusion',
            'nidata.core.fetchers',
            'nidata.localizer',
            'nidata.multimodal',
            'nidata.resting_state',
            'nidata.task']
PACKAGE_DATA = {}
REQUIRES = ["numpy", "nibabel", "six"]
