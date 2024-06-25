from setuptools import setup

import icvlp

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='icvlp-dataset',
    version=icvlp.__version__,
    packages=['icvlp'],
    url='https://github.com/risangbaskoro/icvlp-dataset',
    author='risangbaskoro',
    author_email='contact@risangbaskoro.com',
    description='Indonesian Commercial Vehicle License Plate dataset',
    long_description=long_description,
    long_description_content_type='text/markdown',
    requires_python=">=3.9",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
    ]
)
