from xmltodict import parse, unparse, OrderedDict

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import re
import collections

_HEADER_RE = re.compile(r'^[^\n]*\n')
def _strip(fullxml):
    return _HEADER_RE.sub('', fullxml)

class DictToXMLTestCase(unittest.TestCase):
    def test_root(self):
        obj = {'a': None}
        self.assertEqual(obj, parse(unparse(obj)))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))

    def test_simple_cdata(self):
        obj = {'a': 'b'}
        self.assertEqual(obj, parse(unparse(obj)))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))

    def test_cdata(self):
        obj = {'a': {'#text': 'y'}}
        self.assertEqual(obj, parse(unparse(obj), force_cdata=True))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))

    def test_attrib(self):
        obj = {'a': {'@href': 'x'}}
        self.assertEqual(obj, parse(unparse(obj)))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))

    def test_attrib_and_cdata(self):
        obj = {'a': {'@href': 'x', '#text': 'y'}}
        self.assertEqual(obj, parse(unparse(obj)))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))

    def test_list(self):
        obj = {'a': {'b': ['1', '2', '3']}}
        self.assertEqual(obj, parse(unparse(obj)))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))

    def test_multiple_roots(self):
        self.assertRaises(ValueError, unparse, {'a':'1', 'b':'2'})
        self.assertRaises(ValueError, unparse, {'a': ['1', '2', '3']})

    def test_nested(self):
        obj = {'a': {'b': '1', 'c': '2'}}
        self.assertEqual(obj, parse(unparse(obj)))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))
        obj = {'a': {'b': {'c': {'@a': 'x', '#text': 'y'}}}}
        self.assertEqual(obj, parse(unparse(obj)))
        self.assertEqual(unparse(obj), unparse(parse(unparse(obj))))

    def test_semistructured(self):
        xml = '<a>abc<d/>efg</a>'
        self.assertEqual(_strip(unparse(parse(xml))),
                         '<a><d></d>abcefg</a>')

    if hasattr(collections, 'OrderedDict'):
        def test_preprocessor(self):
            obj = {'a': OrderedDict((('b:int', [1, 2]), ('b', 'c')))}
            def p(key, value):
                try:
                    key, _ = key.split(':')
                except ValueError:
                    pass
                return key, value
            self.assertEqual(_strip(unparse(obj, preprocessor=p)),
                             '<a><b>1</b><b>2</b><b>c</b></a>')

    def test_preprocessor_skipkey(self):
        obj = {'a': {'b': 1, 'c': 2}}
        def p(key, value):
            if key == 'b':
                return None
            return key, value
        self.assertEqual(_strip(unparse(obj, preprocessor=p)),
                         '<a><c>2</c></a>')

    if hasattr(collections, 'OrderedDict'):
        def test_attr_order_roundtrip(self):
            xml = '<root a="1" b="2" c="3"></root>'
            self.assertEqual(xml, _strip(unparse(parse(xml))))

    def test_pretty_print(self):
        obj = {'a': {'b': {'c': 1}}}
        newl = '_newl_'
        indent = '_indent_'
        xml = ('<a>%(newl)s%(indent)s<b>%(newl)s%(indent)s%(indent)s<c>1</c>'
               '%(newl)s%(indent)s</b>%(newl)s</a>') % {
                   'newl': newl, 'indent': indent
               }
        self.assertEqual(xml, _strip(unparse(obj, pretty=True,
                                             newl=newl, indent=indent)))
