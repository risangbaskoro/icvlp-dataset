from icvlp.__version__ import __version__ as ver
from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

# TODO: Add license.

setup(
    name='icvlp-dataset',
    version=ver,
    packages=['icvlp'],
    url='https://github.com/risangbaskoro/icvlp-dataset',
    author='risangbaskoro',
    author_email='contact@risangbaskoro.com',
    description='Indonesian Commercial Vehicle License Plate dataset',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
