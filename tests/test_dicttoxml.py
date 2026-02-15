from xmltodict import parse, unparse
import pytest
import re
from textwrap import dedent

_HEADER_RE = re.compile(r'^[^\n]*\n')


def _strip(fullxml):
    return _HEADER_RE.sub('', fullxml)


def test_root():
    obj = {'a': None}
    assert obj == parse(unparse(obj))
    assert unparse(obj) == unparse(parse(unparse(obj)))


def test_simple_cdata():
    obj = {'a': 'b'}
    assert obj == parse(unparse(obj))
    assert unparse(obj) == unparse(parse(unparse(obj)))


def test_cdata():
    obj = {'a': {'#text': 'y'}}
    assert obj == parse(unparse(obj), force_cdata=True)
    assert unparse(obj) == unparse(parse(unparse(obj)))


def test_attrib():
    obj = {'a': {'@href': 'x'}}
    assert obj == parse(unparse(obj))
    assert unparse(obj) == unparse(parse(unparse(obj)))


def test_attrib_and_cdata():
    obj = {'a': {'@href': 'x', '#text': 'y'}}
    assert obj == parse(unparse(obj))
    assert unparse(obj) == unparse(parse(unparse(obj)))


def test_list():
    obj = {'a': {'b': ['1', '2', '3']}}
    assert obj == parse(unparse(obj))
    assert unparse(obj) == unparse(parse(unparse(obj)))


def test_list_expand_iter():
    obj = {'a': {'b': [['1', '2'], ['3',]]}}
    #assert obj == parse(unparse(obj, expand_iter="item")))
    exp_xml = dedent('''\
    <?xml version="1.0" encoding="utf-8"?>
    <a><b><item>1</item><item>2</item></b><b><item>3</item></b></a>''')
    assert exp_xml == unparse(obj, expand_iter="item")


def test_generator():
    obj = {'a': {'b': ['1', '2', '3']}}

    def lazy_obj():
        return {'a': {'b': (i for i in ('1', '2', '3'))}}
    assert obj == parse(unparse(lazy_obj()))
    assert unparse(lazy_obj()) == unparse(parse(unparse(lazy_obj())))


def test_no_root():
    with pytest.raises(ValueError):
        unparse({})


def test_multiple_roots():
    with pytest.raises(ValueError):
        unparse({'a': '1', 'b': '2'})
    with pytest.raises(ValueError):
        unparse({'a': ['1', '2', '3']})


def test_no_root_nofulldoc():
    assert unparse({}, full_document=False) == ''


def test_multiple_roots_nofulldoc():
    obj = {"a": 1, "b": 2}
    xml = unparse(obj, full_document=False)
    assert xml == '<a>1</a><b>2</b>'
    obj = {'a': [1, 2]}
    xml = unparse(obj, full_document=False)
    assert xml == '<a>1</a><a>2</a>'


def test_nested():
    obj = {'a': {'b': '1', 'c': '2'}}
    assert obj == parse(unparse(obj))
    assert unparse(obj) == unparse(parse(unparse(obj)))
    obj = {'a': {'b': {'c': {'@a': 'x', '#text': 'y'}}}}
    assert obj == parse(unparse(obj))
    assert unparse(obj) == unparse(parse(unparse(obj)))


def test_semistructured():
    xml = '<a>abc<d/>efg</a>'
    assert _strip(unparse(parse(xml))) == '<a><d></d>abcefg</a>'


def test_preprocessor():
    obj = {"a": {"b:int": [1, 2], "b": "c"}}

    def p(key, value):
        try:
            key, _ = key.split(':')
        except ValueError:
            pass
        return key, value

    assert _strip(unparse(obj, preprocessor=p)) == '<a><b>1</b><b>2</b><b>c</b></a>'


def test_preprocessor_skipkey():
    obj = {'a': {'b': 1, 'c': 2}}

    def p(key, value):
        if key == 'b':
            return None
        return key, value

    assert _strip(unparse(obj, preprocessor=p)) == '<a><c>2</c></a>'


def test_attr_order_roundtrip():
    xml = '<root a="1" b="2" c="3"></root>'
    assert xml == _strip(unparse(parse(xml)))


