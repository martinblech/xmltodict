#!/usr/bin/env python
import xml.parsers.expat

__author__ = 'Martin Blech'
__version__ = '0.1.dev'
__license__ = 'MIT'

class ParsingInterrupted(Exception): pass

class DictSAXHandler:
    def __init__(self,
            item_depth=0,
            xml_attribs=True,
            item_callback=lambda *args: True,
            attr_prefix='@',
            cdata_key='#text',
            force_cdata=False):
        self.path = []
        self.stack = []
        self.data = None
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix;
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata

    def startElement(self, name, attrs):
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            attrs = dict((self.attr_prefix+key, value)
                    for (key, value) in attrs.items())
            self.item = self.xml_attribs and attrs or None
            self.data = None
    
    def endElement(self, name):
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = self.data
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            item, data = self.item, self.data
            self.item, self.data = self.stack.pop()
            if self.force_cdata and item is None:
                item = {}
            if item is not None:
                if data:
                    item[self.cdata_key] = data
                self.push_data(name, item)
            else:
                self.push_data(name, data)
        else:
            self.item = self.data = None
        self.path.pop()

    def characters(self, data):
        if data.strip():
            if not self.data:
                self.data = data
            else:
                self.data += data

    def push_data(self, key, data):
        if self.item is None:
            self.item = {}
        try:
            value = self.item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                self.item[key] = [value, data]
        except KeyError:
            self.item[key] = data

def parse(xml_input, *args, **kwargs):
    """Parse the given XML input and convert it into a dictionary.

    `xml_input` can either be a `string` or a file-like object.

    If `xml_attribs` is `True`, element attributes are put in the dictionary
    among regular child elements, using `@` as a prefix to avoid collisions. If
    set to `False`, they are just ignored.

    Simple example::

        >>> doc = xmltodict.parse(\"\"\"
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>
        ... \"\"\")
        >>> doc['a']['@prop']
        u'x'
        >>> doc['a']['b']
        [u'1', u'2']

    If `item_depth` is `0`, the function returns a dictionary for the root
    element (default behavior). Otherwise, it calls `item_callback` every time
    an item at the specified depth is found and returns `None` in the end
    (streaming mode).

    The callback function receives two parameters: the `path` from the document
    root to the item (name-attribs pairs), and the `item` (dict). If the
    callback's return value is false-ish, parsing will be stopped with the
    :class:`ParsingInterrupted` exception.

    Streaming example::

        >>> def handle(path, item):
        ...     print 'path:%s item:%s' % (path, item)
        ...     return True
        ... 
        >>> xmltodict.parse(\"\"\"
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>\"\"\", item_depth=2, item_callback=handle)
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:1
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:2

    """
    handler = DictSAXHandler(*args, **kwargs)
    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    if hasattr(xml_input, 'read'):
        parser.ParseFile(xml_input)
    else:
        parser.Parse(xml_input, True)
    return handler.item

if __name__ == '__main__':
    import sys
    import marshal

    (item_depth,) = sys.argv[1:]
    item_depth = int(item_depth)

    def handle_item(item_type, item):
        marshal.dump((item_type, item), sys.stdout)
        return True

    try:
        root = parse(sys.stdin,
                item_depth=item_depth,
                item_callback=handle_item)
        if item_depth == 0:
            handle_item([], root)
    except KeyboardInterrupt:
        pass
    except IOError, e:
        print e
