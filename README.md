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

It's very fast ([Expat](http://docs.python.org/library/pyexpat.html)-based) and has a streaming mode with a small memory footprint, suitable for big XML dumps like [Discogs](http://discogs.com/data/) or [Wikipedia](http://dumps.wikimedia.org/):

```python
>>> def handle_artist(_, artist):
...     print artist['name']
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

## Ok, how do I get it?

You just need to

```sh
$ pip install xmltodict
```