def test_pretty_print():
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
    assert xml == unparse(obj, pretty=True, newl=newl, indent=indent)


def test_unparse_with_element_comment():
    obj = {"a": {"#comment": "note", "b": "1"}}
    xml = _strip(unparse(obj, full_document=True))
    assert xml == "<a><!--note--><b>1</b></a>"


def test_unparse_with_multiple_element_comments():
    obj = {"a": {"#comment": ["n1", "n2"], "b": "1"}}
    xml = _strip(unparse(obj, full_document=True))
    assert xml == "<a><!--n1--><!--n2--><b>1</b></a>"


def test_unparse_with_top_level_comment():
    obj = {"#comment": "top", "a": "1"}
    xml = _strip(unparse(obj, full_document=True))
    assert xml == "<!--top--><a>1</a>"


def test_unparse_with_multiple_top_level_comments():
    obj = {"#comment": ["t1", "t2"], "a": "1"}
    xml = _strip(unparse(obj, full_document=True))
    assert xml == "<!--t1--><!--t2--><a>1</a>"


def test_unparse_rejects_comment_with_double_hyphen():
    obj = {"#comment": "bad--comment", "a": "1"}
    with pytest.raises(ValueError, match="cannot contain '--'"):
        unparse(obj, full_document=True)


def test_unparse_rejects_comment_ending_with_hyphen():
    obj = {"#comment": "trailing-", "a": "1"}
    with pytest.raises(ValueError, match="cannot end with '-'"):
        unparse(obj, full_document=True)


def test_pretty_print_with_int_indent():
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
    assert xml == unparse(obj, pretty=True, newl=newl, indent=indent)


def test_comment_roundtrip_limited():
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
    assert 'a' in parsed2
    assert parsed2['a']['b'] == '1'

    # Element-level comment preserved under '#comment'
    assert parsed2['a']['#comment'] == 'e1'

    # Top-level comments preserved as a list (order not guaranteed)
    top = parsed2.get('#comment')
    assert top is not None
    top_list = top if isinstance(top, list) else [top]
    assert set(top_list) == {'top1', 'top2'}


def test_encoding():
    value = chr(39321)
    obj = {'a': value}
    utf8doc = unparse(obj, encoding='utf-8')
    latin1doc = unparse(obj, encoding='iso-8859-1')
    assert parse(utf8doc) == parse(latin1doc)
    assert parse(utf8doc) == obj


def test_fulldoc():
    xml_declaration_re = re.compile(
        '^' + re.escape('<?xml version="1.0" encoding="utf-8"?>'))
    assert xml_declaration_re.match(unparse({'a': 1}))
    assert not xml_declaration_re.match(unparse({'a': 1}, full_document=False))


def test_non_string_value():
    obj = {'a': 1}
    assert '<a>1</a>' == _strip(unparse(obj))


def test_non_string_attr():
    obj = {'a': {'@attr': 1}}
    assert '<a attr="1"></a>' == _strip(unparse(obj))


def test_short_empty_elements():
    obj = {'a': None}
    assert '<a/>' == _strip(unparse(obj, short_empty_elements=True))


def test_namespace_support():
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

    assert xml == expected_xml


def test_boolean_unparse():
    expected_xml = '<?xml version="1.0" encoding="utf-8"?>\n<x>true</x>'
    xml = unparse(dict(x=True))
    assert xml == expected_xml

    expected_xml = '<?xml version="1.0" encoding="utf-8"?>\n<x>false</x>'
    xml = unparse(dict(x=False))
    assert xml == expected_xml


def test_rejects_tag_name_with_angle_brackets():
    # Minimal guard: disallow '<' or '>' to prevent breaking tag context
    with pytest.raises(ValueError):
        unparse({"m><tag>content</tag": "unsafe"}, full_document=False)


def test_rejects_attribute_name_with_angle_brackets():
    # Now we expect bad attribute names to be rejected
    with pytest.raises(ValueError):
        unparse(
            {"a": {"@m><tag>content</tag": "unsafe", "#text": "x"}},
            full_document=False,
        )


