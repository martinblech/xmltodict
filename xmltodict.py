#!/usr/bin/env python
"Makes working with XML feel like you are working with JSON"

try:
    from defusedexpat import pyexpat as expat
except ImportError:
    from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator, quoteattr
from xml.sax.xmlreader import AttributesImpl
try:  # pragma no cover
    from cStringIO import StringIO
except ImportError:  # pragma no cover
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
try:  # pragma no cover
    from collections import OrderedDict
except ImportError:  # pragma no cover
    try:
        from ordereddict import OrderedDict
    except ImportError:
        OrderedDict = dict

try:  # pragma no cover
    _basestring = basestring
except NameError:  # pragma no cover
    _basestring = str
try:  # pragma no cover
    _unicode = unicode
except NameError:  # pragma no cover
    _unicode = str

__author__ = 'Martin Blech'
__version__ = '0.11.0'
__license__ = 'MIT'


class ParsingInterrupted(Exception):
    pass


class _DictSAXHandler(object):
    def __init__(self,
                 item_depth=0,
                 item_callback=lambda *args: True,
                 xml_attribs=True,
                 attr_prefix='@',
                 cdata_key='#text',
                 force_cdata=False,
                 cdata_separator='',
                 postprocessor=None,
                 dict_constructor=OrderedDict,
                 strip_whitespace=True,
                 namespace_separator=':',
                 namespaces=None,
                 force_list=None,
                 ordered_mixed_children=False):
        self.path = []
        self.stack = []
        self.data = []
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        self.strip_whitespace = strip_whitespace
        self.namespace_separator = namespace_separator
        self.namespaces = namespaces
        self.namespace_declarations = OrderedDict()
        self.force_list = force_list
        self.ordered_mixed_children = ordered_mixed_children
        self.counter = 0

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
        ret_attrs = attrs
        if not isinstance(attrs, dict):
            ret_attrs = self.dict_constructor(zip(attrs[0::2], attrs[1::2]))
        if self.ordered_mixed_children:
            ret_attrs["__order__"] = self.counter
            self.counter += 1
        return ret_attrs

    def startNamespaceDecl(self, prefix, uri):
        self.namespace_declarations[prefix or ''] = uri

    def startElement(self, full_name, attrs):
        name = self._build_name(full_name)
        attrs = self._attrs_to_dict(attrs)
        if attrs and self.namespace_declarations:
            attrs['xmlns'] = self.namespace_declarations
            self.namespace_declarations = OrderedDict()
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attr_entries = []
                for key, value in attrs.items():
                    key = self.attr_prefix+self._build_name(key)
                    if self.postprocessor:
                        entry = self.postprocessor(self.path, key, value)
                    else:
                        entry = (key, value)
                    if entry:
                        attr_entries.append(entry)
                attrs = self.dict_constructor(attr_entries)
            else:
                attrs = None
            self.item = attrs or None
            self.data = []

    def endElement(self, full_name):
        name = self._build_name(full_name)
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = (None if not self.data
                        else self.cdata_separator.join(self.data))

            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            data = (None if not self.data
                    else self.cdata_separator.join(self.data))
            item = self.item
            self.item, self.data = self.stack.pop()
            if self.strip_whitespace and data:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = None
            self.data = []
        self.path.pop()

    def characters(self, data):
        if not self.data:
            self.data = [data]
        else:
            self.data.append(data)

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                item[key] = [value, data]
        except KeyError:
            if self._should_force_list(key, data):
                item[key] = [data]
            else:
                item[key] = data
        return item

    def _should_force_list(self, key, value):
        if not self.force_list:
            return False
        try:
            return key in self.force_list
        except TypeError:
            return self.force_list(self.path[:-1], key, value)


