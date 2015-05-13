#!/usr/bin/env python
"Makes working with XML feel like you are working with JSON"

from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
try:  # pragma no cover
    from cStringIO import StringIO
except ImportError:  # pragma no cover
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
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
        print(obj)

try:  # pragma no cover
    _basestring = basestring
except NameError:  # pragma no cover
    _basestring = str
try:  # pragma no cover
    _unicode = unicode
except NameError:  # pragma no cover
    _unicode = str

__author__ = 'Martin Blech'
__version__ = '0.9.2'
__license__ = 'MIT'

class NoArg():
    pass

# Methods that will be added by the XMLNodeMetaClass
_XMLNodeMetaClassImports = []

def hasXMLattributes(self):
    if len(self.XMLattrs) > 0:
        return True
    return False

_XMLNodeMetaClassImports.append(hasXMLattributes)

def setXMLattribute(self, attr, val):
    self.XMLattrs[attr] = val

_XMLNodeMetaClassImports.append(setXMLattribute)

def getXMLattribute(self, attr, defval=NoArg()):
    try:
        return self.XMLattrs[attr]
    except KeyError:
        if not isinstance(defval, NoArg):
            return defval
        raise

_XMLNodeMetaClassImports.append(getXMLattribute)

def delXMLattribute(self, attr):
    del self.XMLattrs[attr]

_XMLNodeMetaClassImports.append(delXMLattribute)

def _XMLNodeMetaClassRepr(self):
    return "%s(XMLattrs=%r, value=%s)" % (getattr(self, "__const_class_name__", self.__class__.__name__), self.XMLattrs, self.__parent__.__repr__(self))

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

class XMLNodeMetaClass(type):
    def __new__(cls, name, bases, dict):
        dict["XMLattrs"] = OrderedDict()
        dict["__parent__"] = bases[0]
        dict["__repr__"] = _XMLNodeMetaClassRepr
        for method in _XMLNodeMetaClassImports:
            dict[method.__name__] = method
        return type.__new__(cls, name, bases, dict)
    def __call__(self, *args, **kwargs):
        XMLattrs=kwargs.pop("XMLattrs", OrderedDict())
        obj = type.__call__(self, *args, **kwargs)
        obj.XMLattrs = XMLattrs
        return obj

class XMLCDATANode(_unicode):
    __metaclass__ = XMLNodeMetaClass
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

class XMLListNode(list):
    __metaclass__ = XMLNodeMetaClass
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

class XMLDictNode(OrderedDict):
    __metaclass__ = XMLNodeMetaClass
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
        for (k,v) in self.iteritems():
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
        if not self.namespaces:
            return full_name
        i = full_name.rfind(self.namespace_separator)
        if i == -1:
            return full_name
        namespace, name = full_name[:i], full_name[i+1:]
        short_namespace = self.namespaces.get(namespace, namespace)
        if not short_namespace:
            return name
        else:
            return self.namespace_separator.join((short_namespace, name))

    def _attrs_to_dict(self, attrs):
        if isinstance(attrs, dict):
            return attrs
        return self.dict_constructor(zip(attrs[0::2], attrs[1::2]))

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
            if self.strip_whitespace and data is not None:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if self.new_style and isinstance(attrs, dict):
                if item is not None:
                    node = item
                elif data is not None:
                    node = data
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
                if value.has_key(i):
                    if self.index_keys_compress:
                        setattr(value, self.tag_key, key)
                    if isinstance(value[i], dict) and value[i].has_key(self.cdata_key):
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
        if self.index_keys_compress and not result is None:
            key, data = result
        if item is None:
            item = self.dict_constructor()
        if self.index_keys_compress or result is None:
            try:
                value = item[key]
                if isinstance(value, list):
                    value.append(data)
                if isinstance(value, dict) and (not self.index_keys_compress) and getattr(value, self.delete_key, False):
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
                    if value.has_key(result[0]):
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


def parse(xml_input, encoding=None, expat=expat, process_namespaces=False,
          namespace_separator=':', **kwargs):
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
    """
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
    try:
        parser.ParseFile(xml_input)
    except (TypeError, AttributeError):
        parser.Parse(xml_input, True)
    return handler.item


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
        if value.has_key(tag_key):
            key = value.pop(tag_key)
        elif hasattr(value, tag_key):
            key = getattr(value, tag_key)
        delete_level=False
        if value.has_key(delete_key):
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
        if v is None:
            v = OrderedDict()
        elif not isinstance(v, dict):
            v = _unicode(v)
        if isinstance(v, _basestring):
            v = OrderedDict(((cdata_key, v),))
        cdata = None
        attrs = getattr(v, "XMLattrs", OrderedDict())
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
