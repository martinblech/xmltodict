# xmltodict

`xmltodict` is a Python module that makes working with XML feel like you are working with [JSON](http://docs.python.org/library/json.html), as in this ["spec"](http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html):

[![Build Status](https://secure.travis-ci.org/martinblech/xmltodict.png)](http://travis-ci.org/martinblech/xmltodict)

```python
>>> print(json.dumps(xmltodict.parse("""
...  <mydocument has="an attribute">
...    <and>
...      <many>elements</many>
...      <many>more elements</many>
...    </and>
...    <plus a="complex">
...      element as well
...    </plus>
...  </mydocument>
...  """), indent=4))
{
    "mydocument": {
        "@has": "an attribute", 
        "and": {
            "many": [
                "elements", 
                "more elements"
            ]
        }, 
        "plus": {
            "@a": "complex", 
            "#text": "element as well"
        }
    }
}
```

## Namespace support

By default, `xmltodict` does no XML namespace processing (it just treats namespace declarations as regular node attributes), but passing `process_namespaces=True` will make it expand namespaces for you:

```python
>>> xml = """
... <root xmlns="http://defaultns.com/"
...       xmlns:a="http://a.com/"
...       xmlns:b="http://b.com/">
...   <x>1</x>
...   <a:y>2</a:y>
...   <b:z>3</b:z>
... </root>
... """
>>> xmltodict.parse(xml, process_namespaces=True) == {
...     'http://defaultns.com/:root': {
...         'http://defaultns.com/:x': '1',
...         'http://a.com/:y': '2',
...         'http://b.com/:z': '3',
...     }
... }
True
```

It also lets you collapse certain namespaces to shorthand prefixes, or skip them altogether:

```python
>>> namespaces = {
...     'http://defaultns.com/': None, # skip this namespace
...     'http://a.com/': 'ns_a', # collapse "http://a.com/" -> "ns_a"
... }
>>> xmltodict.parse(xml, process_namespaces=True, namespaces=namespaces) == {
...     'root': {
...         'x': '1',
...         'ns_a:y': '2',
...         'http://b.com/:z': '3',
...     },
... }
True
```

## Streaming Mode

`xmltodict` is very fast ([Expat](http://docs.python.org/library/pyexpat.html)-based) and has a streaming mode with a small memory footprint, suitable for big XML dumps like [Discogs](http://discogs.com/data/) or [Wikipedia](http://dumps.wikimedia.org/).

In the streaming mode, intermediate values are returned during parsing (rather than a representation of the full document being returned after parsing is complete). There are two versions of streaming mode: one which uses a callback functon and one which returns an iterator. (And, the two modes can actually be combined, as well.)

You activate streaming mode by calling the parser with a `generator` argument that evaluates to True and/or an `item_depth` argument that is greater than 0.

### Streaming Mode: Generator/Iterator

If the `generator` argument evaluates to True, the function returns an iterator. On each iteration, it returns a new node from the specified `item_depth`. (An `item_depth` of 0 will return the full tree, an `item_depth` of 1 will return the contents of the root tag, an `item_depth` of 2 will return the contents of the tags of the root element's children, etc.) Each iteration returns a tuple of the `path` from the document root to the item (name-attribs pairs) and the `item` (the contents of the item). The contents of the item will be the value of the sub-node. If the sub-node is an XML tree that would be represened by a dictionary, the iterator will return a dictionary as the `item`. If the sub-node only contains CDATA that would be represented in a text node, the iterator will return a text node as the `item`. If the node is an empty tag which would be represented by None, the iterator returns None as the `item`.

Example:
```python
>>> xml = """\
... <a prop="x">
...   <b>1</b>
...   <b>2</b>
... </a>"""
>>> for (path, item) in xmltodict.parse(xml, generator=True, item_depth=2):
...     print 'path:%s item:%s' % (path, item)
...
path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:1
path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:2
```

### Streaming Mode: Callback

If `item_depth` is greater than 0 and the user specifies an `item_callback`, it will call the `item_callback` every time an item at the specified depth is found.

If `item_depth` is non-0 and `generator` evaluates to False, the function will not return a dictionary for the root element (which is the default behavior). Instead, it will call the `item_callback` every time an item at the specified depth is found and will return `None` in the end.

The `item_callback` function receives the same parameters returned by the `generator`: the `path` from the document root to the item (name-attribs pairs), and the `item` (dict). If the callback's return value is false-ish, parsing will be stopped with the :class:`ParsingInterrupted` exception.

```python
>>> def handle(path, item):
...     print 'path:%s item:%s' % (path, item)
...     return True
...
>>> xml = """\
... <a prop="x">
...   <b>1</b>
...   <b>2</b>
... </a>"""
>>> xmltodict.parse(xml, item_depth=2, item_callback=handle)
path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:1
path:[(u'a', {u'prop': u'x'}), (u'b', None)] item:2
```

It can also be used from the command line to pipe objects to a script like this:

```python
import sys, marshal
while True:
    _, article = marshal.load(sys.stdin)
    print article['title']
```

```sh
$ cat enwiki-pages-articles.xml.bz2 | bunzip2 | xmltodict.py 2 | myscript.py
AccessibleComputing
Anarchism
AfghanistanHistory
AfghanistanGeography
AfghanistanPeople
AfghanistanCommunications
Autism
...
```

Or just cache the dicts so you don't have to parse that big XML file again. You do this only once:

```sh
$ cat enwiki-pages-articles.xml.bz2 | bunzip2 | xmltodict.py 2 | gzip > enwiki.dicts.gz
```

And you reuse the dicts with every script that needs them:

```sh
$ cat enwiki.dicts.gz | gunzip | script1.py
$ cat enwiki.dicts.gz | gunzip | script2.py
...
```

## Roundtripping

You can also convert in the other direction, using the `unparse()` method:

```python
>>> mydict = {
...     'response': {
...             'status': 'good',
...             'last_updated': '2014-02-16T23:10:12Z',
...     }
... }
>>> print unparse(mydict, pretty=True)
<?xml version="1.0" encoding="utf-8"?>
<response>
	<status>good</status>
	<last_updated>2014-02-16T23:10:12Z</last_updated>
</response>
```

## Ok, how do I get it?

You just need to

```sh
$ pip install xmltodict
```

There is an [official Fedora package for xmltodict](https://admin.fedoraproject.org/pkgdb/acls/name/python-xmltodict). If you are on Fedora or RHEL, you can do:

```sh
$ sudo yum install python-xmltodict
```

There is also an [official Arch Linux package for xmltodict](https://www.archlinux.org/packages/community/any/python-xmltodict/). You can use pacman to install if you are using Arch:

```sh
$ sudo pacman -S python-xmltodict
```

## Donate

If you love `xmltodict`, consider supporting the author [on Gittip](https://www.gittip.com/martinblech/).
