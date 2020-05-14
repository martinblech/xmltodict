#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import xmltodict

with open('README.md', 'rb') as f:
    long_description = f.read().decode('utf-8')


setup(name='xmltodict',
      version=xmltodict.__version__,
      description=xmltodict.__doc__,
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=xmltodict.__author__,
      author_email='martinblech@gmail.com',
      url='https://github.com/martinblech/xmltodict',
      license=xmltodict.__license__,
      platforms=['all'],
      python_requires='>=3.4',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Text Processing :: Markup :: XML',
      ],
      py_modules=['xmltodict'],
      tests_require=['nose2', 'coverage'],
      )
