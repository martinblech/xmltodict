#!/usr/bin/env python
"Makes working with XML feel like you are working with JSON"

import sys
from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from copy import deepcopy
try:  # pragma no cover
    from cStringIO import StringIO
except ImportError:  # pragma no cover
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
try: # pragma no cover
    from io import BytesIO
except ImportError: # pragma no cover
    BytesIO = StringIO
try:  # pragma no cover
    from collections import OrderedDict as _OrderedDict
except ImportError:  # pragma no cover
    try:
        from ordereddict import OrderedDict as _OrderedDict
    except ImportError:
        _OrderedDict = dict
try: # pragma no cover
    from pprint import pprint
except ImportError: # pragma no cover
    def pprint(obj, *args, **kwargs):
        if len(args) > 0:
            stream = args[0]
        else:
            stream = kwargs.get("stream", None)
        if stream is not None:
            stream.write("%r\n" % obj)
        else:
            print("%r" % obj)

QNameDecode = None
try: # pragma no cover
    from lxml import etree
    QNameDecode = etree.QName
except ImportError: # pragma no cover
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
            # Not tested; but, should be the same as cElementTree
        except ImportError:
            try:
                import cElementTree as etree
                print("Warning: Not tested with cElementTree")
            except ImportError:
                try:
                    import elementtree.ElementTree as etree
                    print("Warning: Not tested with elementtree.ElementTree")
                except ImportError:
                    print("Unable to import etree: lxml functionality disabled")

class QNameSeparator():
    def __init__(self, text):
        endidx = text.rfind('}')
        if text[0] != '{' or endidx < 0:
            self.namespace = None
            self.localname = text
        else:
            self.namespace = text[1:endidx]
            self.localname = text[endidx+1:]

if etree and QNameDecode == None: # pragma no cover
    class QNameDecode(QNameSeparator):
        def __init__(self, node):
            QNameSeparator.__init__(self, node.tag)

try:  # pragma no cover
    _basestring = basestring
except NameError:  # pragma no cover
    _basestring = str
try:  # pragma no cover
    _unicode = unicode
except NameError:  # pragma no cover
    _unicode = str
try:  # pragma no cover
    _bytes = bytes
except NameError:  # pragma no cover
    _bytes = str

# While doing processing for a generator, process XML text 1KB at a
# time.
parsingIncrement = 1024

__author__ = 'Martin Blech'
__version__ = '0.9.2'
__license__ = 'MIT'

class NoArg():
    pass

class OrderedDict(_OrderedDict):
    def __repr__(self, _repr_running={}):
        temp = self.__class__.__name__
        try:
            # The OrderedDict.__repr__ function takes an
            # extra argument. It also prints the name of
            # the main object's class. This logic temporarily
            # resets the class name so this appears to be
            # what it (fundamentally) is: an OrderedDict
            # object. (For this reason, there is also extra
            # logic to make the XMLDictNode __repr__ function
            # work correctly.)
            self.__class__.__name__ = _OrderedDict.__name__
            rv = _OrderedDict.__repr__(self, _repr_running)
        except:
            rv = _OrderedDict.__repr__(self)
        finally:
            self.__class__.__name__ = temp
        return rv

class _XMLNodeMetaClass(type):
    def __new__(cls, name, bases, dict):
        dict["XMLattrs"] = OrderedDict()
        dict["__parent__"] = bases[-1]
        return type.__new__(cls, name, bases, dict)
    def __call__(self, *args, **kwargs):
        XMLattrs=kwargs.pop("XMLattrs", OrderedDict())
        obj = type.__call__(self, *args, **kwargs)
        obj.XMLattrs = XMLattrs
        return obj


# The below is Python 2/3 Portable equivalent to
#   class XMLNodeMetaClass(object, metaclass=_XMLNodeMetaClass):
#       pass
if sys.version_info[0] >= 3:
    _temp_class_dict = {'__module__': _XMLNodeMetaClass.__module__,
                        '__qualname__': 'XMLNodeMetaClass'}
else:
    _temp_class_dict = {'__module__': _XMLNodeMetaClass.__module__,
                        '__metaclass__': _XMLNodeMetaClass}

XMLNodeMetaClass = _XMLNodeMetaClass(str("XMLNodeMetaClass"),
                                     (object,), _temp_class_dict)

del _temp_class_dict

