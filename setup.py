"""Setup script for xmltodict"""
from setuptools import setup
from setuptools import find_packages

import xmltodict

setup(
    name='xmltodict',
    version=xmltodict.__version__,
    description=xmltodict.__doc__,
    author=xmltodict.__author__,
    author_email=xmltodict.__email__,
    url=xmltodict.__url__,
    license=xmltodict.__license__,
    platforms=['all'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    packages=find_packages()
)
