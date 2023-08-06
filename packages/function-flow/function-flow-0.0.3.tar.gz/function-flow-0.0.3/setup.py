import os
import re
import shutil

from setuptools import find_packages, setup
from setuptools.command.install import install
from subprocess import getoutput

install_requires = [
    'google-api-core>=1.22.1',
    'google-api-python-client>=1.9.3',
    'google-cloud-core>=1.4.4',
    'google-cloud-firestore>=1.6.2',
    'google-cloud-pubsub>=1.0.2',
    'google-cloud-storage>=1.38.0',
    'google-cloud-tasks>=2.0.0',
]

setup(
    name='function-flow',
    version='0.0.3',  # expected format is one of x.y.z.dev0, or x.y.z.rc1 or x.y.z (no to dashes, yes to dots)
    author='Chi Zhang',
    author_email='chii@google.com',
    description='Function Flow - workflow management on Google Cloud Functions',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='Apache',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    extras_require={},
    python_requires='>=3.6.0',
    install_requires=install_requires)