class XMLNodeBase(XMLNodeMetaClass):
    def hasXMLattributes(self):
        if len(self.XMLattrs) > 0:
            return True
        return False

    def setXMLattribute(self, attr, val):
        self.XMLattrs[attr] = val

    def getXMLattribute(self, attr, defval=NoArg()):
        try:
            return self.XMLattrs[attr]
        except KeyError:
            if not isinstance(defval, NoArg):
                return defval
            raise

    def getXMLattributes(self):
        return self.XMLattrs

    def delXMLattribute(self, attr):
        del self.XMLattrs[attr]

    def __repr__(self):
        return "%s(XMLattrs=%r, value=%s)" % (getattr(self, "__const_class_name__", self.__class__.__name__), self.XMLattrs, self.__parent__.__repr__(self))


class XMLCDATANode(XMLNodeBase, _unicode):
    def strip(self, arg=None):
        newtext = _unicode.strip(self, arg)
        return XMLCDATANode(newtext, XMLattrs=self.XMLattrs)
    def prettyprint(self, *args, **kwargs):
        currdepth = kwargs.pop("currdepth", 0)
        newobj = self.__parent__(self)
        if currdepth==0:
            pprint(newobj, *args, **kwargs)
        else:
            return newobj

class XMLListNode(XMLNodeBase, list):
    def prettyprint(self, *args, **kwargs):
        currdepth = kwargs.pop("currdepth", 0)
        depth = kwargs.get("depth", None)
        if depth is not None and depth < currdepth:
            return {}
        # Construct a new item, recursively.
        newlist = list()
        for v in self:
            if hasattr(v, "prettyprint"):
                newlist.append(v.prettyprint(*args, currdepth=currdepth+1, **kwargs))
            else:
                newlist.append(v)
        if currdepth==0:
            pprint(newlist, *args, **kwargs)
        else:
            return newlist

class XMLDictNode(XMLNodeBase, OrderedDict):
    def __init__(self, *args, **kwargs):
        self.__const_class_name__ = self.__class__.__name__
        OrderedDict.__init__(self, *args, **kwargs)
    def prettyprint(self, *args, **kwargs):
        currdepth = kwargs.pop("currdepth", 0)
        depth = kwargs.get("depth", None)
        if depth is not None and depth < currdepth:
            return {}
        # Construct a new item, recursively.
        newdict = dict()
        for (k,v) in self.items():
            if hasattr(v, "prettyprint"):
                newdict[k] = v.prettyprint(*args, currdepth=currdepth+1, **kwargs)
            else:
                newdict[k] = v
        if currdepth==0:
            pprint(newdict, *args, **kwargs)
        else:
            return newdict

class ParsingInterrupted(Exception):
    pass

