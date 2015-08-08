#!/usr/bin/python3

"""
onedrive-d
==========

A Microsoft OneDrive client for Linux.

:copyright: (c) Xiangyu Bu
:license: GPL 3.0
"""

from setuptools import setup

setup_requires = []

install_requires = [
    'ciso8601>=1.0.1',
    'requests>=2.0'
]

test_requires = [
    'requests-mock>=0.6',
    'coverage>=3.7.1'
]

setup(
    name='onedrive_d',
    version='2.0.0',
    author='Xiangyu Bu',
    author_email='xybu92@live.com',
    description='A Microsoft OneDrive client for Linux',
    license='GPL 3.0',
    long_description=open('README.md').read(),
    packages=[
        'onedrive_d',
        'onedrive_d.api',
        'onedrive_d.cli',
        'onedrive_d.common',
        'onedrive_d.store',
        'onedrive_d.tests',
        'onedrive_d.tests.api',
        'onedrive_d.tests.common',
        'onedrive_d.ui'
    ],
    package_data={
        'onedrive_d': ['lang/*.json'],
        'onedrive_d.tests': ['data/*.json']
    },
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='onedrive_d.tests',
    include_package_data=True,
    url='https://github.com/xybu/onedrive-d',
    zip_safe=False
)
