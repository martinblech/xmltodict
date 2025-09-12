from xmltodict import parse, unparse

import unittest
import re
from textwrap import dedent

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

    def test_list_expand_iter(self):
        obj = {'a': {'b': [['1', '2'], ['3',]]}}
        #self.assertEqual(obj, parse(unparse(obj, expand_iter="item")))
        exp_xml = dedent('''\
        <?xml version="1.0" encoding="utf-8"?>
        <a><b><item>1</item><item>2</item></b><b><item>3</item></b></a>''')
        self.assertEqual(exp_xml, unparse(obj, expand_iter="item"))

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
        obj = {"a": 1, "b": 2}
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
        obj = {"a": {"b:int": [1, 2], "b": "c"}}

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

    def test_attr_order_roundtrip(self):
        xml = '<root a="1" b="2" c="3"></root>'
        self.assertEqual(xml, _strip(unparse(parse(xml))))

    def test_pretty_print(self):
        obj = {
            "a": {
                "b": [{"c": [1, 2]}, 3],
                "x": "y",
            }
        }
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

    def test_unparse_with_element_comment(self):
        obj = {"a": {"#comment": "note", "b": "1"}}
        xml = _strip(unparse(obj, full_document=True))
        self.assertEqual(xml, "<a><!--note--><b>1</b></a>")

    def test_unparse_with_multiple_element_comments(self):
        obj = {"a": {"#comment": ["n1", "n2"], "b": "1"}}
        xml = _strip(unparse(obj, full_document=True))
        self.assertEqual(xml, "<a><!--n1--><!--n2--><b>1</b></a>")

    def test_unparse_with_top_level_comment(self):
        obj = {"#comment": "top", "a": "1"}
        xml = _strip(unparse(obj, full_document=True))
        self.assertEqual(xml, "<!--top--><a>1</a>")

    def test_unparse_with_multiple_top_level_comments(self):
        obj = {"#comment": ["t1", "t2"], "a": "1"}
        xml = _strip(unparse(obj, full_document=True))
        self.assertEqual(xml, "<!--t1--><!--t2--><a>1</a>")

    def test_pretty_print_with_int_indent(self):
        obj = {
            "a": {
                "b": [{"c": [1, 2]}, 3],
                "x": "y",
            }
        }
        newl = '\n'
        indent = 2
        xml = dedent('''\
        <?xml version="1.0" encoding="utf-8"?>
        <a>
          <b>
            <c>1</c>
            <c>2</c>
          </b>
          <b>3</b>
          <x>y</x>
        </a>''')
        self.assertEqual(xml, unparse(obj, pretty=True,
                                      newl=newl, indent=indent))

    def test_comment_roundtrip_limited(self):
        # Input with top-level comments and an element-level comment
        xml = """
        <!--top1--><a><b>1</b><!--e1--></a><!--top2-->
        """
        # Parse with comment processing enabled
        parsed1 = parse(xml, process_comments=True)
        # Unparse and parse again (roundtrip)
        xml2 = unparse(parsed1)
        parsed2 = parse(xml2, process_comments=True)

        # Content preserved
        self.assertIn('a', parsed2)
        self.assertEqual(parsed2['a']['b'], '1')

        # Element-level comment preserved under '#comment'
        self.assertEqual(parsed2['a']['#comment'], 'e1')

        # Top-level comments preserved as a list (order not guaranteed)
        top = parsed2.get('#comment')
        self.assertIsNotNone(top)
        top_list = top if isinstance(top, list) else [top]
        self.assertEqual(set(top_list), {'top1', 'top2'})

    def test_encoding(self):
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

    def test_short_empty_elements(self):
        obj = {'a': None}
        self.assertEqual('<a/>', _strip(unparse(obj, short_empty_elements=True)))

    def test_namespace_support(self):
        obj = {
            "http://defaultns.com/:root": {
                "@xmlns": {
                    "": "http://defaultns.com/",
                    "a": "http://a.com/",
                    "b": "http://b.com/",
                },
                "http://defaultns.com/:x": {
                    "@http://a.com/:attr": "val",
                    "#text": "1",
                },
                "http://a.com/:y": "2",
                "http://b.com/:z": "3",
            },
        }
        ns = {
            'http://defaultns.com/': '',
            'http://a.com/': 'a',
            'http://b.com/': 'b',
        }

        expected_xml = '''<?xml version="1.0" encoding="utf-8"?>
<root xmlns="http://defaultns.com/" xmlns:a="http://a.com/" \
xmlns:b="http://b.com/"><x a:attr="val">1</x><a:y>2</a:y><b:z>3</b:z></root>'''
        xml = unparse(obj, namespaces=ns)

        self.assertEqual(xml, expected_xml)

    def test_boolean_unparse(self):
        expected_xml = '<?xml version="1.0" encoding="utf-8"?>\n<x>true</x>'
        xml = unparse(dict(x=True))
        self.assertEqual(xml, expected_xml)

        expected_xml = '<?xml version="1.0" encoding="utf-8"?>\n<x>false</x>'
        xml = unparse(dict(x=False))
        self.assertEqual(xml, expected_xml)

    def test_rejects_tag_name_with_angle_brackets(self):
        # Minimal guard: disallow '<' or '>' to prevent breaking tag context
        with self.assertRaises(ValueError):
            unparse({"m><tag>content</tag": "unsafe"}, full_document=False)

    def test_rejects_attribute_name_with_angle_brackets(self):
        # Now we expect bad attribute names to be rejected
        with self.assertRaises(ValueError):
            unparse(
                {"a": {"@m><tag>content</tag": "unsafe", "#text": "x"}},
                full_document=False,
            )

    def test_rejects_malicious_xmlns_prefix(self):
        # xmlns prefixes go under @xmlns mapping; reject angle brackets in prefix
        with self.assertRaises(ValueError):
            unparse(
                {
                    "a": {
                        "@xmlns": {"m><bad": "http://example.com/"},
                        "#text": "x",
                    }
                },
                full_document=False,
            )

    def test_attribute_values_with_angle_brackets_are_escaped(self):
        # Attribute values should be escaped by XMLGenerator
        xml = unparse({"a": {"@attr": "1<middle>2", "#text": "x"}}, full_document=False)
        # The generated XML should contain escaped '<' and '>' within the attribute value
        self.assertIn('attr="1&lt;middle&gt;2"', xml)

    def test_rejects_tag_name_starting_with_question(self):
        with self.assertRaises(ValueError):
            unparse({"?pi": "data"}, full_document=False)

    def test_rejects_tag_name_starting_with_bang(self):
        with self.assertRaises(ValueError):
            unparse({"!decl": "data"}, full_document=False)

    def test_rejects_attribute_name_starting_with_question(self):
        with self.assertRaises(ValueError):
            unparse({"a": {"@?weird": "x"}}, full_document=False)

    def test_rejects_attribute_name_starting_with_bang(self):
        with self.assertRaises(ValueError):
            unparse({"a": {"@!weird": "x"}}, full_document=False)

    def test_rejects_xmlns_prefix_starting_with_question_or_bang(self):
        with self.assertRaises(ValueError):
            unparse({"a": {"@xmlns": {"?p": "http://e/"}}}, full_document=False)
        with self.assertRaises(ValueError):
            unparse({"a": {"@xmlns": {"!p": "http://e/"}}}, full_document=False)

    def test_rejects_non_string_names(self):
        class Weird:
            def __str__(self):
                return "bad>name"

        # Non-string element key
        with self.assertRaises(ValueError):
            unparse({Weird(): "x"}, full_document=False)
        # Non-string attribute key
        with self.assertRaises(ValueError):
            unparse({"a": {Weird(): "x"}}, full_document=False)

    def test_rejects_tag_name_with_slash(self):
        with self.assertRaises(ValueError):
            unparse({"bad/name": "x"}, full_document=False)

    def test_rejects_tag_name_with_whitespace(self):
        for name in ["bad name", "bad\tname", "bad\nname"]:
            with self.assertRaises(ValueError):
                unparse({name: "x"}, full_document=False)

    def test_rejects_attribute_name_with_slash(self):
        with self.assertRaises(ValueError):
            unparse({"a": {"@bad/name": "x"}}, full_document=False)

    def test_rejects_attribute_name_with_whitespace(self):
        for name in ["@bad name", "@bad\tname", "@bad\nname"]:
            with self.assertRaises(ValueError):
                unparse({"a": {name: "x"}}, full_document=False)

    def test_rejects_xmlns_prefix_with_slash_or_whitespace(self):
        # Slash
        with self.assertRaises(ValueError):
            unparse({"a": {"@xmlns": {"bad/prefix": "http://e/"}}}, full_document=False)
        # Whitespace
        with self.assertRaises(ValueError):
            unparse({"a": {"@xmlns": {"bad prefix": "http://e/"}}}, full_document=False)

    def test_rejects_names_with_quotes_and_equals(self):
        # Element names
        for name in ['a"b', "a'b", "a=b"]:
            with self.assertRaises(ValueError):
                unparse({name: "x"}, full_document=False)
        # Attribute names
        for name in ['@a"b', "@a'b", "@a=b"]:
            with self.assertRaises(ValueError):
                unparse({"a": {name: "x"}}, full_document=False)
        # xmlns prefixes
        for prefix in ['a"b', "a'b", "a=b"]:
            with self.assertRaises(ValueError):
                unparse({"a": {"@xmlns": {prefix: "http://e/"}}}, full_document=False)

    def test_pretty_print_and_short_empty_elements_consistency(self):
        """Test that pretty and compact modes produce equivalent results when stripped.

        This test covers issue #352: Edge case with pretty_print and short_empty_elements.
        When short_empty_elements=True, empty elements should be written as <tag/>
        regardless of whether pretty printing is enabled.
        """
        # Test case from issue #352: empty list child
        input_dict = {"Foos": {"Foo": []}}

        compact = unparse(
            input_dict, pretty=False, short_empty_elements=True, full_document=False
        )
        pretty = unparse(
            input_dict, pretty=True, short_empty_elements=True, full_document=False
        )
        pretty_compacted = pretty.replace("\n", "").replace("\t", "")

        # They should be equal when pretty formatting is stripped
        self.assertEqual(pretty_compacted, compact)
        self.assertEqual(compact, "<Foos/>")
        self.assertEqual(pretty_compacted, "<Foos/>")

    def test_empty_list_filtering(self):
        """Test that empty lists are filtered out and don't create empty child elements."""
        # Test various cases with empty lists
        test_cases = [
            # Case 1: Single empty list child
            ({"Foos": {"Foo": []}}, "<Foos/>"),
            # Case 2: Multiple empty list children
            ({"Foos": {"Foo": [], "Bar": []}}, "<Foos/>"),
            # Case 3: Mixed empty and non-empty children
            ({"Foos": {"Foo": [], "Bar": "value"}}, "<Foos><Bar>value</Bar></Foos>"),
            # Case 4: Nested empty lists
            ({"Foos": {"Foo": {"Bar": []}}}, "<Foos><Foo/></Foos>"),
            # Case 5: Empty list with attributes
            ({"Foos": {"@attr": "value", "Foo": []}}, '<Foos attr="value"/>'),
        ]

        for input_dict, expected_compact in test_cases:
            with self.subTest(input_dict=input_dict):
                # Test compact mode
                compact = unparse(
                    input_dict,
                    pretty=False,
                    short_empty_elements=True,
                    full_document=False,
                )
                self.assertEqual(compact, expected_compact)

                # Test pretty mode
                pretty = unparse(
                    input_dict,
                    pretty=True,
                    short_empty_elements=True,
                    full_document=False,
                )
                pretty_compacted = pretty.replace("\n", "").replace("\t", "")
                self.assertEqual(pretty_compacted, expected_compact)

    def test_empty_list_filtering_with_short_empty_elements_false(self):
        """Test that empty lists are still filtered when short_empty_elements=False."""
        input_dict = {"Foos": {"Foo": []}}

        # With short_empty_elements=False, empty elements should be <tag></tag>
        compact = unparse(
            input_dict, pretty=False, short_empty_elements=False, full_document=False
        )
        pretty = unparse(
            input_dict, pretty=True, short_empty_elements=False, full_document=False
        )
        pretty_compacted = pretty.replace("\n", "").replace("\t", "")

        # They should be equal when pretty formatting is stripped
        self.assertEqual(pretty_compacted, compact)
        self.assertEqual(compact, "<Foos></Foos>")
        self.assertEqual(pretty_compacted, "<Foos></Foos>")

    def test_non_empty_lists_are_not_filtered(self):
        """Test that non-empty lists are not filtered out."""
        # Test with non-empty lists
        input_dict = {"Foos": {"Foo": ["item1", "item2"]}}

        compact = unparse(
            input_dict, pretty=False, short_empty_elements=True, full_document=False
        )
        pretty = unparse(
            input_dict, pretty=True, short_empty_elements=True, full_document=False
        )
        pretty_compacted = pretty.replace("\n", "").replace("\t", "")

        # The lists should be processed normally
        self.assertEqual(pretty_compacted, compact)
        self.assertEqual(compact, "<Foos><Foo>item1</Foo><Foo>item2</Foo></Foos>")
        self.assertEqual(
            pretty_compacted, "<Foos><Foo>item1</Foo><Foo>item2</Foo></Foos>"
        )

    def test_empty_dict_vs_empty_list_behavior(self):
        """Test the difference between empty dicts and empty lists."""
        # Empty dict should create a child element
        input_dict_dict = {"Foos": {"Foo": {}}}
        compact_dict = unparse(
            input_dict_dict,
            pretty=False,
            short_empty_elements=True,
            full_document=False,
        )
        self.assertEqual(compact_dict, "<Foos><Foo/></Foos>")

        # Empty list should be filtered out
        input_dict_list = {"Foos": {"Foo": []}}
        compact_list = unparse(
            input_dict_list,
            pretty=False,
            short_empty_elements=True,
            full_document=False,
        )
        self.assertEqual(compact_list, "<Foos/>")

        # They should be different
        self.assertNotEqual(compact_dict, compact_list)

    def test_non_string_text_with_attributes(self):
        """Test that non-string #text values work when tag has attributes.

        This test covers GitHub issue #366: Tag value (#text) must be a string
        when tag has additional parameters - unparse.

        Also tests that plain values and explicit #text values are treated
        consistently (both go through the same conversion logic).
        """
        # Test cases for explicit #text values with attributes
        self.assertEqual(unparse({"a": {"@param": "test", "#text": 1}}, full_document=False),
                         '<a param="test">1</a>')

        self.assertEqual(unparse({"a": {"@param": 42, "#text": 3.14}}, full_document=False),
                         '<a param="42">3.14</a>')

        self.assertEqual(unparse({"a": {"@param": "flag", "#text": True}}, full_document=False),
                         '<a param="flag">true</a>')

        self.assertEqual(unparse({"a": {"@param": "test", "#text": None}}, full_document=False),
                         '<a param="test">None</a>')

        self.assertEqual(unparse({"a": {"@param": "test", "#text": "string"}}, full_document=False),
                         '<a param="test">string</a>')

        self.assertEqual(unparse({"a": {"@attr1": "value1", "@attr2": 2, "#text": 100}}, full_document=False),
                         '<a attr1="value1" attr2="2">100</a>')

        # Test cases for plain values (should be treated the same as #text)
        self.assertEqual(unparse({"a": 1}, full_document=False), '<a>1</a>')
        self.assertEqual(unparse({"a": 3.14}, full_document=False), '<a>3.14</a>')
        self.assertEqual(unparse({"a": True}, full_document=False), '<a>true</a>')
        self.assertEqual(unparse({"a": "hello"}, full_document=False), '<a>hello</a>')
        self.assertEqual(unparse({"a": None}, full_document=False), '<a></a>')

        # Consistency tests: plain values should match explicit #text values
        self.assertEqual(unparse({"a": 42}, full_document=False),
                         unparse({"a": {"#text": 42}}, full_document=False))

        self.assertEqual(unparse({"a": 3.14}, full_document=False),
                         unparse({"a": {"#text": 3.14}}, full_document=False))

        self.assertEqual(unparse({"a": True}, full_document=False),
                         unparse({"a": {"#text": True}}, full_document=False))

        self.assertEqual(unparse({"a": "hello"}, full_document=False),
                         unparse({"a": {"#text": "hello"}}, full_document=False))