def test_rejects_malicious_xmlns_prefix():
    # xmlns prefixes go under @xmlns mapping; reject angle brackets in prefix
    with pytest.raises(ValueError):
        unparse(
            {
                "a": {
                    "@xmlns": {"m><bad": "http://example.com/"},
                    "#text": "x",
                }
            },
            full_document=False,
        )


def test_attribute_values_with_angle_brackets_are_escaped():
    # Attribute values should be escaped by XMLGenerator
    xml = unparse({"a": {"@attr": "1<middle>2", "#text": "x"}}, full_document=False)
    # The generated XML should contain escaped '<' and '>' within the attribute value
    assert 'attr="1&lt;middle&gt;2"' in xml


def test_rejects_tag_name_starting_with_question():
    with pytest.raises(ValueError):
        unparse({"?pi": "data"}, full_document=False)


def test_rejects_tag_name_starting_with_bang():
    with pytest.raises(ValueError):
        unparse({"!decl": "data"}, full_document=False)


def test_rejects_attribute_name_starting_with_question():
    with pytest.raises(ValueError):
        unparse({"a": {"@?weird": "x"}}, full_document=False)


def test_rejects_attribute_name_starting_with_bang():
    with pytest.raises(ValueError):
        unparse({"a": {"@!weird": "x"}}, full_document=False)


def test_rejects_xmlns_prefix_starting_with_question_or_bang():
    with pytest.raises(ValueError):
        unparse({"a": {"@xmlns": {"?p": "http://e/"}}}, full_document=False)
    with pytest.raises(ValueError):
        unparse({"a": {"@xmlns": {"!p": "http://e/"}}}, full_document=False)


def test_rejects_non_string_names():
    class Weird:
        def __str__(self):
            return "bad>name"

    # Non-string element key
    with pytest.raises(ValueError):
        unparse({Weird(): "x"}, full_document=False)
    # Non-string attribute key
    with pytest.raises(ValueError):
        unparse({"a": {Weird(): "x"}}, full_document=False)


def test_rejects_tag_name_with_slash():
    with pytest.raises(ValueError):
        unparse({"bad/name": "x"}, full_document=False)


def test_rejects_tag_name_with_whitespace():
    for name in ["bad name", "bad\tname", "bad\nname"]:
        with pytest.raises(ValueError):
            unparse({name: "x"}, full_document=False)


def test_rejects_attribute_name_with_slash():
    with pytest.raises(ValueError):
        unparse({"a": {"@bad/name": "x"}}, full_document=False)


def test_rejects_attribute_name_with_whitespace():
    for name in ["@bad name", "@bad\tname", "@bad\nname"]:
        with pytest.raises(ValueError):
            unparse({"a": {name: "x"}}, full_document=False)


def test_rejects_xmlns_prefix_with_slash_or_whitespace():
    # Slash
    with pytest.raises(ValueError):
        unparse({"a": {"@xmlns": {"bad/prefix": "http://e/"}}}, full_document=False)
    # Whitespace
    with pytest.raises(ValueError):
        unparse({"a": {"@xmlns": {"bad prefix": "http://e/"}}}, full_document=False)


def test_rejects_names_with_quotes_and_equals():
    # Element names
    for name in ['a"b', "a'b", "a=b"]:
        with pytest.raises(ValueError):
            unparse({name: "x"}, full_document=False)
    # Attribute names
    for name in ['@a"b', "@a'b", "@a=b"]:
        with pytest.raises(ValueError):
            unparse({"a": {name: "x"}}, full_document=False)
    # xmlns prefixes
    for prefix in ['a"b', "a'b", "a=b"]:
        with pytest.raises(ValueError):
            unparse({"a": {"@xmlns": {prefix: "http://e/"}}}, full_document=False)


def test_pretty_print_and_short_empty_elements_consistency():
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
    assert pretty_compacted == compact
    assert compact == "<Foos/>"
    assert pretty_compacted == "<Foos/>"


