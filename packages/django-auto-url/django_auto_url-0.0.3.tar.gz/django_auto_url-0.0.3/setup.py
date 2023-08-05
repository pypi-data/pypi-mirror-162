# -*- coding: utf-8 -*-

import os.path
from codecs import open

from setuptools import setup, find_packages

REQUIRED = [
    'Django',
]

# find the location of this file
this_directory = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(
    name='django_auto_url',
    version=version,
    packages=find_packages(),
    url='https://gitlab.com/thht_django/django_auto_url',
    license='GPLv3',
    author='Thomas Hartmann',
    author_email='thomas.hartmann@th-ht.de',
    description='Automagic urls for Django',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='Django URL'
)
