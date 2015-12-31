#!/usr/bin/python3

"""
onedrive-d
==========

A Microsoft OneDrive client for Linux.

:copyright: (c) Xiangyu Bu
:license: GPL 3.0
"""

import sys

from setuptools import setup


setup_requires = []

install_requires = [
    'setuptools',
    'requests>2.0.0',
    'zgitignore>=0.7.1'
]

requires = [
    'iso8601',
    'clint',
    'requests',
    'send2trash',
    'zgitignore'
]

test_requires = [
    'python-dateutil',
    'requests-mock>=0.6',
    'coverage>=3.7.1'
]

python_version = sys.version_info

if python_version[0] < 3:
    raise Exception('This package does not support Python 2.x. Please run with Python 3.x and newer instead.')

if python_version[0] == 3 and python_version[1] == 2:
    test_requires.append('mock>=1.3.0')

setup(
    name='onedrive_d',
    version='2.0.0',
    author='Xiangyu Bu',
    author_email='xybu92@live.com',
    description='A Microsoft OneDrive client for Linux',
    license='GPL 3.0',
    long_description=open('README.md').read(),
    packages=[
        'onedrive_d'
    ],
    package_data={
        'onedrive_d': ['lang/*', 'data/*']
    },
    entry_points={
        'console_scripts': [
            'onedrived = onedrive_d.cli.cli_main:main',
            'onedrived-pref = onedrive_d.cli.pref_main:main'
        ]
    },
    setup_requires=setup_requires,
    install_requires=install_requires,
        requires=requires,
    tests_require=test_requires,
        test_suite='tests',
    include_package_data=True,
    url='https://github.com/xybu/onedrive-d',
        zip_safe=False
)
