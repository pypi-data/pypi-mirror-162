#!/usr/bin/env python

sdict = {
    'name': 'multi_request',
    'version': "0.0.2",
    'packages': ['multi_request'],
    'zip_safe': False,
    'install_requires': [
        'pandas==1.3.4',
        'requests==2.26.0'
    ],
    'author': 'Zhao Xu',
    'classifiers': [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python'],
    'scripts': ['multi_request/mreq']
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
