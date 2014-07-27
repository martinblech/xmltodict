# xmltodict

`xmltodict` is a Python module that makes working with XML feel like you are working with [JSON](http://docs.python.org/library/json.html), as in this ["spec"](http://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html):

[![Build Status](https://secure.travis-ci.org/martinblech/xmltodict.png)](http://travis-ci.org/martinblech/xmltodict)

```python
>>> doc = xmltodict.parse("""
... <mydocument has="an attribute">
...   <and>
...     <many>elements</many>
...     <many>more elements</many>
...   </and>
...   <plus a="complex">
...     element as well
...   </plus>
... </mydocument>
... """)
>>>
>>> doc['mydocument']['@has']
u'an attribute'
>>> doc['mydocument']['and']['many']
[u'elements', u'more elements']
>>> doc['mydocument']['plus']['@a']
u'complex'
>>> doc['mydocument']['plus']['#text']
u'element as well'
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

## Streaming mode

`xmltodict` is very fast ([Expat](http://docs.python.org/library/pyexpat.html)-based) and has a streaming mode with a small memory footprint, suitable for big XML dumps like [Discogs](http://discogs.com/data/) or [Wikipedia](http://dumps.wikimedia.org/):

```python
>>> def handle_artist(_, artist):
...     print artist['name']
...     return True
>>> 
>>> xmltodict.parse(GzipFile('discogs_artists.xml.gz'),
...     item_depth=2, item_callback=handle_artist)
A Perfect Circle
Fantômas
King Crimson
Chris Potter
...
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

## Donate

If you love `xmltodict`, consider supporting the author [on Gittip](https://www.gittip.com/martinblech/).
