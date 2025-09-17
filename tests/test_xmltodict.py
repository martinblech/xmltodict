from xmltodict import parse, ParsingInterrupted
import collections
import pytest
from io import BytesIO

from xml.parsers.expat import ParserCreate
from xml.parsers import expat


def test_string_vs_file():
    xml = '<a>data</a>'
    assert parse(xml) == parse(BytesIO(xml.encode('ascii')))


def test_minimal():
    assert parse('<a/>') == {'a': None}
    assert parse('<a/>', force_cdata=True) == {'a': None}


def test_simple():
    assert parse('<a>data</a>') == {'a': 'data'}


def test_force_cdata():
    assert parse('<a>data</a>', force_cdata=True) == {'a': {'#text': 'data'}}


def test_selective_force_cdata_tuple():
    xml = "<a><b>data1</b><c>data2</c><d>data3</d></a>"
    # Test with tuple of specific element names
    result = parse(xml, force_cdata=("b", "d"))
    expected = {
        "a": {"b": {"#text": "data1"}, "c": "data2", "d": {"#text": "data3"}}
    }
    assert result == expected


def test_selective_force_cdata_single_element():
    xml = "<a><b>data1</b><c>data2</c></a>"
    # Test with single element name
    result = parse(xml, force_cdata=("b",))
    expected = {"a": {"b": {"#text": "data1"}, "c": "data2"}}
    assert result == expected


def test_selective_force_cdata_empty_tuple():
    xml = "<a><b>data1</b><c>data2</c></a>"
    # Test with empty tuple (should behave like force_cdata=False)
    result = parse(xml, force_cdata=())
    expected = {"a": {"b": "data1", "c": "data2"}}
    assert result == expected


def test_selective_force_cdata_callable():
    xml = "<a><b>data1</b><c>data2</c><d>data3</d></a>"

    # Test with callable function
    def should_force_cdata(path, key, value):
        return key in ["b", "d"]

    result = parse(xml, force_cdata=should_force_cdata)
    expected = {
        "a": {"b": {"#text": "data1"}, "c": "data2", "d": {"#text": "data3"}}
    }
    assert result == expected


def test_selective_force_cdata_nested_elements():
    xml = "<a><b><c>data1</c></b><d>data2</d></a>"
    # Test with nested elements - only 'c' should be forced
    result = parse(xml, force_cdata=("c",))
    expected = {"a": {"b": {"c": {"#text": "data1"}}, "d": "data2"}}
    assert result == expected


def test_selective_force_cdata_with_attributes():
    xml = '<a><b attr="value">data1</b><c>data2</c></a>'
    # Test with attributes - force_cdata should still work
    result = parse(xml, force_cdata=("b",))
    expected = {"a": {"b": {"@attr": "value", "#text": "data1"}, "c": "data2"}}
    assert result == expected


def test_selective_force_cdata_backwards_compatibility():
    xml = "<a><b>data1</b><c>data2</c></a>"
    # Test that boolean True still works (backwards compatibility)
    result_true = parse(xml, force_cdata=True)
    expected_true = {"a": {"b": {"#text": "data1"}, "c": {"#text": "data2"}}}
    assert result_true == expected_true

    # Test that boolean False still works (backwards compatibility)
    result_false = parse(xml, force_cdata=False)
    expected_false = {"a": {"b": "data1", "c": "data2"}}
    assert result_false == expected_false


def test_custom_cdata():
    assert parse('<a>data</a>', force_cdata=True, cdata_key='_CDATA_') == {'a': {'_CDATA_': 'data'}}


def test_list():
    assert parse('<a><b>1</b><b>2</b><b>3</b></a>') == {'a': {'b': ['1', '2', '3']}}


def test_attrib():
    assert parse('<a href="xyz"/>') == {'a': {'@href': 'xyz'}}


def test_skip_attrib():
    assert parse('<a href="xyz"/>', xml_attribs=False) == {'a': None}


def test_custom_attrib():
    assert parse('<a href="xyz"/>', attr_prefix='!') == {'a': {'!href': 'xyz'}}


def test_attrib_and_cdata():
    assert parse('<a href="xyz">123</a>') == {'a': {'@href': 'xyz', '#text': '123'}}


