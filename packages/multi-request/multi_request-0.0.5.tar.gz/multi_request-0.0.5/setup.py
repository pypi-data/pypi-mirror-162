#!/usr/bin/env python


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()  
    long_description=long_description
    long_description_content_type="text/markdown"


sdict = {
    'name': 'multi_request',
    'version': "0.0.5",
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
        'Programming Language :: Python'
    ],
    'long_description': long_description,
    'long_description_content_type': long_description_content_type
}



try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
