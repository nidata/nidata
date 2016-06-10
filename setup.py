import os.path as op
from setuptools import setup, find_packages

# Get version and release info, which is all stored in nidata/version.py
ver_file = op.join('nidata', 'version.py')
with open(ver_file) as f:
    exec(f.read())

print(REQUIRES)
opts = dict(name=NAME,
            maintainer=MAINTAINER,
            maintainer_email=MAINTAINER_EMAIL,
            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            url=URL,
            download_url=DOWNLOAD_URL,
            license=LICENSE,
            classifiers=CLASSIFIERS,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            platforms=PLATFORMS,
            version=VERSION,
            packages=find_packages(),
            package_data=PACKAGE_DATA,
            install_requires=REQUIRES,
            zip_safe=False)


if __name__ == '__main__':
    setup(**opts)