def test_semi_structured():
    assert parse('<a>abc<b/>def</a>') == {'a': {'b': None, '#text': 'abcdef'}}
    assert parse('<a>abc<b/>def</a>', cdata_separator='\n') == {'a': {'b': None, '#text': 'abc\ndef'}}


def test_nested_semi_structured():
    assert parse('<a>abc<b>123<c/>456</b>def</a>') == {'a': {'#text': 'abcdef', 'b': {'#text': '123456', 'c': None}}}


def test_skip_whitespace():
    xml = """
    <root>


      <emptya>           </emptya>
      <emptyb attr="attrvalue">


      </emptyb>
      <value>hello</value>
    </root>
    """
    assert parse(xml) == {'root': {'emptya': None, 'emptyb': {'@attr': 'attrvalue'}, 'value': 'hello'}}


def test_keep_whitespace():
    xml = "<root> </root>"
    assert parse(xml) == dict(root=None)
    assert parse(xml, strip_whitespace=False) == dict(root=' ')


def test_streaming():
    def cb(path, item):
        cb.count += 1
        assert path == [('a', {'x': 'y'}), ('b', None)]
        assert item == str(cb.count)
        return True
    cb.count = 0
    parse('<a x="y"><b>1</b><b>2</b><b>3</b></a>', item_depth=2, item_callback=cb)
    assert cb.count == 3


def test_streaming_interrupt():
    def cb(path, item):
        return False
    with pytest.raises(ParsingInterrupted):
        parse('<a>x</a>', item_depth=1, item_callback=cb)


def test_streaming_generator():
    def cb(path, item):
        cb.count += 1
        assert path == [('a', {'x': 'y'}), ('b', None)]
        assert item == str(cb.count)
        return True
    cb.count = 0
    parse((n for n in '<a x="y"><b>1</b><b>2</b><b>3</b></a>'), item_depth=2, item_callback=cb)
    assert cb.count == 3


def test_streaming_returns_none():
    # When streaming (item_depth > 0), parse should return None
    def cb(path, item):
        return True

    result = parse("<a><b>1</b><b>2</b></a>", item_depth=2, item_callback=cb)
    assert result is None


def test_postprocessor():
    def postprocessor(path, key, value):
        try:
            return key + ':int', int(value)
        except (ValueError, TypeError):
            return key, value
    assert {'a': {'b:int': [1, 2], 'b': 'x'}} == parse('<a><b>1</b><b>2</b><b>x</b></a>', postprocessor=postprocessor)


def test_postprocessor_attribute():
    def postprocessor(path, key, value):
        try:
            return key + ':int', int(value)
        except (ValueError, TypeError):
            return key, value
    assert {'a': {'@b:int': 1}} == parse('<a b="1"/>', postprocessor=postprocessor)


def test_postprocessor_skip():
    def postprocessor(path, key, value):
        if key == 'b':
            value = int(value)
            if value == 3:
                return None
        return key, value
    assert {'a': {'b': [1, 2]}} == parse('<a><b>1</b><b>2</b><b>3</b></a>', postprocessor=postprocessor)


def test_unicode():
    value = chr(39321)
    assert {'a': value} == parse(f'<a>{value}</a>')


def test_encoded_string():
    value = chr(39321)
    xml = f'<a>{value}</a>'
    assert parse(xml) == parse(xml.encode('utf-8'))


def test_namespace_support():
    xml = """
    <root xmlns="http://defaultns.com/"
          xmlns:a="http://a.com/"
          xmlns:b="http://b.com/"
          version="1.00">
      <x a:attr="val">1</x>
      <a:y>2</a:y>
      <b:z>3</b:z>
    </root>
    """
    d = {
        'http://defaultns.com/:root': {
            '@version': '1.00',
            '@xmlns': {
                '': 'http://defaultns.com/',
                'a': 'http://a.com/',
                'b': 'http://b.com/',
            },
            'http://defaultns.com/:x': {
                '@http://a.com/:attr': 'val',
                '#text': '1',
            },
            'http://a.com/:y': '2',
            'http://b.com/:z': '3',
        }
    }
    res = parse(xml, process_namespaces=True)
    assert res == d


