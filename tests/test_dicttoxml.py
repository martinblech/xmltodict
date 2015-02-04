import sys
from xmltodict import parse, unparse, OrderedDict

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import re
import collections
from textwrap import dedent

IS_JYTHON = sys.platform.startswith('java')

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

    def test_no_root(self):
        self.assertRaises(ValueError, unparse, {})

    def test_multiple_roots(self):
        self.assertRaises(ValueError, unparse, {'a': '1', 'b': '2'})
        self.assertRaises(ValueError, unparse, {'a': ['1', '2', '3']})

    def test_no_root_nofulldoc(self):
        self.assertEqual(unparse({}, full_document=False), '')

    def test_multiple_roots_nofulldoc(self):
        obj = OrderedDict((('a', 1), ('b', 2)))
        xml = unparse(obj, full_document=False)
        self.assertEqual(xml, '<a>1</a><b>2</b>')
        obj = {'a': [1, 2]}
        xml = unparse(obj, full_document=False)
        self.assertEqual(xml, '<a>1</a><a>2</a>')

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

    if hasattr(collections, 'OrderedDict') and not IS_JYTHON:
        # Jython's SAX does not preserve attribute order
        def test_attr_order_roundtrip(self):
            xml = '<root a="1" b="2" c="3"></root>'
            self.assertEqual(xml, _strip(unparse(parse(xml))))

    if hasattr(collections, 'OrderedDict'):
        def test_pretty_print(self):
            obj = {'a': OrderedDict((
                ('b', [{'c': [1, 2]}, 3]),
                ('x', 'y'),
            ))}
            newl = '\n'
            indent = '....'
            xml = dedent('''\
            <?xml version="1.0" encoding="utf-8"?>
            <a>
            ....<b>
            ........<c>1</c>
            ........<c>2</c>
            ....</b>
            ....<b>3</b>
            ....<x>y</x>
            </a>''')
            self.assertEqual(xml, unparse(obj, pretty=True,
                                          newl=newl, indent=indent))

    def test_encoding(self):
        try:
            value = unichr(39321)
        except NameError:
            value = chr(39321)
        obj = {'a': value}
        utf8doc = unparse(obj, encoding='utf-8')
        latin1doc = unparse(obj, encoding='iso-8859-1')
        self.assertEqual(parse(utf8doc), parse(latin1doc))
        self.assertEqual(parse(utf8doc), obj)

    def test_fulldoc(self):
        xml_declaration_re = re.compile(
            '^' + re.escape('<?xml version="1.0" encoding="utf-8"?>'))
        self.assertTrue(xml_declaration_re.match(unparse({'a': 1})))
        self.assertFalse(
            xml_declaration_re.match(unparse({'a': 1}, full_document=False)))