class _DictSAXHandler(object):
    def __init__(self,
                 item_depth=0,
                 item_callback=lambda *args: True,
                 xml_attribs=True,
                 attr_prefix=NoArg(),
                 cdata_key='#text',
                 force_cdata=False,
                 cdata_separator='',
                 postprocessor=None,
                 dict_constructor=NoArg(),
                 strip_whitespace=True,
                 namespace_separator=':',
                 namespaces=None,
                 tag_key='#tag',
                 index_keys=(),
                 index_keys_compress=True,
                 delete_key='#deletelevel',
                 force_list=(),
                 strip_namespace=False,
                 new_style=False):
        self.path = []
        self.stack = []
        self.data = None
        self.attrs = None
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.strip_whitespace = strip_whitespace
        self.namespace_separator = namespace_separator
        self.namespaces = namespaces
        self.tag_key = tag_key
        self.index_keys = index_keys
        self.index_keys_compress = index_keys_compress
        self.delete_key = delete_key
        self.force_list = force_list
        self.strip_namespace = strip_namespace
        self.new_style = new_style
        if self.new_style:
            self.list_constructor = XMLListNode
            self.cdata_constructor = XMLCDATANode
        else:
            self.list_constructor = list
            self.cdata_constructor = _unicode
        if isinstance(dict_constructor, NoArg):
            if self.new_style:
                self.dict_constructor = XMLDictNode
            else:
                self.dict_constructor = OrderedDict
        else:
            self.dict_constructor = dict_constructor
        if isinstance(attr_prefix, NoArg):
            if self.new_style:
                self.attr_prefix=""
            else:
                self.attr_prefix="@"
        else:
            self.attr_prefix = attr_prefix

    def _build_name(self, full_name):
        if (not self.namespaces) and (not self.strip_namespace):
            return full_name
        i = full_name.rfind(self.namespace_separator)
        if i == -1:
            return full_name
        namespace, name = full_name[:i], full_name[i+1:]
        if self.strip_namespace:
            return name
        short_namespace = self.namespaces.get(namespace, namespace)
        if not short_namespace:
            return name
        else:
            return self.namespace_separator.join((short_namespace, name))

    def _attrs_to_dict(self, attrs):
        if isinstance(attrs, dict):
            rv = attrs
        else:
            rv = self.dict_constructor(zip(attrs[0::2], attrs[1::2]))
        if self.strip_namespace:
            for k in list(rv.keys()):
                if k == "xmlns" or k.startswith("xmlns" + self.namespace_separator):
                    del rv[k]
            for k in list(rv.keys()):
                if k.rfind(":") >= 0:
                    newkey = k[k.rfind(self.namespace_separator) + 1:]
                    if newkey in rv:
                        raise ValueError("Stripping namespace causes duplicate attribute \"%s\"" % newkey)
                    rv[newkey] = rv[k]
                    del rv[k]
        return rv

    def startElement(self, full_name, attrs):
        name = self._build_name(full_name)
        attrs = self._attrs_to_dict(attrs)
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            if self.new_style:
                self.stack.append((self.item, self.attrs, self.data))
            else:
                self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attrs = self.dict_constructor(
                    (self.attr_prefix+self._build_name(key), value)
                    for (key, value) in attrs.items())
            else:
                attrs = None
            if self.new_style:
                self.attrs = attrs
                self.item = None
            else:
                self.item = attrs or None
            self.data = None

    def endElement(self, full_name):
        name = self._build_name(full_name)
        if self.strip_whitespace and self.data is not None:
            self.data = self.data.strip() or None
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = self.data
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            if self.new_style:
                item, attrs, data = self.item, self.attrs, self.data
                self.item, self.attrs, self.data = self.stack.pop()
            else:
                item, data = self.item, self.data
                self.item, self.data = self.stack.pop()
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if self.new_style and isinstance(attrs, dict):
                if item is not None:
                    node = item
                elif data is not None:
                    node = data
                elif len(attrs) > 0:
                    node = data = self.cdata_constructor()
                else:
                    node = None
                if node is not None:
                    for (key, value) in attrs.items():
                        node.setXMLattribute(key, value)
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = self.attrs = self.data = None
        self.path.pop()

    def characters(self, data):
        if not self.data:
            self.data = self.cdata_constructor(data)
        else:
            self.data = self.cdata_constructor(self.data + self.cdata_separator + data)

    def _promote_keys(self, key, value):
        if isinstance(value, dict):
            for i in self.index_keys:
                if i in value:
                    if self.index_keys_compress:
                        setattr(value, self.tag_key, key)
                    if isinstance(value[i], dict) and self.cdata_key in value[i]:
                        return (_unicode(value[i][self.cdata_key]), value)
                    return (_unicode(value[i]), value)
        return None

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        result = self._promote_keys(key, data)
        if self.index_keys_compress and result is not None:
            key, data = result
        if item is None:
            item = self.dict_constructor()
        if self.index_keys_compress or result is None:
            try:
                value = item[key]
                if isinstance(value, list):
                    value.append(data)
                elif isinstance(value, dict) and (not self.index_keys_compress) and getattr(value, self.delete_key, False):
                    raise ValueError("Mixture of data types: some have index keys and some do not, while processing \"%s\" key" % key)
                else:
                    item[key] = self.list_constructor((value, data))
            except KeyError:
                if key in self.force_list:
                    item[key] = self.list_constructor((data,))
                else:
                    item[key] = data
        else:
            try:
                value = item[key]
                if isinstance(value, dict) and getattr(value, self.delete_key, False):
                    if result[0] in value:
                        value[result[0]] = self.list_constructor((value[result[0]], result[1]))
                    else:
                        value[result[0]] = result[1]
                else:
                    raise ValueError("Mixture of data types: some have index keys and some do not, while processing \"%s\" key" % key)
            except KeyError:
                item[key] = self.dict_constructor()
                item[key][result[0]] = result[1]
                setattr(item[key], self.delete_key, True)
        return item

class Parser(object):
    def __init__(self, **kwargs):
        # Save the arguments for later.
        self.kwargs=dict(kwargs)

        # For now, pop off the arguments that we don't want to pass to
        # the handler class.
        encoding=kwargs.pop('encoding', None)
        my_expat=kwargs.pop('expat', expat)
        process_namespaces=kwargs.pop('process_namespaces', False)
        namespace_separator=kwargs.pop('namespace_separator', ':')
        generator=kwargs.pop('generator', False)

        # Try the arguments to catch argument errors now. We will toss
        # out the created handler and parser, anyway.
        handler = _DictSAXHandler(namespace_separator=namespace_separator,
                                  **kwargs)
        if not encoding:
            encoding = 'utf-8'
        if not process_namespaces:
            namespace_separator = None
        parser = my_expat.ParserCreate(
            encoding,
            namespace_separator
        )
        del handler
        del parser
    def __call__(self, xml_input, **kwargs):
        # NOTE: For now, this just calls the external parse()
        # method. I would prefer to rewrite this so the external
        # parse() method just calls this class (similar to the
        # relationship between the parse_lxml() method and the
        # LXMLParser class). However, I am writing this class in this
        # way to make the diffs easier to read.
        newkwargs = dict(self.kwargs)
        newkwargs.update(kwargs)
        return parse(xml_input, **newkwargs)

