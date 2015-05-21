from xmltodict import parse, Parser, parse_lxml, LXMLParser, ParsingInterrupted
import xmltodict

try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from io import BytesIO as StringIO
except ImportError:
    from xmltodict import StringIO

unicode = xmltodict._unicode

def _encode(s):
    try:
        return bytes(s, 'ascii')
    except (NameError, TypeError):
        return s

if not hasattr(unittest.TestCase, "assertIsInstance"):
    need_assertIsInstance = True
else:
    need_assertIsInstance = False

if not hasattr(unittest.TestCase, "assertIsNotInstance"):
    need_assertIsNotInstance = True
else:
    need_assertIsNotInstance = False

class XMLToDictTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.parse = parse
        self.Parser = Parser

    if need_assertIsInstance:
        def assertIsInstance(self, a, b, msg=None):
            self.assertTrue(isinstance(a, b), msg=msg)

    if need_assertIsNotInstance:
        def assertIsNotInstance(self, a, b, msg=None):
            self.assertFalse(isinstance(a, b), msg=msg)

    def xmlTextToTestFormat(self, xml):
        return xml

    def test_parse_class(self):
        xml = '<a>data</a>'
        xml = self.xmlTextToTestFormat(xml)
        parser = self.Parser()
        self.assertIsInstance(parser, self.Parser)
        rv = parser(xml)
        self.assertIsInstance(rv, dict)
        self.assertIsNotInstance(rv, xmltodict.XMLDictNode)
        self.assertEqual(rv, {'a': 'data'})
        rv = parser(xml, new_style=True)
        self.assertIsInstance(rv, xmltodict.XMLDictNode)
        self.assertEqual(rv, {'a': 'data'})

    def test_parse_class_defaults(self):
        xml = '<a>data</a>'
        xml = self.xmlTextToTestFormat(xml)
        parser = self.Parser(force_cdata=True)
        self.assertEqual(parser(xml), {'a': {'#text': 'data'}})
        self.assertEqual(parser(xml, force_cdata=False),
                         {'a': 'data'})
        self.assertEqual(parser(xml), {'a': {'#text': 'data'}})

    def test_string_vs_file(self):
        xml = '<a>data</a>'
        xml = self.xmlTextToTestFormat(xml)
        self.assertEqual(self.parse(xml),
                         self.parse(StringIO(_encode(xml))))

    def test_minimal(self):
        xml = '<a/>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': None}
        self.assertEqual(self.parse(xml), expectedResult)
        self.assertEqual(self.parse(xml, force_cdata=True),
                         expectedResult)
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        rv = self.parse(xml, force_cdata=True, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())

    def test_simple(self):
        xml = '<a>data</a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': 'data'}
        self.assertEqual(self.parse(xml), expectedResult)
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertEqual(rv.getXMLattributes(), {})

    def test_list_simple(self):
        xml = '<a><b>data1</b><b>data2</b></a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'b': ['data1', 'data2']}}
        self.assertEqual(self.parse(xml), expectedResult)
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertEqual(rv.getXMLattributes(), {})
        self.assertFalse(rv['a'].hasXMLattributes())
        self.assertFalse(rv['a']['b'].hasXMLattributes())
        self.assertFalse(rv['a']['b'][0].hasXMLattributes())
        self.assertFalse(rv['a']['b'][1].hasXMLattributes())

    def test_force_cdata(self):
        xml = '<a>data</a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'#text': 'data'}}
        parser = self.Parser(force_cdata=True)
        self.assertEqual(parser(xml), expectedResult)
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())

    def test_custom_cdata(self):
        xml = '<a>data</a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'_CDATA_': 'data'}}
        parser = self.Parser(force_cdata=True, cdata_key='_CDATA_')
        self.assertEqual(parser(xml), expectedResult)
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())

    def test_list(self):
        xml = '<a><b>1</b><b>2</b><b>3</b></a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'b': ['1', '2', '3']}}
        self.assertEqual(self.parse(xml), expectedResult)
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())

    def test_attrib_root(self):
        xml = '<a href="xyz"/>'
        xml = self.xmlTextToTestFormat(xml)
        self.assertEqual(self.parse(xml),
                         {'a': {'@href': 'xyz'}})
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, {'a': ''})
        self.assertFalse(rv.hasXMLattributes())
        self.assertTrue(rv['a'].hasXMLattributes())
        self.assertEqual(rv['a'].getXMLattribute("href", None), 'xyz')
        self.assertEqual(rv['a'].getXMLattributes(), {'href': 'xyz'})

    def test_attrib_leaf(self):
        xml = '<root><a href="xyz"/></root>'
        xml = self.xmlTextToTestFormat(xml)
        self.assertEqual(self.parse(xml),
                         {'root': {'a': {'@href': 'xyz'}}})
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, {'root': {'a': ''}})
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        nodea = rv['root']['a']
        self.assertTrue(nodea.hasXMLattributes())
        self.assertEqual(nodea.getXMLattribute("href", None), 'xyz')
        self.assertEqual(nodea.getXMLattributes(), {'href': 'xyz'})

    def test_skip_attrib(self):
        xml = '<a href="xyz"/>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': None}
        parser = self.Parser(xml_attribs=False)
        self.assertEqual(parser(xml), expectedResult)
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())

    def test_custom_attrib(self):
        xml = '<a href="xyz"/>'
        xml = self.xmlTextToTestFormat(xml)
        parser = self.Parser(attr_prefix='!')
        self.assertEqual(parser(xml),
                         {'a': {'!href': 'xyz'}})
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, {'a': ''})
        self.assertFalse(rv.hasXMLattributes())
        self.assertTrue(rv['a'].hasXMLattributes())
        self.assertEqual(rv['a'].getXMLattributes(),
                         {'!href': 'xyz'})

    def test_attrib_and_cdata(self):
        xml = '<a href="xyz">123</a>'
        xml = self.xmlTextToTestFormat(xml)
        self.assertEqual(self.parse(xml),
                         {'a': {'@href': 'xyz', '#text': '123'}})
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, {'a': '123'})
        self.assertFalse(rv.hasXMLattributes())
        self.assertTrue(rv['a'].hasXMLattributes())
        self.assertEqual(rv['a'].getXMLattributes(),
                         {'href': 'xyz'})

    def test_semi_structured(self):
        xml = '<a>abc<b/>def</a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'b': None, '#text': 'abcdef'}}
        self.assertEqual(self.parse(xml), expectedResult)
        self.assertEqual(self.parse(xml, new_style=True), expectedResult)
        expectedResult = {'a': {'b': None, '#text': 'abc\ndef'}}
        parser = self.Parser(cdata_separator='\n')
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_nested_semi_structured(self):
        xml = '<a>abc<b>123<c/>456</b>def</a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'#text': 'abcdef', 'b': {
            '#text': '123456', 'c': None}}}
        self.assertEqual(self.parse(xml), expectedResult)
        self.assertEqual(self.parse(xml, new_style=True), expectedResult)

    def test_skip_whitespace(self):
        xml = """
        <root>


          <emptya>           </emptya>
          <emptyb attr="attrvalue">


          </emptyb>
          <value>hello</value>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        self.assertEqual(
            self.parse(xml),
            {'root': {'emptya': None,
                      'emptyb': {'@attr': 'attrvalue'},
                      'value': 'hello'}})
        rv = self.parse(xml, new_style=True)
        self.assertEqual(
            rv,
            {'root': {'emptya': None,
                      'emptyb': '',
                      'value': 'hello'}})
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        self.assertFalse(rv['root']['value'].hasXMLattributes())
        self.assertTrue(rv['root']['emptyb'].hasXMLattributes())
        self.assertEqual(rv['root']['emptyb'].getXMLattributes(),
                         {'attr': 'attrvalue'})

    def test_keep_whitespace(self):
        xml = "<root> </root>"
        xml = self.xmlTextToTestFormat(xml)
        self.assertEqual(self.parse(xml), dict(root=None))
        self.assertEqual(self.parse(xml, new_style=True), dict(root=None))
        parser = self.Parser(strip_whitespace=False)
        self.assertEqual(parser(xml), dict(root=' '))
        self.assertEqual(parser(xml, new_style=True), dict(root=' '))

    def test_streaming(self):
        def cb(path, item):
            cb.count += 1
            self.assertEqual(path, [('a', {'x': 'y'}), ('b', None)])
            self.assertEqual(item, str(cb.count))
            return True
        xml = '<a x="y"><b>1</b><b>2</b><b>3</b></a>'
        xml = self.xmlTextToTestFormat(xml)
        parser = self.Parser(item_depth=2, item_callback=cb)
        cb.count = 0
        parser(xml)
        self.assertEqual(cb.count, 3)
        cb.count = 0
        parser(xml, new_style=True)
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
        xml = '<a><b>1</b><b>2</b><b>x</b></a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'b:int': [1, 2], 'b': 'x'}}
        parser = self.Parser(postprocessor=postprocessor)
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_postprocessor_skip(self):
        def postprocessor(path, key, value):
            if key == 'b':
                value = int(value)
                if value == 3:
                    return None
            return key, value
        xml = '<a><b>1</b><b>2</b><b>3</b></a>'
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': {'b': [1, 2]}}
        parser = self.Parser(postprocessor=postprocessor)
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_unicode(self):
        try:
            value = unichr(39321)
        except NameError:
            value = chr(39321)
        xml = '<a>%s</a>' % value
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {'a': value}
        self.assertEqual(self.parse(xml), expectedResult)
        self.assertEqual(self.parse(xml, new_style=True), expectedResult)

    def test_encoded_string(self):
        try:
            value = unichr(39321)
        except NameError:
            value = chr(39321)
        xml = '<a>%s</a>' % value
        xml = self.xmlTextToTestFormat(xml)
        if not (isinstance(xml, str) or isinstance(xml, unicode)):
            raise unittest.SkipTest("Test only makes sense when parsing text.")

        self.assertEqual(self.parse(xml),
                         self.parse(xml.encode('utf-8')))
        self.assertEqual(self.parse(xml, new_style=True),
                         self.parse(xml.encode('utf-8'), new_style=True))

    def test_namespace_support(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x a:attr="val">1</x>
          <a:y>2</a:y>
          <b:z>3</b:z>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'http://defaultns.com/:root': {
                'http://defaultns.com/:x': {
                    '@http://a.com/:attr': 'val',
                    '#text': '1',
                },
                'http://a.com/:y': '2',
                'http://b.com/:z': '3',
            }
        }
        parser=self.Parser(process_namespaces=True)
        self.assertEqual(parser(xml), expectedResult)
        expectedResult = {
            'http://defaultns.com/:root': {
                'http://defaultns.com/:x': '1',
                'http://a.com/:y': '2',
                'http://b.com/:z': '3',
            }
        }
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['http://defaultns.com/:root'].hasXMLattributes())
        self.assertFalse(rv['http://defaultns.com/:root']['http://a.com/:y'].hasXMLattributes())
        self.assertFalse(rv['http://defaultns.com/:root']['http://b.com/:z'].hasXMLattributes())
        self.assertEqual(
            rv['http://defaultns.com/:root']['http://defaultns.com/:x'].getXMLattributes(),
            {'http://a.com/:attr': 'val'})

    def test_namespace_collapse(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x a:attr="val">1</x>
          <a:y>2</a:y>
          <b:z>3</b:z>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        namespaces = {
            'http://defaultns.com/': None,
            'http://a.com/': 'ns_a',
        }
        expectedResult = {
            'root': {
                'x': {
                    '@ns_a:attr': 'val',
                    '#text': '1',
                },
                'ns_a:y': '2',
                'http://b.com/:z': '3',
            },
        }
        parser=self.Parser(process_namespaces=True, namespaces=namespaces)
        self.assertEqual(parser(xml), expectedResult)
        expectedResult = {
            'root': {
                'x': '1',
                'ns_a:y': '2',
                'http://b.com/:z': '3',
            }
        }
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        self.assertFalse(rv['root']['ns_a:y'].hasXMLattributes())
        self.assertFalse(rv['root']['http://b.com/:z'].hasXMLattributes())
        self.assertTrue(rv['root']['x'].hasXMLattributes())
        self.assertEqual(rv['root']['x'].getXMLattributes(),
                         {'ns_a:attr': 'val'})

    def translate_namespace(self, root, ns_map, _inherited_ns={}, force_cdata=False):
        """
        Recursively translate the namespace identifiers. Return a
        new dictionary with the new namespace identifiers, but NO
        xmlns attributes.

        The initial callers hould NOT specify _inherited_ns. That
        will be populated on recursive calls.

        The initial caller should specify a `root`, which points to
        the dictionary that contains the root node; and, the `ns_map`,
        which is a dictionary with URLs as keys and NS identifiers
        as values. (The default NS identifier should be specified as
        "".)

        KNOWN BUG: If the namespaces are defined in child nodes that
        are in a list and the child nodes in the list have different
        xmlns attributes, this may not work correctly.
        """
        if isinstance(root, list):
            rv = list()
            for v in root:
                rv.append(self.translate_namespace(v, ns_map, _inherited_ns, force_cdata))
            return rv

        if not (isinstance(root, dict) or isinstance(root, xmltodict.XMLCDATANode)):
            return root

        if isinstance(root, xmltodict.XMLCDATANode):
            items = []
            rv = xmltodict.XMLCDATANode(root)
        else:
            items = list(root.items())
            if isinstance(root, xmltodict.XMLDictNode):
                rv = xmltodict.XMLDictNode()
            else:
                rv = dict()
        if isinstance(root, xmltodict.XMLCDATANode) or isinstance(root, xmltodict.XMLDictNode):
            for (k,v) in root.getXMLattributes().items():
                items.append(("@" + k, v))

        for (k,v) in items:
            if k.startswith("@xmlns"):
                pass
            else:
                new_ns = dict(_inherited_ns)
                child = v

                # This doesn't work quite right. Good enough for now.
                while isinstance(child, list):
                    child = child[0]

                # Build a namespace dictionary for this node.
                if isinstance(child, dict):
                    for (childK, childV) in child.items():
                        if childK.startswith("@xmlns"):
                            index = childK.rfind(":")
                            if index < 0:
                                self.assertEqual(childK, "@xmlns")
                                new_ns[""] = childV
                            else:
                                new_ns[childK[index+1:]] = childV
                if hasattr(child, "getXMLattributes"):
                    for (childK, childV) in child.getXMLattributes().items():
                        if childK.startswith("xmlns"):
                            index = childK.rfind(":")
                            if index < 0:
                                self.assertEqual(childK, "xmlns")
                                new_ns[""] = childV
                            else:
                                new_ns[childK[index+1:]] = childV

                # Translate the namespace for the tag, if necessary.
                if k[0] == "@":
                    basetag = k[1:]
                else:
                    basetag = k
                index = basetag.rfind(":")
                if index < 0:
                    nsurl = new_ns.get("")
                else:
                    nsurl = new_ns.get(basetag[:index])
                    self.assertTrue(
                        nsurl,
                        msg="Mapping for namespace \"%s\" not found" % (
                            k[:index],
                        ))
                    basetag = basetag[index+1:]
                if (not nsurl) or (not ns_map.get(nsurl, '@@NOMATCH@@')):
                    newtag = basetag
                else:
                    self.assertTrue(nsurl in ns_map)
                    newtag = ns_map[nsurl] + ":" + basetag

                # Build the entry
                if (isinstance(rv, xmltodict.XMLDictNode) or isinstance(rv, xmltodict.XMLCDATANode)) and k[0] == "@":
                    rv.setXMLattribute(newtag, v)
                else:
                    if k[0] == "@":
                        newtag = "@" + newtag
                    rv[newtag] = self.translate_namespace(v, ns_map,
                                                          new_ns,
                                                          force_cdata)

        # Special case: If all we are returning is a text node, promote
        # it.
        if isinstance(rv, dict) and list(rv.keys()) == ['#text'] and (not force_cdata):
            if isinstance(rv, xmltodict.XMLDictNode):
                newAttrs = rv.getXMLattributes()
                newAttrs.update(rv['#text'].getXMLattributes())
                rv['#text'].XMLattrs = newAttrs
            return rv['#text']
        return rv

    def test_namespace_ignore(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/"
              xmlns:c="http://c.com/">
          <x>1</x>
          <a:y c:attr="val">2</a:y>
          <b:z>3</b:z>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'root': {
                '@xmlns': 'http://defaultns.com/',
                '@xmlns:a': 'http://a.com/',
                '@xmlns:b': 'http://b.com/',
                '@xmlns:c': 'http://c.com/',
                'x': '1',
                'a:y': {
                    '@c:attr': 'val',
                    '#text': '2',
                },
                'b:z': '3',
            },
        }
        if isinstance(xml, str) or isinstance(xml, unicode) or hasattr(xml, "nsmap") or (hasattr(xml, "getroot") and hasattr(xml.getroot(), "nsmap")):
            self.assertEqual(self.parse(xml), expectedResult)
            expectedAttributes = dict(root={})
            for (k,v) in list(expectedResult['root'].items()):
                if k.startswith("@"):
                    expectedAttributes['root'][k[1:]] = expectedResult['root'].pop(k)
                elif isinstance(v, dict):
                    expectedAttributes[k]={}
                    for childK in list(expectedResult['root'][k].keys()):
                        if childK.startswith("@"):
                            expectedAttributes[k][childK[1:]] = expectedResult['root'][k].pop(childK)
                    if list(expectedResult['root'][k].keys()) == ['#text']:
                        expectedResult['root'][k] = expectedResult['root'][k]['#text']
            rv = self.parse(xml, new_style=True)
            self.assertEqual(rv, expectedResult)
            self.assertEqual(rv['root'].getXMLattributes(),
                             expectedAttributes.pop('root'))
            for k in expectedAttributes.keys():
                self.assertEqual(rv['root'][k].getXMLattributes(),
                                 expectedAttributes[k])
        else:
            # Here, the NS identifiers may be different because they
            # were lost during parsing.
            # The key thing is that the NS relationships be the
            # same.
            ns_map = dict()
            for k in list(expectedResult['root'].keys()):
                if k.startswith('@xmlns'):
                    v = expectedResult['root'].pop(k)
                    if k.rfind(":") >= 0:
                        k = k[k.rfind(":")+1:]
                    else:
                        k = ""
                    ns_map[v] = k
            rv = self.translate_namespace(self.parse(xml), ns_map)
            self.assertEqual(rv, expectedResult)
            rv = self.translate_namespace(self.parse(xml, new_style=True),
                                          ns_map)
            for (k,v) in list(expectedResult['root'].items()):
                if k.startswith("@"):
                    self.assertEqual(rv['root'].getXMLattribute(k[1:]),
                                     expectedResult['root'].pop(k))
                elif isinstance(v, dict):
                    for childK in list(expectedResult['root'][k].keys()):
                        if childK.startswith("@"):
                            self.assertTrue(
                                childK[1:] in rv['root'][k].getXMLattributes(),
                                msg="%s attribute not in attribute store %r" % (
                                    childK[1:],
                                    rv['root'][k].getXMLattributes()
                                )
                            )
                            self.assertEqual(
                                rv['root'][k].getXMLattribute(childK[1:]),
                                expectedResult['root'][k].pop(childK),
                            )
                    if list(expectedResult['root'][k].keys()) == ['#text']:
                        expectedResult['root'][k] = expectedResult['root'][k]['#text']
            self.assertEqual(rv, expectedResult)

    def test_namespace_strip_basic(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x>1</x>
          <a:y>2</a:y>
          <b:z>3</b:z>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'root': {
                'x': '1',
                'y': '2',
                'z': '3',
            }
        }
        parser = self.Parser(strip_namespace=True)
        self.assertEqual(parser(xml), expectedResult)
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        for k in rv['root'].keys():
            self.assertFalse(rv['root'][k].hasXMLattributes())

    def test_namespace_strip_attributes_positive(self):
        xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x>1</x>
          <a:y a:a="val">2</a:y>
          <b:z a="val1" a:b="val2">3</b:z>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'root': {
                'x': '1',
                'y': {
                    '@a': 'val',
                    '#text': '2',
                },
                'z': {
                    '@a': 'val1',
                    '@b': 'val2',
                    '#text': '3',
                },
            }
        }
        parser = self.Parser(strip_namespace=True)
        self.assertEqual(parser(xml), expectedResult)
        expectedResult = {
            'root': {
                'x': '1',
                'y': '2',
                'z': '3',
            }
        }
        rv = parser(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        self.assertFalse(rv['root']['x'].hasXMLattributes())
        self.assertEqual(rv['root']['y'].getXMLattributes(),
                         {'a': 'val'})
        self.assertEqual(rv['root']['z'].getXMLattributes(),
                         {'a': 'val1', 'b': 'val2'})

    def test_namespace_strip_attributes_negative(self):
        xml1 = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x a="val1" a:a="val2">1</x>
        </root>
        """
        xml1 = self.xmlTextToTestFormat(xml1)
        xml2 = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x a:a="val1" b:a="val2">1</x>
        </root>
        """
        xml2 = self.xmlTextToTestFormat(xml2)
        parser = self.Parser(strip_namespace=True)
        for xml in (xml1, xml2):
            self.assertRaises(ValueError, parser, xml)
            self.assertRaises(ValueError, parser, xml, new_style=True)

    def test_newstyle_xmlattribute_get_negative(self):
        xml = """
        <root>
          <x a="val1">1</x>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'root': {
                'x': '1',
            },
        }
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        self.assertTrue(rv['root']['x'].hasXMLattributes())
        self.assertEqual(rv['root']['x'].getXMLattribute('a'), "val1")
        self.assertEqual(rv['root']['x'].getXMLattribute('b', '@@@@'), '@@@@')
        self.assertRaises(KeyError, rv['root']['x'].getXMLattribute, 'b')

    def test_newstyle_xmlattribute_set(self):
        xml = """
        <root>
          <x a="val1">1</x>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'root': {
                'x': '1',
            },
        }
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        self.assertTrue(rv['root']['x'].hasXMLattributes())
        self.assertEqual(rv['root']['x'].getXMLattribute('a'), "val1")
        rv['root']['x'].setXMLattribute('a', "val2")
        self.assertEqual(rv['root']['x'].getXMLattribute('a'), "val2")
        self.assertRaises(KeyError, rv['root']['x'].getXMLattribute, 'b')
        rv['root']['x'].setXMLattribute('b', "val3")
        self.assertEqual(rv['root']['x'].getXMLattribute('a'), "val2")
        self.assertEqual(rv['root']['x'].getXMLattribute('b'), "val3")
        self.assertEqual(rv['root']['x'].getXMLattributes(),
                         {'a': "val2", 'b': "val3"})
        self.assertEqual(rv['root'].getXMLattributes(), dict())
        rv['root'].setXMLattribute('newattrib', "@@@")
        self.assertTrue(rv['root'].hasXMLattributes())
        self.assertEqual(rv['root'].getXMLattribute('newattrib'), "@@@")
        self.assertEqual(rv['root'].getXMLattributes(),
                         {'newattrib': "@@@"})

    def test_newstyle_xmlattribute_delete(self):
        xml = """
        <root>
          <x a="val1">1</x>
        </root>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'root': {
                'x': '1',
            },
        }
        rv = self.parse(xml, new_style=True)
        self.assertEqual(rv, expectedResult)
        self.assertFalse(rv.hasXMLattributes())
        self.assertFalse(rv['root'].hasXMLattributes())
        self.assertTrue(rv['root']['x'].hasXMLattributes())
        self.assertEqual(rv['root']['x'].getXMLattribute('a'), "val1")
        self.assertEqual(rv['root']['x'].getXMLattributes(),
                         {'a': "val1"})
        self.assertRaises(KeyError, rv['root']['x'].delXMLattribute,
                          'b')
        self.assertEqual(rv['root']['x'].getXMLattributes(),
                         {'a': "val1"})
        rv['root']['x'].delXMLattribute('a')
        self.assertFalse(rv['root']['x'].hasXMLattributes())
        self.assertEqual(rv['root']['x'].getXMLattributes(), dict())

    def test_key_promotion_with_compress(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server1': {
                    'name': 'server1',
                    'os': 'os1',
                },
                'server2': {
                    'name': 'server2',
                    'os': 'os2',
                },
            }
        }
        parser = self.Parser(index_keys=('name',))
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_key_promotion_without_compress(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server':  {
                    'server1': {
                        'name': 'server1',
                        'os': 'os1',
                    },
                    'server2': {
                        'name': 'server2',
                        'os': 'os2',
                    },
                },
            }
        }
        parser = self.Parser(index_keys=('name',), index_keys_compress=False)
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_key_promotion_with_compress_with_force_cdata(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server1': {
                    'name': {'#text': 'server1'},
                    'os': {'#text': 'os1'},
                },
                'server2': {
                    'name': {'#text': 'server2'},
                    'os': {'#text': 'os2'},
                },
            }
        }
        parser = self.Parser(index_keys=('name',), force_cdata=True)
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_key_promotion_without_compress_with_force_cdata(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server':  {
                    'server1': {
                        'name': {'#text': 'server1'},
                        'os': {'#text': 'os1'},
                    },
                    'server2': {
                        'name': {'#text': 'server2'},
                        'os': {'#text': 'os2'},
                    },
                },
            }
        }
        parser = self.Parser(index_keys=('name',), index_keys_compress=False,
                        force_cdata=True)
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_key_promotion_mixed_with_compress(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <os>os2</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server1': {
                    'name': 'server1',
                    'os': 'os1',
                },
                'server': {
                    'os': 'os2',
                },
            }
        }
        parser = self.Parser(index_keys=('name',))
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_key_promotion_mixed_without_compress(self):
        test_xmls = ["""
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <os>os2</os>
          </server>
        </servers>
        """,
        """
        <servers>
          <server>
            <os>os1</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
        </servers>
        """,
        """
        <servers>
          <server>
            <os>os1</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
          <server>
            <os>os3</os>
          </server>
        </servers>
        """,
        """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <os>os2</os>
          </server>
          <server>
            <name>server3</name>
            <os>os3</os>
          </server>
        </servers>
        """,
        ]
        parser = self.Parser(index_keys=('name',), index_keys_compress=False)
        for xml in test_xmls:
            xml = self.xmlTextToTestFormat(xml)
            self.assertRaises(ValueError, parser, xml)
            self.assertRaises(ValueError, parser, xml, new_style=True)

    def test_key_promotion_list_with_compress(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <name>server1</name>
            <os>os2</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server1': [
                    {
                        'name': 'server1',
                        'os': 'os1',
                    },
                    {
                        'name': 'server1',
                        'os': 'os2',
                    },
                ],
                'server2': {
                    'name': 'server2',
                    'os': 'os2',
                },
            }
        }
        parser = self.Parser(index_keys=('name',))
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_key_promotion_list_without_compress(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
          <server>
            <name>server1</name>
            <os>os2</os>
          </server>
          <server>
            <name>server2</name>
            <os>os2</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server': {
                    'server1': [
                        {
                            'name': 'server1',
                            'os': 'os1',
                        },
                        {
                            'name': 'server1',
                            'os': 'os2',
                        },
                    ],
                    'server2': {
                        'name': 'server2',
                        'os': 'os2',
                    },
                },
            }
        }
        parser = self.Parser(index_keys=('name',), index_keys_compress=False)
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_force_list_basic(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
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
        parser = self.Parser(force_list=('server',))
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_force_list_with_index_key_compress(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server1': {
                    'name': 'server1',
                    'os': 'os1',
                },
            }
        }
        parser = self.Parser(force_list=('server',), index_keys=('name',))
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

    def test_force_list_without_index_key_compress(self):
        xml = """
        <servers>
          <server>
            <name>server1</name>
            <os>os1</os>
          </server>
        </servers>
        """
        xml = self.xmlTextToTestFormat(xml)
        expectedResult = {
            'servers': {
                'server': {
                    'server1': {
                        'name': 'server1',
                        'os': 'os1',
                    },
                },
            }
        }
        parser = self.Parser(force_list=('server',), index_keys=('name',),
                        index_keys_compress=False)
        self.assertEqual(parser(xml), expectedResult)
        self.assertEqual(parser(xml, new_style=True), expectedResult)

