# onedrive-d

__The previous version has been moved to https://github.com/xybu/onedrive-d-old.__

__This repository is still under active development and the program is not yet usable.__

<a href="https://travis-ci.org/xybu/onedrive-d" target="_blank">
    ![Travis CI](https://img.shields.io/travis/xybu/onedrive-d.svg "Travis CI")
</a>
[![License](https://img.shields.io/github/license/xybu/onedrive-d.svg "GNU GPL v3.0")](LICENSE)
<a href="https://coveralls.io/github/xybu/onedrive-d" target="_blank">
    ![Coverage Status](https://coveralls.io/repos/xybu/onedrive-d/badge.svg?service=github "Coveralls Status")
</a>
<a href="https://codeclimate.com/github/xybu/onedrive-d" target="_blank">
    ![Code Climate](https://img.shields.io/codeclimate/github/xybu/onedrive-d.svg "Code Climate GPA")
</a>

## Overview

`onedrive-d` is a Microsoft OneDrive client on Linux platforms. It allows a Linux user to sync with one or more
OneDrive Personal account by synchronizing each remote OneDrive repository with a designated local directory. __Note
that OneDrive for Business is not supported (see issue #1).__

## Pre-requisites

`onedrive-d` is written in Python 3 and does ___NOT___ run under Python 2.x. The package is tested for the following
Python versions: `3.2`, `3.3`, `3.4`, `3.5-dev`.

To check if you have the correct Python interpreter, run

```bash
$ python3 --version
```

Because the CLI runs as a Linux daemon and some dependency packages are written in CPython, some system-level packages
are required: `python3-dev` (on Fedora / SUSE it is called `python3-devel`). If you do not have `gcc` installed, for
example, on Debian 8, you may also need to install the package `gcc`.

A low-level package required is `inotify-tools` (for most Linux distributes).

It is suggested that you install the latest version of `pip3` and `setuptools`:
```bash
# Download the latest pip package from source
$ wget -O- https://bootstrap.pypa.io/get-pip.py | sudo python3

# Use pip3 to upgrade setuptools
$ sudo pip3 install --upgrade setuptools
```

## Install

After properly setting up pre-requisites, run the following command to install the package:

```bash
# use sudo to install the package system-wide

# Install onedrive-d with no GUI support
$ python3 setup.py install

# Install onedrive-d with GUI
$ python3 setup.py install gui # TODO: finish this.
```

## Configure

### Authenticate OneDrive accounts

TBA.

### Link local directories

TBA.

### Setup preferemces

TBA.

### Use ignore list

(Refer to this document.)[docs/ignore_list.md]

## Uninstall

You will need `pip3` to properly uninstall the package.

```
$ pip3 uninstall onedrive_d
```

## Support

Please beware that the program comes with absolutely NO WARRANTY, and resources for tech support are extremely limited.

To report a bug or ask a question, create an issue on the repository.

You can also contact @xybu by messages or email.