class _GeneratorCallback(object):
    def __init__(self, item_callback=None):
        if item_callback == None:
            item_callback = lambda *args: True
        self.item_callback = item_callback
        self.stack = []
    def get_items(self):
        done = False
        while not done:
            try:
                yield self.stack.pop(0)
            except IndexError:
                done=True
    def add_item(self, stack, value):
        rv = self.item_callback(stack, value)
        self.stack.append((deepcopy(stack), value))
        return rv

def _parse_generator(xml_input, parser, cb):
    if isinstance(xml_input, str) or isinstance(xml_input, _unicode):
        ioObj = StringIO(xml_input)
    elif isinstance(xml_input, _bytes):
        ioObj = BytesIO(xml_input)
    else:
        ioObj = xml_input

    atEof=False
    while not atEof:
        buf = ioObj.read(parsingIncrement)
        if len(buf) == 0:
            atEof=True
        parser.Parse(buf, atEof)
        for rv in cb.get_items():
            yield rv

def parse(xml_input, encoding=None, expat=expat,
          process_namespaces=False, namespace_separator=':',
          generator=False, **kwargs):
    """Parse the given XML input and convert it into a dictionary.

    `xml_input` can either be a `string` or a file-like object.

    If `xml_attribs` is `True`, element attributes are put in the dictionary
    among regular child elements, using `@` as a prefix to avoid collisions. If
    set to `False`, they are just ignored.

    Simple example::

        >>> import xmltodict
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

    This also supports "streaming mode", where intermediate values are
    returned during parsing. There are two versions of "streaming
    mode": one which uses a callback functon and one which returns an
    iterator. (The two modes can actually be combined, as well.)

    If `generator` evaluates to True, the function returns an
    iterator. On each iteration, it returns a new node from the
    specified `item_depth`. (An `item_depth` of 0 will return the full
    tree, an `item_depth` of 1 will return the contents of the root
    tag, an `item_depth` of 2 will return the contents of the tags of
    the root element's children, etc.) Each iteration returns a tuple
    of the `path` from the document root to the item (name-attribs
    pairs) and the `item` (the contents of the item). The contents of
    the item will be the value of that sub-node. If it would be a
    dictionary, it returns a dictionary. If it would be a text node,
    it returns a text node. If it would be None (empty tag), it
    returns None.

    If `item_depth` is non-0 and the user specifies an
    `item_callback`, it will call the `item_callback` every time an
    item at the specified depth is found.

    If `item_depth` is non-0 and `generator` evaluates to False, the
    function will not return a dictionary for the root element (which
    is the default behavior). Instead, it will call the
    `item_callback` every time an item at the specified depth is found
    and will return `None` in the end (streaming mode).

    The `item_callback` function receives the same parameters returned
    by the `generator`: the `path` from the document root to the item
    (name-attribs pairs), and the `item` (dict). If the callback's
    return value is false-ish, parsing will be stopped with the
    :class:`ParsingInterrupted` exception.

    Generator/Iterator example:
        >>> xml = \"\"\"\\
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>\"\"\"
        >>> for (path, item) in xmltodict.parse(xml, generator=True, item_depth=2):
        ...     print 'path:%s item:%s' % (path, item)
        ... 
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:1
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:2

    Callback example::

        >>> def handle(path, item):
        ...     print 'path:%s item:%s' % (path, item)
        ...     return True
        ...
        >>> xml = \"\"\"\\
        ... <a prop="x">
        ...   <b>1</b>
        ...   <b>2</b>
        ... </a>\"\"\"
        >>> xmltodict.parse(xml, item_depth=2, item_callback=handle)
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:1
        path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:2

    The optional argument `postprocessor` is a function that takes `path`,
    `key` and `value` as positional arguments and returns a new `(key, value)`
    pair where both `key` and `value` may have changed. Usage example::

        >>> def postprocessor(path, key, value):
        ...     try:
        ...         return key + ':int', int(value)
        ...     except (ValueError, TypeError):
        ...         return key, value
        >>> xmltodict.parse('<a><b>1</b><b>2</b><b>x</b></a>',
        ...                 postprocessor=postprocessor)
        OrderedDict([(u'a', OrderedDict([(u'b:int', [1, 2]), (u'b', u'x')]))])

    You can pass an alternate version of `expat` (such as `defusedexpat`) by
    using the `expat` parameter. E.g:

        >>> import defusedexpat
        >>> xmltodict.parse('<a>hello</a>', expat=defusedexpat.pyexpat)
        OrderedDict([(u'a', u'hello')])

    You can use the `index_keys` argument to pass an ordered tuple
    or list of indices. If a subtree contains a child element with a tag
    that matches one of the items in the `index_keys` argument, the function
    will make the value of that element be the key for the subtree.
    This process occurs after any user-supplied postprocessor. The items
    in `index_keys` are examined in order. The first matching item will be
    used as the index.

        For example, given this input:
        <servers>
          <server>
            <name>host1</name>
            <ip_address>10.0.0.1</ip_address>
            <os>Linux</os>
          </server>
          <server>
            <name>host2</name>
            <ip_address>10.0.0.2</ip_address>
            <os>OSX</os>
          </server>
        </servers>

        If called with index_keys=('name',), it will produce
        this dictionary:
        {'servers':
          {'host1':
            {'name': 'host1',
             'ip_address': '10.0.0.1',
             'os': 'Linux'},
           'host2':
            {'name': 'host2',
             'ip_address': '10.0.0.2',
             'os': 'OSX'} } }

    You can use the `index_keys_compress` argument to modify the way the
    `index_keys` argument processing works. If you specify
    `index_keys_compress=False`, the original key will remain in
    place. However, instead of the original key pointing to a list, it
    will point to a dictionary keyed off of the value of the element
    that matches an entry in `index_key`.

        For example, given the XML document from the previous example,
        if called with `index_keys=('name',)` and
        `index_keys_compress=False`, it will produce this dictionary:
        {'servers':
          {'server':
            {'host1':
              {'name': 'host1',
               'ip_address': '10.0.0.1',
               'os': 'Linux'},
             'host2':
              {'name': 'host2',
               'ip_address': '10.0.0.2',
               'os': 'OSX'} } } }

    You can use the `force_list` argument to force lists to be created even
    when there is only a single child of a given level of hierarchy. The
    `force_list` argument is a tuple of keys. If the key for a given level
    of hierarchy is in the `force_list` argument, that level of hierarchy
    will have a list as a child (even if there is only one sub-element).
    The `index_keys` operation takes precendence over this. This is applied
    after any user-supplied postprocessor has already run.

        For example, given this input:
        <servers>
          <server>
            <name>host1</name>
            <os>Linux</os>
            <interfaces>
              <interface>
                <name>em0</name>
                <ip_address>10.0.0.1</ip_address>
              </interface>
            </interfaces>
          </server>
        </servers>

        If called with `force_list=('interface',)`, it will produce
        this dictionary:
        {'servers':
          {'server':
            {'name': 'host1',
             'os': 'Linux'},
             'interfaces':
              {'interface':
                [ {'name': 'em0', 'ip_address': '10.0.0.1' } ] } } }

    You can use the `new_style` argument to cause the function to
    return output that uses classes based on the XMLNodeMetaClass. The
    main functional difference is that the XML attributes are placed
    in a class attribute, rather than being placed in a dictionary
    entry. The XML attributes are accessible/settable using these
    functions:
        obj.hasXMLattributes(): Returns True if there are XML
          attributes, or False otherwise.
        obj.setXMLattribute(attr, val): Sets the XML attribute of name
         `attr` to `val`.
        obj.getXMLattribute(attr[, default]): Gets the XML attribute
          of name `attr`. If there is no such attribute, it will
          return default (if supplied) or raise a KeyError.
        obj.delXMLattribute(attr, val): Deletes the XML attribute of name
         `attr`.

    The classes returned when the `new_style` argument is True also
    have a `prettyprint` method, which is mostly a pass-through to the
    pprint() function. The main difference is that it strips the
    attributes and converts the contents into simple types (such as
    list and dict) so pprint will function as expected.

    You can use the `strip_namespace` parameter to strip XML namespace
    information from the returned dictionary. If the `strip_namespace`
    parameter is set to True, the parser will remove the namespace
    prefix (if any) from the element name and will remove the xmlns
    attributes from the nodes.

    """
    if generator and kwargs.get('item_depth', 0) > 0:
        cb = _GeneratorCallback(kwargs.get('item_callback', None))
        kwargs['item_callback'] = cb.add_item

    handler = _DictSAXHandler(namespace_separator=namespace_separator,
                              **kwargs)
    if isinstance(xml_input, _unicode):
        if not encoding:
            encoding = 'utf-8'
        xml_input = xml_input.encode(encoding)
    if not process_namespaces:
        namespace_separator = None
    parser = expat.ParserCreate(
        encoding,
        namespace_separator
    )
    try:
        parser.ordered_attributes = True
    except AttributeError:
        # Jython's expat does not support ordered_attributes
        pass
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    parser.buffer_text = True
    if generator and kwargs.get('item_depth', 0) > 0:
        return _parse_generator(xml_input=xml_input, parser=parser,
                                cb=cb)
    else:
        try:
            parser.ParseFile(xml_input)
        except (TypeError, AttributeError):
            parser.Parse(xml_input, True)
    if generator:
        return [([], handler.item)]
    else:
        return handler.item

