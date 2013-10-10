#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
import xmltodict

setup(name='xmltodict',
      version=xmltodict.__version__,
      description=xmltodict.__doc__,
      author=xmltodict.__author__,
      author_email='martinblech@gmail.com',
      url='https://github.com/martinblech/xmltodict',
      license=xmltodict.__license__,
      platforms=['all'],
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ],
      py_modules=['xmltodict'],
      setup_requires=['nose>=1.0', 'coverage'],
      )
