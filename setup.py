#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) University of California Regeants
# Distributed under the terms of the Modified BSD License.
#
# ----------------------------------------------------------------------------
from __future__ import print_function

from distutils.core import setup

setup_args = dict(
    name='nersc_sdn',
    version='0.1',
    packages=['nersc_sdn'],
    scripts=['cli.py','initdb.py'],
    data_files=[('/etc', [ 'nersc_sdn.conf.example' ]),
                ('/usr/sbin', ['job_server.py'])],
    description="""NERSC's SDN API service to dynamically create routes to HPC compute nodes""",
    long_description="""NERSC's SDN API service to dynamically create routes to HPC compute nodes""",
    author="Shane Canon",
    author_email="scanon@lbl.gov",
    url="http://www.nersc.gov",
    license="BSD",
    platforms="Linux, Mac OS X",
    keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)

def main():
    setup(**setup_args)

if __name__ == '__main__':
    main()