if etree:
    class NamespaceError(ValueError):
        def __init__(self, namespace):
            self.namespace = namespace
        def __str__(self):
            return "Namespace \"%s\" not found in namespace store." % self.namespace
        def __repr__(self):
            return "%s(namespace=%s)" % (self.__class__.__name__,
                                         self.namespace)

    def parse_attrib(in_dict, out_dict, ns_dict, namespace_separator):
        for (k,v) in list(in_dict.items()):
            parsed_attr = QNameSeparator(k)
            if not parsed_attr.namespace:
                out_dict[k] = v
                del in_dict[k]
            else:
                try:
                    new_ns = ns_dict[parsed_attr.namespace]
                except KeyError:
                    raise NamespaceError(parsed_attr.namespace)
                new_k = namespace_separator.join(
                    (new_ns,
                     parsed_attr.localname)
                )
                out_dict[new_k] = v
                del in_dict[k]

    def parse_lxml_node(node, handler, process_namespaces,
                        strip_namespace, namespace_separator, cb,
                        namespace_dict=None, rootElement=False):
        # Parsing LXML/ElementTree is actually quite simple. We
        # can just recursively call this function to walk through
        # the tree of elements and call the same handler we use
        # for parsing the text version through a SAX parser.
        # Almost all of the complexity is handling the namespaces.

        # Initialize the namespace_dict, if needed.
        if namespace_dict == None:
            namespace_dict = {'nexttag': _unicode('ns0')}

        # Ignore processing instructions and comments.
        if node.tag not in (etree.PI, etree.Comment):
            # Figure out NS:
            # If 'strip_namespace' or 'process_namespaces' are set, we
            # can do the same thing. In these cases, we just care about
            # making sure the attributes and tags are formed correctly so
            # that the handler will do the correct thing. In general, our
            # goal is to emulate what the expat processor would do if
            # process_namespaces was set to True.
            #
            # Otherwise, try to restore the original nodename ("ns:tag")
            # and XMLNS attributes. (Again, this emulates what the expat
            # processor would do.) If we've lost the original
            # namespace identifiers, make up our own.
            if strip_namespace or process_namespaces:
                parsed_tag = QNameDecode(node)
                if not parsed_tag.namespace:
                    tag = parsed_tag.localname
                else:
                    tag = namespace_separator.join((parsed_tag.namespace,
                                                    parsed_tag.localname))

                # Fix the attributes. Just paste them together with
                # the namespace separator. The standard parsing code
                # can handle them further. (In the case where
                # strip_namespace is set, it can check for name
                # conflicts (e.g.  <a a:attr1="" b:attr1=""
                # c:attr1=""/>). That is the reason we don't strip
                # them out here when strip_namespace is true. It seems
                # best to have the logic in a single place.
                attrib = dict()
                for (k,v) in node.attrib.items():
                    parsed_attr = QNameSeparator(k)
                    if not parsed_attr.namespace:
                        attrib[k] = v
                    else:
                        new_k = namespace_separator.join(
                            (parsed_attr.namespace,
                             parsed_attr.localname)
                        )
                        attrib[new_k] = v

            elif hasattr(node, 'nsmap') and len(node.nsmap) == 0:
                # If nsmap is present (lxml) and it is 0, then we
                # should have no namespace information to process.
                # If nsmap is present and it is greater than 0,
                # then we want to process the namespace information,
                # even if all we do is create proper xmlns attributes.
                tag = node.tag
                attrib = dict(node.attrib)
            else:
                # If the node has the nsmap attribute, reverse it to
                # create a namespace lookup dictionary for us.
                if hasattr(node, 'nsmap'):
                    ns_resolve_dict = dict(zip(node.nsmap.values(),
                                               node.nsmap.keys()))
                # If the node doesn't have the nsmap attribute, all NS
                # identfiers are lost. We can recreate them with
                # locally-generated identifiers, which we store in the
                # namespace_dict.
                else:
                    ns_resolve_dict = namespace_dict

                # Initialize the new attributes
                attrib = dict()

                # Determine if we need to add a namespace to the tag.
                parsed_tag = QNameDecode(node)
                if (not parsed_tag.namespace) or (not ns_resolve_dict.get(parsed_tag.namespace, '@@NOMATCH@@')):
                    tag = parsed_tag.localname
                else:
                    # If the namespace isn't in our resolver dictionary,
                    # add it to the namespace_dict. Note that this
                    # will not work correctly if the node had an nsmap.
                    # It isn't supposed to work correctly in that case.
                    # If the tag uses a namespace that isn't in the
                    # nsmap, that seems like a bug.
                    if parsed_tag.namespace not in ns_resolve_dict:
                        newns = namespace_dict['nexttag']
                        namespace_dict[parsed_tag.namespace] = newns
                        namespace_dict['nexttag'] = _unicode("ns%d" % (int(newns[2:]) + 1, ))
                        attrib[_unicode("xmlns:" + newns)] = parsed_tag.namespace
                    tag = namespace_separator.join((ns_resolve_dict[parsed_tag.namespace],
                                                    parsed_tag.localname))

                # Deal with the attributes.
                old_attrib = dict(node.attrib)
                while len(old_attrib) > 0:
                    try:
                        parse_attrib(old_attrib, attrib, ns_resolve_dict,
                                     namespace_separator)
                    except NamespaceError:
                        # NOTE: "except NamespaceError as e" is not
                        # supported in older Python versions. Once
                        # support for those versions is deprecated, we
                        # should consider changing this to the more
                        # standard syntax.
                        e = sys.exc_info()[1]
                        if hasattr(node, 'nsmap'):
                            raise
                        newns = namespace_dict['nexttag']
                        namespace_dict[e.namespace] = newns
                        namespace_dict['nexttag'] = _unicode(
                            "ns%d" % (int(newns[2:]) + 1, )
                        )
                        attrib[_unicode("xmlns:" + newns)] = e.namespace

                # Add any necessary xmlns tags.
                if hasattr(node, "nsmap"):
                    if rootElement:
                        parent_nsmap = {}
                    else:
                        parent_nsmap = node.getparent().nsmap
                    for (k,v) in node.nsmap.items():
                        if parent_nsmap.get(k, '@@NOMATCH@@') != v:
                            if k:
                                attrib[_unicode("xmlns:" + k)] = v
                            else:
                                attrib[_unicode("xmlns")] = v

            handler.startElement(tag, attrib)
            if node.text and len(node.text) > 0:
                handler.characters(node.text)
            for child in node:
                child_iterator = parse_lxml_node(
                    child, handler, process_namespaces, strip_namespace,
                    namespace_separator, cb, namespace_dict
                )
                for rv in child_iterator:
                    yield rv
                for rv in cb.get_items():
                    yield rv
            handler.endElement(tag)
        if (not rootElement) and node.tail and len(node.tail) > 0:
            handler.characters(node.tail)

    class LXMLParser(object):
        def __init__(self, process_namespaces=False,
                     namespace_separator=':', allow_extra_args=False,
                     generator=False, **kwargs):
            self.process_namespaces = process_namespaces
            self.namespace_separator = namespace_separator
            self.allow_extra_args = allow_extra_args
            self.generator = generator
            self.kwargs = kwargs
            self.strip_namespace = kwargs.get('strip_namespace',False)
            handler = _DictSAXHandler(namespace_separator=self.namespace_separator,
                                      **kwargs)
            del handler
        def __call__(self, lxml_root, *args, **kwargs):
            if len(args) > 0 and not self.allow_extra_args:
                raise TypeError("%s callable takes 1 argument (%d given)" %
                                (self.__class__.__name__, len(args)))
            generator = kwargs.pop('generator', self.generator)
            newkwargs = dict(self.kwargs)
            newkwargs.update(kwargs)

            cb = _GeneratorCallback(newkwargs.get('item_callback', None))
            if generator and newkwargs.get('item_depth', 0) > 0:
                newkwargs['item_callback'] = cb.add_item

            handler = _DictSAXHandler(
                namespace_separator=self.namespace_separator,
                **newkwargs
            )
            try:
                if isinstance(lxml_root, etree._ElementTree):
                    lxml_root = lxml_root.getroot()
            except:
                try:
                    if isinstance(lxml_root, etree.ElementTree):
                        lxml_root = lxml_root.getroot()
                except:
                    if not hasattr(lxml_root, 'tag'):
                        lxml_root = lxml_root.getroot()
            childIter = parse_lxml_node(lxml_root, handler,
                                        self.process_namespaces,
                                        self.strip_namespace,
                                        self.namespace_separator,
                                        cb, rootElement=True)
            if generator and newkwargs.get('item_depth', 0) > 0:
                return childIter
            else:
                for i in childIter:
                    pass
                if generator:
                    return [([], handler.item)]
                else:
                    return handler.item
                            
    def parse_lxml(lxml_root, *args, **kwargs):
        return LXMLParser(*args, **kwargs)(lxml_root)

