#!/usr/bin/python3

"""
onedrive-d
A Microsoft OneDrive client for Linux.

:copyright: (c) Xiangyu Bu
:license: GPLv3
"""

import sys

from setuptools import setup, find_packages

from onedrivee import __project__, __version__, __author__, __email__, __homepage__

setup_requires = [
    'setuptools'
]

install_requires = [
    'iso8601',
    'clint',
    'requests>2.0.0',
    'send2trash',
    'zgitignore>=0.7.1'
]

test_requires = [
    'python-dateutil',
    'requests-mock>=0.6',
    'coverage>=3.7.1'
]

readme = open('README.md').read()

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

python_version = sys.version_info

if python_version[0] < 3:
    raise Exception('This package does not support Python 2.x. Please run with Python 3.x and newer instead.')

if python_version[0] == 3 and python_version[1] == 2:
    test_requires.append('mock>=1.3.0')

setup(
        name=__project__,
        version=__version__,
        author=__author__,
        author_email=__email__,
        url=__homepage__,
        description='A Microsoft OneDrive client for Linux',
        license='GPLv3',
        long_description=readme,
        packages=packages,
        include_package_data=True,
        #package_data={
        #    'onedrivee': ['lang/*', 'data/*']
        #},
        entry_points={
            'console_scripts': [
                'onedrivee = onedrivee.main.cli_main:main',
                'onedrivee-pref = onedrivee.main.pref_main:main'
            ],
            'gui_scripts': []
        },
        setup_requires=setup_requires,
        install_requires=install_requires,
        tests_require=test_requires,
        test_suite='tests',
        zip_safe=False,
        requires=['clint', 'requests', 'iso8601', 'send2trash', 'zgitignore']
)
