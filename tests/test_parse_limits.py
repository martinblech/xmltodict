import io
import pytest
from xmltodict import parse, ParsingInterrupted, ParsingLimitExceeded


@pytest.mark.parametrize('option', ['max_depth', 'max_nodes'])
@pytest.mark.parametrize('value', [0, -1, True, False, 1.5, '2', [], {}])
def test_invalid_limits(option, value):
    with pytest.raises(ValueError, match='positive integer or None'):
        parse('<r/>', **{option: value})


@pytest.mark.parametrize('kind', ['string', 'file', 'generator'])
def test_depth_boundary(kind):
    xml = '<r><a><b/></a></r>'
    def source():
        if kind == 'file':
            return io.BytesIO(xml.encode())
        if kind == 'generator':
            return (xml[i:i+2] for i in range(0, len(xml), 2))
        return xml
    assert parse(source(), max_depth=3) == {'r': {'a': {'b': None}}}
    with pytest.raises(ParsingLimitExceeded, match='max_depth'):
        parse(source(), max_depth=2)


def test_root_depth_one():
    assert parse('<r/>', max_depth=1, max_nodes=1) == {'r': None}
    with pytest.raises(ParsingLimitExceeded):
        parse('<r><a/></r>', max_depth=1)


@pytest.mark.parametrize('namespaces', [True, False])
@pytest.mark.parametrize('attributes', [True, False])
def test_namespace_and_attribute_count(namespaces, attributes):
    xml = '<r xmlns="urn:r" xmlns:x="urn:x" a="1"><x:a/><b xmlns="urn:b"/></r>'
    # Three elements, three namespace declarations, one ordinary attribute.
    parse(xml, max_nodes=7, process_namespaces=namespaces, xml_attribs=attributes)
    with pytest.raises(ParsingLimitExceeded, match='max_nodes'):
        parse(xml, max_nodes=6, process_namespaces=namespaces, xml_attribs=attributes)


def test_text_comments_not_nodes():
    assert parse('<r><!--x-->text</r>', process_comments=True, max_nodes=1)


def test_streaming_cumulative_nodes():
    seen = []
    with pytest.raises(ParsingLimitExceeded, match='max_nodes'):
        parse('<r><x>1</x><x>2</x><x>3</x></r>', max_nodes=3, item_depth=2,
              item_callback=lambda path, item: seen.append(item) or True)
    assert seen == ['1', '2']


def test_depth_above_streaming_cutoff():
    seen = []
    with pytest.raises(ParsingLimitExceeded, match='max_depth'):
        parse('<r><x><a/></x></r>', max_depth=2, item_depth=4,
              item_callback=lambda path, item: seen.append(item) or True)
    assert seen == []


def test_callback_interrupt_preserved():
    with pytest.raises(ParsingInterrupted):
        parse('<r><x/></r>', max_nodes=2, item_depth=2,
              item_callback=lambda path, item: False)


def test_prevents_rejected_element_processing():
    processed = []
    def postprocessor(path, key, value):
        processed.append(key)
        return key, value
    with pytest.raises(ParsingLimitExceeded):
        parse('<r><x a="1"/></r>', max_nodes=1, postprocessor=postprocessor)
    assert processed == []


def test_default_and_explicit_none_same():
    xml = '<r><x a="1">text</x><x/></r>'
    assert parse(xml) == parse(xml, max_depth=None, max_nodes=None)


def test_entity_default_preserved():
    with pytest.raises(ValueError, match='entities are disabled'):
        parse('<!DOCTYPE r [<!ENTITY x "a">]><r>&x;</r>', max_nodes=4)


@pytest.mark.parametrize('kind', ['string', 'file', 'generator'])
def test_node_boundary_input_modes(kind):
    xml = '<r a="1"><x/></r>'
    def source():
        if kind == 'file':
            return io.BytesIO(xml.encode())
        if kind == 'generator':
            return (xml[i:i+2] for i in range(0, len(xml), 2))
        return xml
    assert parse(source(), max_nodes=3) == {'r': {'@a': '1', 'x': None}}
    with pytest.raises(ParsingLimitExceeded, match='max_nodes'):
        parse(source(), max_nodes=2)


def test_streaming_success_and_depth_resets():
    seen = []
    result = parse('<r><x>1</x><x>2</x></r>', max_depth=2, max_nodes=3,
                   item_depth=2, item_callback=lambda p, i: seen.append(i) or True)
    assert result is None
    assert seen == ['1', '2']
