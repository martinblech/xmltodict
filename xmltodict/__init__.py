"""xmltodict"""
__license__ = 'MIT'
__version__ = '0.9.3'

__author__ = 'Martin Blech'
__email__ = 'martinblech@gmail.com'
__url__ = 'https://github.com/martinblech/xmltodict'

from xmltodict.xmltodict import parse
from xmltodict.xmltodict import unparse

__all__ = [
    parse.__name__,
    unparse.__name__,
]
