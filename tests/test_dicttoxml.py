import sys
from xmltodict import parse, unparse, OrderedDict

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import re
from textwrap import dedent
import os
from zipfile import ZipFile
from io import TextIOWrapper

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

    def test_generator(self):
        obj = {'a': {'b': ['1', '2', '3']}}
        def lazy_obj():
            return {'a': {'b': (i for i in ('1', '2', '3'))}}
        self.assertEqual(obj, parse(unparse(lazy_obj())))
        self.assertEqual(unparse(lazy_obj()),
             unparse(parse(unparse(lazy_obj()))))

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

    if not IS_JYTHON:
        # Jython's SAX does not preserve attribute order
        def test_attr_order_roundtrip(self):
            xml = '<root a="1" b="2" c="3"></root>'
            self.assertEqual(xml, _strip(unparse(parse(xml))))

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

    def test_non_string_value(self):
        obj = {'a': 1}
        self.assertEqual('<a>1</a>', _strip(unparse(obj)))

    def test_non_string_attr(self):
        obj = {'a': {'@attr': 1}}
        self.assertEqual('<a attr="1"></a>', _strip(unparse(obj)))


class OrderedMixedChildrenTests(unittest.TestCase):

    order_at_leaf_xml = \
        """<?xml version="1.0" encoding="utf-8"?>\n""" \
        """<a><b>1</b><c>2</c><b>3</b><c>4</c></a>"""

    order_at_branch_xml = \
        """<?xml version="1.0" encoding="utf-8"?>\n""" \
        """<a><b><d>1</d><d>2</d></b><c><f>5</f><f>6</f></c>""" \
        """<b><e>test</e></b><c><g>a</g><g>b</g></c></a>"""

    @classmethod
    def setUpClass(cls):
        xml_zip = os.path.join(os.path.dirname(__file__), 'large_document.zip')
        with ZipFile(xml_zip) as zip_file:
            with zip_file.open('xform.xml') as xml_file:
                cls.large_document = TextIOWrapper(xml_file).read()

    def test_order_at_leaf(self):
        obj = {"a": OrderedDict((
            ("b", (
                {"@__order__": 1, "#text": "1"},
                {"@__order__": 3, "#text": "3"}
            )),
            ("c", (
                {"@__order__": 2, "#text": "2"},
                {"@__order__": 4, "#text": "4"}
            ))
        ))}
        expected = self.order_at_leaf_xml
        observed = unparse(obj, ordered_mixed_children=True)
        self.assertEqual(expected, observed)

    def test_order_at_leaf_round_trip_equal(self):
        expected = self.order_at_leaf_xml
        parsed = parse(expected, ordered_mixed_children=True)
        observed = unparse(parsed, ordered_mixed_children=True)
        self.assertEqual(expected, observed)

    def test_order_at_branch(self):
        obj = {"a": OrderedDict((
            ("b", (
                {"@__order__": 1, "d": (1, 2)},
                {"@__order__": 3, "e": "test"}
            )),
            ("c", (
                {"@__order__": 2, "f": (5, 6)},
                {"@__order__": 4, "g": ("a", "b")}
            ))
        ))}
        expected = self.order_at_branch_xml
        observed = unparse(obj, ordered_mixed_children=True)
        self.assertEqual(expected, observed)

    def test_order_at_branch_round_trip_equal(self):
        expected = self.order_at_branch_xml
        parsed = parse(expected, ordered_mixed_children=True)
        observed = unparse(parsed, ordered_mixed_children=True)
        self.assertEqual(expected, observed)

    def test_round_trip_not_equal_permutations(self):
        flag_sets = ((True, False), (False, True), (False, False))
        expected_set = (
            self.order_at_leaf_xml,
            self.order_at_branch_xml,
            self.large_document
        )
        for i, expected in enumerate(expected_set):
            for parse_flag, unparse_flag in flag_sets:
                parsed = parse(expected, ordered_mixed_children=parse_flag)
                observed = unparse(parsed, ordered_mixed_children=unparse_flag)
                fail_msg = "\nInput: {0}, Parse: {1}, Unparse: {2}".format(
                    i+1, parse_flag, unparse_flag)
                self.assertNotEqual(expected, observed, fail_msg)

    def test_order_unspecified_goes_last(self):
        obj = {"a": OrderedDict((
            ("b", (
                1, {"@__order__": 3, "#text": "3"}, 0
            )),
            ("c", (
                {"@__order__": 2, "#text": "2"}, 5, 4
            ))
        ))}
        expected = """<?xml version="1.0" encoding="utf-8"?>\n""" \
                   """<a><c>2</c><b>3</b><b>1</b><b>0</b><c>5</c><c>4</c></a>"""
        observed = unparse(obj, ordered_mixed_children=True)
        self.assertEqual(expected, observed)

    def test_large_document_round_trip(self):
        expected = self.large_document
        xml_dict = parse(expected, ordered_mixed_children=True)
        observed = unparse(xml_dict, ordered_mixed_children=True)
        self.assertEqual(expected, observed)


class XMLGeneratorShortTests(unittest.TestCase):

    def test_flag_on_produces_short_empty_tags(self):
        obj = {'a': {'b': None}}
        expected = """<?xml version="1.0" encoding="utf-8"?>\n""" \
                   """<a><b/></a>"""
        observed = unparse(obj, short_empty_elements=True)
        self.assertEqual(expected, observed)

    def test_flag_off_produces_expanded_empty_tags(self):
        obj = {'a': {'b': None}}
        expected = """<?xml version="1.0" encoding="utf-8"?>\n""" \
                   """<a><b></b></a>"""
        observed = unparse(obj, short_empty_elements=False)
        self.assertEqual(expected, observed)
