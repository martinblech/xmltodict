from xmltodict import parse, ParsingInterrupted

try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from io import BytesIO as StringIO
except ImportError:
    from xmltodict import StringIO


def _encode(s):
    try:
        return bytes(s, 'ascii')
    except (NameError, TypeError):
        return s


class XMLToDictTestCase(unittest.TestCase):

    def test_string_vs_file(self):
        xml = '<a>data</a>'
        self.assertEqual(parse(xml),
                         parse(StringIO(_encode(xml))))

    def test_minimal(self):
        self.assertEqual(parse('<a/>'),
                         {'a': None})
        self.assertEqual(parse('<a/>', force_cdata=True),
                         {'a': None})

    def test_simple(self):
        self.assertEqual(parse('<a>data</a>'),
                         {'a': 'data'})

    def test_force_cdata(self):
        self.assertEqual(parse('<a>data</a>', force_cdata=True),
                         {'a': {'#text': 'data'}})

    def test_custom_cdata(self):
        self.assertEqual(parse('<a>data</a>',
                               force_cdata=True,
                               cdata_key='_CDATA_'),
                         {'a': {'_CDATA_': 'data'}})

    def test_list(self):
        self.assertEqual(parse('<a><b>1</b><b>2</b><b>3</b></a>'),
                         {'a': {'b': ['1', '2', '3']}})

    def test_attrib(self):
        self.assertEqual(parse('<a href="xyz"/>'),
                         {'a': {'@href': 'xyz'}})

    def test_skip_attrib(self):
        self.assertEqual(parse('<a href="xyz"/>', xml_attribs=False),
                         {'a': None})

    def test_custom_attrib(self):
        self.assertEqual(parse('<a href="xyz"/>',
                               attr_prefix='!'),
                         {'a': {'!href': 'xyz'}})

    def test_attrib_and_cdata(self):
        self.assertEqual(parse('<a href="xyz">123</a>'),
                         {'a': {'@href': 'xyz', '#text': '123'}})

    def test_semi_structured(self):
        self.assertEqual(parse('<a>abc<b/>def</a>'),
                         {'a': {'b': None, '#text': 'abcdef'}})
        self.assertEqual(parse('<a>abc<b/>def</a>',
                               cdata_separator='\n'),
                         {'a': {'b': None, '#text': 'abc\ndef'}})

    def test_nested_semi_structured(self):
        self.assertEqual(parse('<a>abc<b>123<c/>456</b>def</a>'),
                         {'a': {'#text': 'abcdef', 'b': {
                             '#text': '123456', 'c': None}}})

    def test_skip_whitespace(self):
        xml = """
        <root>


          <emptya>           </emptya>
          <emptyb attr="attrvalue">


          </emptyb>
          <value>hello</value>
        </root>
        """
        self.assertEqual(
            parse(xml),
            {'root': {'emptya': None,
                      'emptyb': {'@attr': 'attrvalue'},
                      'value': 'hello'}})

    def test_keep_whitespace(self):
        xml = "<root> </root>"
        self.assertEqual(parse(xml), dict(root=None))
        self.assertEqual(parse(xml, strip_whitespace=False),
                         dict(root=' '))

    def test_streaming(self):
        def cb(path, item):
            cb.count += 1
            self.assertEqual(path, [('a', {'x': 'y'}), ('b', None)])
            self.assertEqual(item, str(cb.count))
            return True
        cb.count = 0
        parse('<a x="y"><b>1</b><b>2</b><b>3</b></a>',
              item_depth=2, item_callback=cb)
        self.assertEqual(cb.count, 3)

    def test_streaming_interrupt(self):
        cb = lambda path, item: False
        self.assertRaises(ParsingInterrupted,
                          parse, '<a>x</a>',
                          item_depth=1, item_callback=cb)

    def test_postprocessor(self):
        def postprocessor(path, key, value):
            try:
                return key + ':int', int(value)
            except (ValueError, TypeError):
                return key, value
        self.assertEqual({'a': {'b:int': [1, 2], 'b': 'x'}},
                         parse('<a><b>1</b><b>2</b><b>x</b></a>',
                               postprocessor=postprocessor))

    def test_postprocessor_skip(self):
        def postprocessor(path, key, value):
            if key == 'b':
                value = int(value)
                if value == 3:
                    return None
            return key, value
        self.assertEqual({'a': {'b': [1, 2]}},
                         parse('<a><b>1</b><b>2</b><b>3</b></a>',
                               postprocessor=postprocessor))

    def test_unicode(self):
        try:
            value = unichr(39321)
        except NameError:
            value = chr(39321)
        self.assertEqual({'a': value},
                         parse('<a>%s</a>' % value))

    def test_encoded_string(self):
        try:
            value = unichr(39321)
        except NameError:
            value = chr(39321)
        xml = '<a>%s</a>' % value
        self.assertEqual(parse(xml),
                         parse(xml.encode('utf-8')))

    def test_namespace_support(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x>1</x>
          <a:y>2</a:y>
          <b:z>3</b:z>
        </root>
        """
        d = {
            'http://defaultns.com/:root': {
                'http://defaultns.com/:x': '1',
                'http://a.com/:y': '2',
                'http://b.com/:z': '3',
            }
        }
        self.assertEqual(parse(xml, process_namespaces=True), d)

    def test_namespace_collapse(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x>1</x>
          <a:y>2</a:y>
          <b:z>3</b:z>
        </root>
        """
        namespaces = {
            'http://defaultns.com/': None,
            'http://a.com/': 'ns_a',
        }
        d = {
            'root': {
                'x': '1',
                'ns_a:y': '2',
                'http://b.com/:z': '3',
            },
        }
        self.assertEqual(
            parse(xml, process_namespaces=True, namespaces=namespaces), d)

    def test_namespace_ignore(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
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
                'x': '1',
                'a:y': '2',
                'b:z': '3',
            },
        }
        self.assertEqual(parse(xml), d)
