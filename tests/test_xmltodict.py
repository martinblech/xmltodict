import xmltodict

try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from io import BytesIO as StringIO
except ImportError:
    StringIO = xmltodict.StringIO

def _encode(s):
    try:
        return bytes(s, 'ascii')
    except (NameError, TypeError):
        return s

class XMLToDictTestCase(unittest.TestCase):

    def test_string_vs_file(self):
        xml = '<a>data</a>'
        self.assertEqual(xmltodict.parse(xml),
                         xmltodict.parse(StringIO(_encode(xml))))

    def test_minimal(self):
        self.assertEqual(xmltodict.parse('<a/>'),
                         {'a': None})
        self.assertEqual(xmltodict.parse('<a/>', force_cdata=True),
                         {'a': None})

    def test_simple(self):
        self.assertEqual(xmltodict.parse('<a>data</a>'),
                         {'a': 'data'})

    def test_force_cdata(self):
        self.assertEqual(xmltodict.parse('<a>data</a>', force_cdata=True),
                         {'a': {'#text': 'data'}})

    def test_custom_cdata(self):
        self.assertEqual(xmltodict.parse('<a>data</a>',
                                         force_cdata=True,
                                         cdata_key='_CDATA_'),
                         {'a': {'_CDATA_': 'data'}})

    def test_list(self):
        self.assertEqual(xmltodict.parse('<a><b>1</b><b>2</b><b>3</b></a>'),
                         {'a': {'b': ['1', '2', '3']}})

    def test_attrib(self):
        self.assertEqual(xmltodict.parse('<a href="xyz"/>'),
                         {'a': {'@href': 'xyz'}})

    def test_skip_attrib(self):
        self.assertEqual(xmltodict.parse('<a href="xyz"/>', xml_attribs=False),
                         {'a': None})

    def test_custom_attrib(self):
        self.assertEqual(xmltodict.parse('<a href="xyz"/>',
                                         attr_prefix='!'),
                         {'a': {'!href': 'xyz'}})

    def test_attrib_and_cdata(self):
        self.assertEqual(xmltodict.parse('<a href="xyz">123</a>'),
                         {'a': {'@href': 'xyz', '#text': '123'}})

    def test_semi_structured(self):
        self.assertEqual(xmltodict.parse('<a>abc<b/>def</a>'),
                         {'a': {'b': None, '#text': 'abcdef'}})
        self.assertEqual(xmltodict.parse('<a>abc<b/>def</a>',
                                         cdata_separator='\n'),
                         {'a': {'b': None, '#text': 'abc\ndef'}})

    def test_nested_semi_structured(self):
        self.assertEqual(xmltodict.parse('<a>abc<b>123<c/>456</b>def</a>'),
                         {'a': {'#text': 'abcdef', 'b': {
                             '#text': '123456', 'c': None}}})

    def test_streaming(self):
        def cb(path, item):
            cb.count += 1
            self.assertEqual(path, [('a', {'x': 'y'}), ('b', None)])
            self.assertEqual(item, str(cb.count))
            return True
        cb.count = 0
        xmltodict.parse('<a x="y"><b>1</b><b>2</b><b>3</b></a>',
                        2, cb)
        self.assertEqual(cb.count, 3)

    def test_streaming_interrupt(self):
        def cb(path, item):
            return False
        try:
            xmltodict.parse('<a>x</a>', 1, cb)
            self.fail()
        except xmltodict.ParsingInterrupted:
            pass

    def test_postprocessor(self):
        def postprocessor(path, key, value):
            try:
                return key + ':int', int(value)
            except (ValueError, TypeError):
                return key, value
        self.assertEqual({'a': {'b:int': [1, 2], 'b': 'x'}},
                         xmltodict.parse('<a><b>1</b><b>2</b><b>x</b></a>',
                                         postprocessor=postprocessor))

    def test_postprocessor_skip(self):
        def postprocessor(path, key, value):
            if key == 'b':
                value = int(value)
                if value == 3:
                    return None
            return key, value
        self.assertEqual({'a': {'b': [1, 2]}},
                         xmltodict.parse('<a><b>1</b><b>2</b><b>3</b></a>',
                                         postprocessor=postprocessor))

    def test_postprocess_whitespace(self):
        xml = """
        <root>


          <emptya>           </emptya>
          <emptyb attr="attrvalue">


          </emptyb>
          <value>hello</value>
        </root>
        """
        def skip_whitespace(path, key, value):
            try:
                if not value.strip():
                    return None
            except:
                pass
            return key, value
        self.assertEqual(
            xmltodict.parse(xml, postprocessor=skip_whitespace),
            {'root': {'emptyb': {'@attr': 'attrvalue'}, 'value': 'hello'}})