def _emit(key, value, content_handler,
          attr_prefix='@',
          cdata_key='#text',
          depth=0,
          preprocessor=None,
          pretty=False,
          newl='\n',
          indent='\t',
          full_document=True,
          tag_key='#tag',
          delete_key='#deletelevel'):
    if isinstance(value, dict):
        # Support tag_key and delete_key both as "normal" dictionary
        # entries and as hidden attributes. Prefer the "normal"
        # dictionary entries (if present) over the attributes.
        if tag_key in value:
            key = value.pop(tag_key)
        elif hasattr(value, tag_key):
            key = getattr(value, tag_key)
        delete_level=False
        if delete_key in value:
            delete_level=value.pop(delete_key)
        if delete_level or getattr(value, delete_key, False):
            newvalue=[]
            for sub_hierachy in value.keys():
                if isinstance(value[sub_hierachy], list):
                    newvalue.extend(value[sub_hierachy])
                else:
                    newvalue.append(value[sub_hierachy])
            value = newvalue
    if preprocessor is not None:
        result = preprocessor(key, value)
        if result is None:
            return
        key, value = result
    if (not hasattr(value, '__iter__')
            or isinstance(value, _basestring)
            or isinstance(value, dict)):
        value = [value]
    for index, v in enumerate(value):
        if full_document and depth == 0 and index > 0:
            raise ValueError('document with multiple roots')
        attrs = getattr(v, "XMLattrs", OrderedDict())
        if v is None:
            v = OrderedDict()
        elif not isinstance(v, dict):
            v = _unicode(v)
        if isinstance(v, _basestring):
            v = OrderedDict(((cdata_key, v),))
        cdata = None
        children = []
        for ik, iv in v.items():
            if ik == cdata_key:
                cdata = iv
                continue
            if ik.startswith(attr_prefix):
                attrs[ik[len(attr_prefix):]] = iv
                continue
            children.append((ik, iv))
        if pretty:
            content_handler.ignorableWhitespace(depth * indent)
        content_handler.startElement(key, AttributesImpl(attrs))
        if pretty and children:
            content_handler.ignorableWhitespace(newl)
        for child_key, child_value in children:
            _emit(child_key, child_value, content_handler,
                  attr_prefix, cdata_key, depth+1, preprocessor,
                  pretty, newl, indent)
        if cdata is not None:
            content_handler.characters(cdata)
        if pretty and children:
            content_handler.ignorableWhitespace(depth * indent)
        content_handler.endElement(key)
        if pretty and depth:
            content_handler.ignorableWhitespace(newl)