def test_namespace_collapse():
    xml = """
    <root xmlns="http://defaultns.com/"
          xmlns:a="http://a.com/"
          xmlns:b="http://b.com/"
          version="1.00">
      <x a:attr="val">1</x>
      <a:y>2</a:y>
      <b:z>3</b:z>
    </root>
    """
    namespaces = {
        'http://defaultns.com/': '',
        'http://a.com/': 'ns_a',
    }
    d = {
        'root': {
            '@version': '1.00',
            '@xmlns': {
                '': 'http://defaultns.com/',
                'a': 'http://a.com/',
                'b': 'http://b.com/',
            },
            'x': {
                '@ns_a:attr': 'val',
                '#text': '1',
            },
            'ns_a:y': '2',
            'http://b.com/:z': '3',
        },
    }
    res = parse(xml, process_namespaces=True, namespaces=namespaces)
    assert res == d


def test_namespace_collapse_all():
    xml = """
    <root xmlns="http://defaultns.com/"
          xmlns:a="http://a.com/"
          xmlns:b="http://b.com/"
          version="1.00">
      <x a:attr="val">1</x>
      <a:y>2</a:y>
      <b:z>3</b:z>
    </root>
    """
    namespaces = collections.defaultdict(lambda: None)
    d = {
        'root': {
            '@version': '1.00',
            '@xmlns': {
                '': 'http://defaultns.com/',
                'a': 'http://a.com/',
                'b': 'http://b.com/',
            },
            'x': {
                '@attr': 'val',
                '#text': '1',
            },
            'y': '2',
            'z': '3',
        },
    }
    res = parse(xml, process_namespaces=True, namespaces=namespaces)
    assert res == d


def test_namespace_ignore():
    xml = """
    <root xmlns="http://defaultns.com/"
          xmlns:a="http://a.com/"
          xmlns:b="http://b.com/"
          version="1.00">
      <x>1</x>
      <a:y>2</a:y>
      <b:z>3</b:z>
    </root>
    """
    d = {
        'root': {
            '@xmlns': 'http://defaultns.com/',
            '@xmlns:a': 'http://a.com/',
            '@xmlns:b': 'http://b.com/',
            '@version': '1.00',
            'x': '1',
            'a:y': '2',
            'b:z': '3',
        },
    }
    assert parse(xml) == d


def test_force_list_basic():
    xml = """
    <servers>
      <server>
        <name>server1</name>
        <os>os1</os>
      </server>
    </servers>
    """
    expectedResult = {
        'servers': {
            'server': [
                {
                    'name': 'server1',
                    'os': 'os1',
                },
            ],
        }
    }
    assert parse(xml, force_list=('server',)) == expectedResult


def test_force_list_callable():
    xml = """
    <config>
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
        </servers>
        <skip>
            <server></server>
        </skip>
    </config>
    """

    def force_list(path, key, value):
        """Only return True for servers/server, but not for skip/server."""
        if key != 'server':
            return False
        return path and path[-1][0] == 'servers'

    expectedResult = {
        'config': {
            'servers': {
                'server': [
                    {
                        'name': 'server1',
                        'os': 'os1',
                    },
                ],
            },
            'skip': {
                'server': None,
            },
        },
    }
    assert parse(xml, force_list=force_list, dict_constructor=dict) == expectedResult


def test_disable_entities_true_rejects_xmlbomb():
    xml = """
    <!DOCTYPE xmlbomb [
        <!ENTITY a "1234567890" >
        <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
        <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">
    ]>
    <bomb>&c;</bomb>
    """
    with pytest.raises(ValueError, match="entities are disabled"):
        parse(xml, disable_entities=True)


def test_disable_entities_false_returns_xmlbomb():
    xml = """
    <!DOCTYPE xmlbomb [
        <!ENTITY a "1234567890" >
        <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
        <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">
    ]>
    <bomb>&c;</bomb>
    """
    bomb = "1234567890" * 64
    expectedResult = {'bomb': bomb}
    assert parse(xml, disable_entities=False) == expectedResult


def test_external_entity():
    xml = """
    <!DOCTYPE external [
        <!ENTITY ee SYSTEM "http://www.python.org/">
    ]>
    <root>&ee;</root>
    """
    with pytest.raises(ValueError, match="entities are disabled"):
        parse(xml)
    assert parse(xml, disable_entities=False) == {"root": None}


