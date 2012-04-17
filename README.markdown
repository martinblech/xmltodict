# xmltodict

`xmltodict` is a Python module that makes working with XML feel like you are working with JSON:

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
>>> doc['mydocument']['plus']['_CDATA_']
u'element as well'
```

It's very fast (Expat-based) and has a streaming mode with a small memory footprint, suitable for big XML dumps like Discogs or Wikipedia:

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