def unparse(input_dict, output=None, encoding='utf-8', full_document=True,
            **kwargs):
    """Emit an XML document for the given `input_dict` (reverse of `parse`).

    The resulting XML document is returned as a string, but if `output` (a
    file-like object) is specified, it is written there instead.

    Dictionary keys prefixed with `attr_prefix` (default=`'@'`) are interpreted
    as XML node attributes, whereas keys equal to `cdata_key`
    (default=`'#text'`) are treated as character data.

    The `pretty` parameter (default=`False`) enables pretty-printing. In this
    mode, lines are terminated with `'\n'` and indented with `'\t'`, but this
    can be customized with the `newl` and `indent` parameters.

    """
    if full_document and len(input_dict) != 1:
        raise ValueError('Document must have exactly one root.')
    must_return = False
    if output is None:
        output = StringIO()
        must_return = True
    content_handler = XMLGenerator(output, encoding)
    if full_document:
        content_handler.startDocument()
    for key, value in input_dict.items():
        _emit(key, value, content_handler, full_document=full_document,
              **kwargs)
    if full_document:
        content_handler.endDocument()
    if must_return:
        value = output.getvalue()
        try:  # pragma no cover
            value = value.decode(encoding)
        except AttributeError:  # pragma no cover
            pass
        return value

if __name__ == '__main__':  # pragma: no cover
    import sys
    import marshal

    (item_depth,) = sys.argv[1:]
    item_depth = int(item_depth)

    def handle_item(path, item):
        marshal.dump((path, item), sys.stdout)
        return True

    try:
        root = parse(sys.stdin,
                     item_depth=item_depth,
                     item_callback=handle_item,
                     dict_constructor=dict)
        if item_depth == 0:
            handle_item([], root)
    except KeyboardInterrupt:
        pass