def test_empty_list_filtering():
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
        # Test compact mode
        compact = unparse(
            input_dict,
            pretty=False,
            short_empty_elements=True,
            full_document=False,
        )
        assert compact == expected_compact

        # Test pretty mode
        pretty = unparse(
            input_dict,
            pretty=True,
            short_empty_elements=True,
            full_document=False,
        )
        pretty_compacted = pretty.replace("\n", "").replace("\t", "")
        assert pretty_compacted == expected_compact


def test_empty_list_filtering_with_short_empty_elements_false():
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
    assert pretty_compacted == compact
    assert compact == "<Foos></Foos>"
    assert pretty_compacted == "<Foos></Foos>"


def test_non_empty_lists_are_not_filtered():
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
    assert pretty_compacted == compact
    assert compact == "<Foos><Foo>item1</Foo><Foo>item2</Foo></Foos>"
    assert (
        pretty_compacted == "<Foos><Foo>item1</Foo><Foo>item2</Foo></Foos>"
    )


def test_empty_dict_vs_empty_list_behavior():
    """Test the difference between empty dicts and empty lists."""
    # Empty dict should create a child element
    input_dict_dict = {"Foos": {"Foo": {}}}
    compact_dict = unparse(
        input_dict_dict,
        pretty=False,
        short_empty_elements=True,
        full_document=False,
    )
    assert compact_dict == "<Foos><Foo/></Foos>"

    # Empty list should be filtered out
    input_dict_list = {"Foos": {"Foo": []}}
    compact_list = unparse(
        input_dict_list,
        pretty=False,
        short_empty_elements=True,
        full_document=False,
    )
    assert compact_list == "<Foos/>"

    # They should be different
    assert compact_dict != compact_list


def test_non_string_text_with_attributes():
    """Test that non-string #text values work when tag has attributes.

    This test covers GitHub issue #366: Tag value (#text) must be a string
    when tag has additional parameters - unparse.

    Also tests that plain values and explicit #text values are treated
    consistently (both go through the same conversion logic).
    """
    # Test cases for explicit #text values with attributes
    assert unparse({"a": {"@param": "test", "#text": 1}}, full_document=False) == '<a param="test">1</a>'

    assert unparse({"a": {"@param": 42, "#text": 3.14}}, full_document=False) == '<a param="42">3.14</a>'

    assert unparse({"a": {"@param": "flag", "#text": True}}, full_document=False) == '<a param="flag">true</a>'

    assert unparse({"a": {"@param": "test", "#text": None}}, full_document=False) == '<a param="test"></a>'

    assert unparse({"a": {"@param": "test", "#text": "string"}}, full_document=False) == '<a param="test">string</a>'

    assert unparse({"a": {"@attr1": "value1", "@attr2": 2, "#text": 100}}, full_document=False) == '<a attr1="value1" attr2="2">100</a>'

    # Test cases for plain values (should be treated the same as #text)
    assert unparse({"a": 1}, full_document=False) == '<a>1</a>'
    assert unparse({"a": 3.14}, full_document=False) == '<a>3.14</a>'
    assert unparse({"a": True}, full_document=False) == '<a>true</a>'
    assert unparse({"a": "hello"}, full_document=False) == '<a>hello</a>'
    assert unparse({"a": None}, full_document=False) == '<a></a>'

    # Consistency tests: plain values should match explicit #text values
    assert unparse({"a": 42}, full_document=False) == unparse({"a": {"#text": 42}}, full_document=False)

    assert unparse({"a": 3.14}, full_document=False) == unparse({"a": {"#text": 3.14}}, full_document=False)

    assert unparse({"a": True}, full_document=False) == unparse({"a": {"#text": True}}, full_document=False)

    assert unparse({"a": "hello"}, full_document=False) == unparse({"a": {"#text": "hello"}}, full_document=False)
    assert unparse({"a": None}, full_document=False) == unparse({"a": {"#text": None}}, full_document=False)


def test_none_text_with_short_empty_elements_and_attributes():
    obj = {"x": {"#text": None, "@pro": None}, "y": None}
    assert unparse(obj, short_empty_elements=True, full_document=False) == '<x pro=""/><y/>'


def test_none_attribute_serializes_as_empty_string():
    assert unparse({"x": {"@pro": None}}, full_document=False) == '<x pro=""></x>'