class EtreeToDictTestCase(XMLToDictTestCase):
    def __init__(self, *args, **kwargs):
        XMLToDictTestCase.__init__(self, *args, **kwargs)
        self.parse=parse_lxml
        self.Parser=LXMLParser

    def xmlTextToTestFormat(self, xml):
        try:
            return xmltodict.etree.fromstring(xml)
        except UnicodeEncodeError:
            xml = xml.encode('utf-8')
            return xmltodict.etree.fromstring(xml)

    @unittest.skip("Test does not make sense in the Etree context")
    def test_string_vs_file(self):
        pass

    def test_element_vs_element_tree(self):
        xml = '<a>data</a>'
        xml_element = xmltodict.etree.fromstring(xml)
        xml_elementtree = xmltodict.etree.ElementTree(xml_element)
        self.assertEqual(self.parse(xml_element),
                         self.parse(xml_elementtree))

class NewStyleClassTestCase(unittest.TestCase):
    def pprint_compare(self, obj1, obj2, **kwargs):
        ioObj1 = xmltodict.StringIO()
        obj1.prettyprint(width=1000, stream=ioObj1, **kwargs)
        ioObj2 = xmltodict.StringIO()
        xmltodict.pprint(obj2, width=1000, stream=ioObj2, **kwargs)
        self.assertEqual(ioObj1.getvalue(), ioObj2.getvalue())

    def test_newstyle_prettyprint(self):
        data1_orig = "data1"
        data1 = xmltodict.XMLCDATANode(data1_orig)
        data2_orig = "data2"
        data2 = xmltodict.XMLCDATANode(data2_orig)
        list1_orig = [data1_orig, data2_orig]
        list1 = xmltodict.XMLListNode((data1, data2))
        nodec = xmltodict.XMLDictNode({'c': list1})
        nodeb = xmltodict.XMLDictNode({'b': nodec})
        nodea = xmltodict.XMLDictNode({'a': nodeb})

        for depth in (None, 1, 2, 3, 4, 5):
            #dict level
            self.pprint_compare(nodea,
                                {'a': {'b': {'c': list1_orig}}},
                                depth=depth)

            # list level
            self.pprint_compare(list1, list1_orig, depth=depth)

            # CDATA level
            self.pprint_compare(data1, data1_orig, depth=depth)

        # Check non-XML*Node elements under an XML*Node element
        list1 = xmltodict.XMLListNode((data1, data2_orig))
        self.pprint_compare(list1, list1_orig)
        nodec['d'] = data2_orig
        self.pprint_compare(nodec,
                            {'c': list1_orig, 'd': data2_orig})