def test_external_entity_with_custom_expat():
    xml = """
    <!DOCTYPE external [
        <!ENTITY ee SYSTEM "http://www.python.org/">
    ]>
    <root>&ee;</root>
    """

    class CustomExpat:
        def __init__(self, external_entity_result):
            self.external_entity_result = external_entity_result

        def ParserCreate(self, *args, **kwargs):
            parser = ParserCreate(*args, **kwargs)

            def _handler(*args, **kwargs):
                return self.external_entity_result

            parser.ExternalEntityRefHandler = _handler
            return parser

        ExpatError = expat.ExpatError

    with pytest.raises(expat.ExpatError):
        parse(xml, disable_entities=False, expat=CustomExpat(0))
    assert parse(xml, disable_entities=False, expat=CustomExpat(1)) == {"root": None}
    with pytest.raises(ValueError):
        assert parse(xml, disable_entities=True, expat=CustomExpat(1))
    with pytest.raises(ValueError):
        assert parse(xml, disable_entities=True, expat=CustomExpat(0))


def test_disable_entities_true_allows_doctype_without_entities():
    xml = """<?xml version='1.0' encoding='UTF-8'?>
    <!DOCTYPE data SYSTEM "diagram.dtd">
    <foo>bar</foo>
    """
    assert parse(xml, disable_entities=True) == {"foo": "bar"}
    assert parse(xml, disable_entities=False) == {"foo": "bar"}


def test_disable_entities_allows_comments_by_default():
    xml = """
    <a>
        <!-- ignored -->
        <b>1</b>
    </a>
    """
    assert parse(xml) == {'a': {'b': '1'}}


def test_comments():
    xml = """
    <a>
      <b>
        <!-- b comment -->
        <c>
            <!-- c comment -->
            1
        </c>
        <d>2</d>
      </b>
    </a>
    """
    expectedResult = {
        'a': {
            'b': {
                '#comment': 'b comment',
                'c': {

                    '#comment': 'c comment',
                    '#text': '1',
                },
                'd': '2',
            },
        }
    }
    assert parse(xml, process_comments=True) == expectedResult


def test_streaming_with_comments_and_attrs():
    xml = """
    <a>
        <b attr1="value">
            <!-- note -->
            <c>cdata</c>
        </b>
    </a>
    """

    def handler(path, item):
        expected = {
            "@attr1": "value",
            "#comment": "note",
            "c": "cdata",
        }
        assert expected == item
        return True

    parse(xml, item_depth=2, item_callback=handler, process_comments=True)


def test_streaming_memory_usage():
    # Guard against re-introducing accumulation of streamed items into parent
    try:
        import tracemalloc
    except ImportError:
        pytest.skip("tracemalloc not available")

    NUM_ITEMS = 20000

    def xml_gen():
        yield "<a>"
        # generate many children with attribute and text
        for i in range(NUM_ITEMS):
            yield f'<b attr="v">{i % 10}</b>'
        yield "</a>"

    count = 0

    def cb(path, item):
        nonlocal count
        count += 1
        return True

    tracemalloc.start()
    parse(xml_gen(), item_depth=2, item_callback=cb)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert count == NUM_ITEMS
    # Peak memory should remain reasonably bounded; choose a conservative threshold
    # This value should stay well below pathological accumulation levels
    MAX_BYTES = 32 * 1024  # 32 KiB
    assert peak < MAX_BYTES, f"peak memory too high: {peak} bytes"


def test_streaming_attrs():
    xml = """
    <a>
        <b attr1="value">
            <c>cdata</c>
        </b>
    </a>
    """
    def handler(path, item):
        expected = {
            '@attr1': 'value',
            'c': 'cdata'
        }
        assert expected == item
        return True

    parse(xml, item_depth=2, item_callback=handler)


def test_namespace_on_root_without_other_attrs():
    xml = """
    <MyXML xmlns="http://www.xml.org/schemas/Test">
        <Tag1>Text1</Tag1>
        <Tag2 attr2="en">Text2</Tag2>
        <Tag3>Text3</Tag3>
        <Tag4 attr4="en">Text4</Tag4>
    </MyXML>
    """
    namespaces = {
        "http://www.xml.org/schemas/Test": None,
    }
    expected = {
        "MyXML": {
            "@xmlns": {"": "http://www.xml.org/schemas/Test"},
            "Tag1": "Text1",
            "Tag2": {"@attr2": "en", "#text": "Text2"},
            "Tag3": "Text3",
            "Tag4": {"@attr4": "en", "#text": "Text4"},
        }
    }
    assert parse(xml, process_namespaces=True, namespaces=namespaces) == expected
