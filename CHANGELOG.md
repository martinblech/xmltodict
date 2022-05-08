CHANGELOG
=========

v0.13.0
-------

* Add install info to readme for openSUSE. (#205)
  * Thanks, @smarlowucf!
* Support defaultdict for namespace mapping (#211)
  * Thanks, @nathanalderson!
* parse(generator) is now possible (#212)
  * Thanks, @xandey!
* Processing comments on parsing from xml to dict (connected to #109) (#221)
  * Thanks, @svetazol!
* Add expand_iter kw to unparse to expand iterables (#213)
  * Thanks, @claweyenuk!
* Fixed some typos
  * Thanks, @timgates42 and @kianmeng!
* Add support for python3.8
  * Thanks, @t0b3!
* Drop Jython/Python 2 and add Python 3.9/3.10.
* Drop OrderedDict in Python >= 3.7
* Do not use len() to determine if a sequence is empty
  * Thanks, @DimitriPapadopoulos!
* Add more namespace attribute tests
  * Thanks, @leogregianin!
* Fix encoding issue in setup.py
  * Thanks, @rjarry!

v0.12.0
-------

* Allow force_commits=True for getting all keys as lists (#204)
* README.md: fix useless uses of cat (#200)
* Add FreeBSD install instructions (#199)
* Fix and simplify travis config (#192)
* Add support for Python 3.7 (#189)
* Drop support for EOL Python (#191)
* Use Markdown long_description on PyPI (#190)
* correct spelling mistake (#165)
* correctly unparse booleans (#180)
* Updates README.md with svg badge

v0.11.0
-------

* Determine fileness by checking for `read` attr
  * Thanks, @jwodder!
* Add support for Python 3.6.
  * Thanks, @cclauss!
* Release as a universal wheel.
  * Thanks, @adamchainz!
* Updated docs examples to use print function.
  * Thanks, @cdeil!
* unparse: pass short_empty_elements to XMLGenerator
  * Thanks, @zhanglei002!
* Added namespace support when unparsing.
  * Thanks, @imiric!

v0.10.2
-------

* Fixed defusedexpat expat import.
  * Thanks, @fiebiga!

v0.10.1
-------

* Use defusedexpat if available.
* Allow non-string attributes in unparse.
* Add postprocessor support for attributes.
* Make command line interface Python 3-compatible.

v0.10.0
-------

* Add force_list feature.
  * Thanks, @guewen and @jonlooney!
* Add support for Python 3.4 and 3.5.
* Performance optimization: use list instead of string for CDATA.
  * Thanks, @bharel!
* Include Arch Linux package instructions in README.
  * Thanks, @felixonmars!
* Improved documentation.
  * Thanks, @ubershmekel!
* Allow any iterable in unparse, not just lists.
  * Thanks, @bzamecnik!
* Bugfix: Process namespaces in attributes too.
* Better testing under Python 2.6.
  * Thanks, @TyMaszWeb!

v0.9.2
------

* Fix multiroot check for list values (edge case reported by @JKillian)

v0.9.1
------

* Only check single root when full_document=True (Thanks @JKillian!)

v0.9.0
------

* Added CHANGELOG.md
* Avoid ternary operator in call to ParserCreate().
* Adding Python 3.4 to Tox test environment.
* Added full_document flag to unparse (default=True).

v0.8.7
------

* Merge pull request #56 from HansWeltar/master
* Improve performance for large files
* Updated README unparse example with pretty=True.

v0.8.6
------

* Fixed extra newlines in pretty print mode.
* Fixed all flake8 warnings.

v0.8.5
------

* Added Tox config.
* Let expat figure out the doc encoding.

v0.8.4
------

* Fixed Jython TravisCI build.
* Moved nose and coverage to tests_require.
* Dropping python 2.5 from travis.yml.

v0.8.3
------

* Use system setuptools if available.

v0.8.2
------

* Switch to latest setuptools.

v0.8.1
------

* Include distribute_setup.py in MANIFEST.in
* Updated package classifiers (python versions, PyPy, Jython).

v0.8.0
------

* Merge pull request #40 from martinblech/jython-support
* Adding Jython support.
* Fix streaming example callback (must return True)

v0.7.0
------

* Merge pull request #35 from martinblech/namespace-support
* Adding support for XML namespaces.
* Merge pull request #33 from bgilb/master
* fixes whitespace style
* changes module import syntax and assertRaises
* adds unittest assertRaises

v0.6.0
------

* Merge pull request #31 from martinblech/document-unparse
* Adding documentation for unparse()
* Merge pull request #30 from martinblech/prettyprint
* Adding support for pretty print in unparse()

v0.5.1
------

* Merge pull request #29 from dusual/master
* ordereddict import for less 2.6 if available

v0.5.0
------

* Allow using alternate versions of `expat`.
* Added shameless link to GitTip.
* Merge pull request #20 from kevbo/master
* Adds unparse example to README

v0.4.6
------

* fix try/catch block for pypi (throws AttributeError instead of TypeError)
* prevent encoding an already encoded string
* removed unnecessary try/catch for xml_input.encode(). check if file or string, EAFP style. (thanks @turicas)

v0.4.5
------

* test with python 3.3 too
* avoid u'unicode' syntax (fails in python 3.2)
* handle unicode input strings properly
* add strip_whitespace option (default=True)
* Merge pull request #16 from slestak/master
* fix unittest
* working with upstream to improve #15
* remove pythonpath tweaks, change loc of #15 patch
* upstream  #15

v0.4.4
------

* test attribute order roundtrip only if OrderedDict is available (python >= 2.7)
* Merge branch 'master' of github.com:martinblech/xmltodict
* preserve xml attribute order (fixes #13)

v0.4.3
------

* fix #12: postprocess cdata items too
* added info about official fedora package

v0.4.2
------

* Merge pull request #11 from ralphbean/master
* Include README, LICENSE, and tests in the distributed tarball.

v0.4.1
------

* take all characters (no need to strip and filter)
* fixed CLI (marshal only takes dict, not OrderedDict)
* ignore MANIFEST

v0.4
----

* #8 preprocessing callback in unparse()

v0.3
----

* implemented postprocessor callback (#6)
* update readme with install instructions

v0.2
----

* link to travis-ci build status
* more complete info in setup.py (for uploading to PyPi)
* coverage annotations for tricky py3k workarounds
* py3k compatibility
* removed unused __future__ print_function
* using io.StringIO on py3k
* removed unnecessary exception catching
* initial travis-ci configuration
* made _emit function private
* unparse functionality
* added tests
* updated (c) notice to acknowledge individual contributors
* added license information
* fixed README
* removed temp build directory and added a .gitignore to avoid that happening again
* Merge pull request #1 from scottscott/master
* Added setup script to make xmltodict a Python module.
* fixed bad handling of cdata in semistructured xml, changed _CDATA_ to #text as default
* added attr_prefix, cdata_key and force_cdata parameters
* links in README
* links in README
* improved README
* initial commit

