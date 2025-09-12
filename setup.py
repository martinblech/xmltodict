#!/usr/bin/env python
from setuptools import setup

import xmltodict

with open('README.md', 'rb') as f:
    long_description = f.read().decode('utf-8')


setup(
    name="xmltodict",
    version=xmltodict.__version__,
    description=xmltodict.__doc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=xmltodict.__author__,
    author_email="martinblech@gmail.com",
    url="https://github.com/martinblech/xmltodict",
    license=xmltodict.__license__,
    platforms=["all"],
    python_requires=">=3.9",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    py_modules=["xmltodict"],
    tests_require=["nose2", "coverage"],
)