def parse(xml_input, encoding=None, expat=expat, process_namespaces=False,
          namespace_separator=':', disable_entities=True,
          ordered_mixed_children=False, **kwargs):
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
        ...     print('path:%s item:%s' % (path, item))
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

    You can use the force_list argument to force lists to be created even
    when there is only a single child of a given level of hierarchy. The
    force_list argument is a tuple of keys. If the key for a given level
    of hierarchy is in the force_list argument, that level of hierarchy
    will have a list as a child (even if there is only one sub-element).
    The index_keys operation takes precendence over this. This is applied
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

    If called with force_list=('interface',), it will produce
    this dictionary:
    {'servers':
      {'server':
        {'name': 'host1',
         'os': 'Linux'},
         'interfaces':
          {'interface':
            [ {'name': 'em0', 'ip_address': '10.0.0.1' } ] } } }

    `force_list` can also be a callable that receives `path`, `key` and
    `value`. This is helpful in cases where the logic that decides whether
    a list should be forced is more complex.

    The parameter ordered_mixed_children will cause the parser to add an
    attribute to each element in the data with a key `@__order__`, with a value
    that corresponds to the element's processing order within the document.
    By default, mixed child elements are grouped by name and only keep their
    relative order. Sometimes the order does matter, but the system you're
    working with doesn't have any other way to indicate order than by the
    coincidence of order in the document.

    For example, this input:
    <a>
      <b>1</b>
      <c>2</c>
      <b>3</b>
    </a>

    Would normally be parsed as:
    {"a": {"b": [1, 3], "c": 2}}

    This would then be unparsed as:
    <a>
      <b>1</b>
      <b>3</b>
      <c>2</c>
    </a>

    With `ordered_mixed_children=True`, the order information is included so
    that the original input is produced when unparsing (the `@__order__`
    attribute is removed).
    {"a": {
      "@__order__": 1,
      "b": ({"@__order__": 2, "#text": 1},
           {"@__order__": 3, "#text": 3}),
      "c": {"@__order__": 4, "#text": 2}
      }
    }
    """
    handler = _DictSAXHandler(namespace_separator=namespace_separator,
                              ordered_mixed_children=ordered_mixed_children,
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
    parser.StartNamespaceDeclHandler = handler.startNamespaceDecl
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    parser.buffer_text = True
    if disable_entities:
        try:
            # Attempt to disable DTD in Jython's expat parser (Xerces-J).
            feature = "http://apache.org/xml/features/disallow-doctype-decl"
            parser._reader.setFeature(feature, True)
        except AttributeError:
            # For CPython / expat parser.
            # Anything not handled ends up here and entities aren't expanded.
            parser.DefaultHandler = lambda x: None
            # Expects an integer return; zero means failure -> expat.ExpatError.
            parser.ExternalEntityRefHandler = lambda *x: 1
    if hasattr(xml_input, 'read'):
        parser.ParseFile(xml_input)
    else:
        parser.Parse(xml_input, True)
    return handler.item


def _process_namespace(name, namespaces, ns_sep=':', attr_prefix='@'):
    if not namespaces:
        return name
    try:
        ns, name = name.rsplit(ns_sep, 1)
    except ValueError:
        pass
    else:
        ns_res = namespaces.get(ns.strip(attr_prefix))
        name = '{0}{1}{2}{3}'.format(
            attr_prefix if ns.startswith(attr_prefix) else '',
            ns_res, ns_sep, name) if ns_res else name
    return name


def _emit(key, value, content_handler,
          attr_prefix='@',
          cdata_key='#text',
          depth=0,
          preprocessor=None,
          pretty=False,
          newl='\n',
          indent='\t',
          namespace_separator=':',
          namespaces=None,
          full_document=True,
          ordered_mixed_children=False):
    key = _process_namespace(key, namespaces, namespace_separator, attr_prefix)
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
        attrs = OrderedDict()
        children = []
        for ik, iv in v.items():
            if ik == cdata_key:
                cdata = iv
                continue
            if ik.startswith(attr_prefix):
                ik = _process_namespace(ik, namespaces, namespace_separator,
                                        attr_prefix)
                if ik == '@xmlns' and isinstance(iv, dict):
                    for k, v in iv.items():
                        attr = 'xmlns{0}'.format(':{0}'.format(k) if k else '')
                        attrs[attr] = _unicode(v)
                    continue
                if not isinstance(iv, _unicode):
                    iv = _unicode(iv)
                attrs[ik[len(attr_prefix):]] = iv
                continue
            children.append((ik, iv))

        if ordered_mixed_children:
            order_attr = "__order__"
            attrs.pop(order_attr, None)
            order_key = attr_prefix + order_attr
            # Each ordered element is "lifted" one level into a list of dicts.
            lift_list = []
            for child_key, child_value in children:
                if isinstance(child_value, (list, tuple)):
                    for val in child_value:
                        lift_list.append((child_key, val))
                else:
                    lift_list.append((child_key, child_value))
            children = sorted(
                lift_list, key=lambda x: get_child_order_key(x, order_key))

        if pretty:
            content_handler.ignorableWhitespace(depth * indent)
        if len(attrs) == 0 and cdata is None and len(children) == 0:
            content_handler.startElement(key, attrs)
            content_handler.endElement(key)
            if pretty:
                content_handler.ignorableWhitespace(newl)
            continue
        content_handler.startElement(key, AttributesImpl(attrs))
        if pretty and children:
            content_handler.ignorableWhitespace(newl)
        for child_key, child_value in children:
            _emit(child_key, child_value, content_handler,
                  attr_prefix, cdata_key, depth+1, preprocessor,
                  pretty, newl, indent, namespaces=namespaces,
                  namespace_separator=namespace_separator,
                  ordered_mixed_children=ordered_mixed_children)
        if cdata is not None:
            content_handler.characters(cdata)
        if pretty and children:
            content_handler.ignorableWhitespace(depth * indent)
        content_handler.endElement(key)
        if pretty and depth:
            content_handler.ignorableWhitespace(newl)


def get_child_order_key(item, order_key):
    """
    Get the order key for a child element, default to infinity (stable last).
    """
    infinity = float('inf')
    item_key, item_value = item
    if isinstance(item_value, dict):
        return item_value.pop(order_key, infinity)
    else:
        return infinity


class XMLGeneratorShort(XMLGenerator):
    """Copy of functionality added in Python 3.2 for short empty elements."""

    def __init__(self, out=None, encoding="utf-8",
                 short_empty_elements=False):
        XMLGenerator.__init__(self, out, encoding)
        self._short_empty_elements = short_empty_elements
        self._pending_start_element = False
        if getattr(self, "_out", None) is None:
            # Python 3.2 removed this for no apparent reason.
            self._out = out

    def startElement(self, name, attrs):
        if self._pending_start_element:
            self._write(_unicode('>'))
            self._pending_start_element = False
        self._write(_unicode('<' + name))
        for (name, value) in attrs.items():
            self._write(_unicode(' %s=%s' % (name, quoteattr(value))))
        if self._short_empty_elements:
            self._pending_start_element = True
        else:
            self._write(_unicode('>'))

    def endElement(self, name):
        if self._pending_start_element:
            self._write(_unicode('/>'))
            self._pending_start_element = False
        else:
            self._write(_unicode('</%s>' % name))

    def _write(self, text):
        if isinstance(text, str):
            self._out.write(text)
        else:
            self._out.write(text.encode(self._encoding, 'xmlcharrefreplace'))


def unparse(input_dict, output=None, encoding='utf-8', full_document=True,
            short_empty_elements=False, ordered_mixed_children=False, **kwargs):
    """Emit an XML document for the given `input_dict` (reverse of `parse`).

    The resulting XML document is returned as a string, but if `output` (a
    file-like object) is specified, it is written there instead.

    Dictionary keys prefixed with `attr_prefix` (default=`'@'`) are interpreted
    as XML node attributes, whereas keys equal to `cdata_key`
    (default=`'#text'`) are treated as character data.

    The `pretty` parameter (default=`False`) enables pretty-printing. In this
    mode, lines are terminated with `'\n'` and indented with `'\t'`, but this
    can be customized with the `newl` and `indent` parameters.

    The `ordered_mixed_children` parameter (default=`False`) is available if
    the output of mixed child elements is significant. By default, mixed child
    elements are grouped by name and only keep their relative order. In addition
    to this parameter, the order must be specified in the data. To do this,
    add the sort order to an `@__order__` attribute in each element that should
    be ordered. The order attribute is removed from the output XML. Unordered
    elements are placed after those with an order specified, in their relative
    order.

    The `short_empty_elements` parameter (default=False) will cause empty
    elements to be output in their short form, e.g. "<tag/>" vs. "<tag></tag>".
    This feature was added to the default XMLGenerator in Python 3.2.
    """
    if full_document and len(input_dict) != 1:
        raise ValueError('Document must have exactly one root.')
    must_return = False
    if output is None:
        output = StringIO()
        must_return = True
    content_handler = XMLGeneratorShort(output, encoding, short_empty_elements)
    if full_document:
        content_handler.startDocument()
    for key, value in input_dict.items():
        _emit(key, value, content_handler, full_document=full_document,
              ordered_mixed_children=ordered_mixed_children, **kwargs)
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
    try:
        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
    except AttributeError:
        stdin = sys.stdin
        stdout = sys.stdout

    (item_depth,) = sys.argv[1:]
    item_depth = int(item_depth)


    def handle_item(path, item):
        marshal.dump((path, item), stdout)
        return True

    try:
        root = parse(stdin,
                     item_depth=item_depth,
                     item_callback=handle_item,
                     dict_constructor=dict)
        if item_depth == 0:
            handle_item([], root)
    except KeyboardInterrupt:
        pass
