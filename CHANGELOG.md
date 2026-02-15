# Changelog

## [1.0.3](https://github.com/martinblech/xmltodict/compare/v1.0.2...v1.0.3) (2026-02-15)


### Bug Fixes

* **unparse:** serialize None text/attrs as empty values (fixes [#401](https://github.com/martinblech/xmltodict/issues/401)) ([aa16511](https://github.com/martinblech/xmltodict/commit/aa165113bef2b3a1a822209863343b9dc9ffe43a))


### Documentation

* **readme:** fix Fedora and Arch package links ([fd6a73b](https://github.com/martinblech/xmltodict/commit/fd6a73bf606c3932bcc82bf559a70867a1dd75cd))

## [1.0.2](https://github.com/martinblech/xmltodict/compare/v1.0.1...v1.0.2) (2025-09-17)


### Bug Fixes

* allow DOCTYPE with disable_entities=True (default) ([25b61a4](https://github.com/martinblech/xmltodict/commit/25b61a41f580cfc211df07c5fbbf603bd8eb5a5f))

## [1.0.1](https://github.com/martinblech/xmltodict/compare/v1.0.0...v1.0.1) (2025-09-17)


### Bug Fixes

* fail closed when entities disabled ([c986d2d](https://github.com/martinblech/xmltodict/commit/c986d2d37a93d45fcc059b09063d9d9c45a655ec))
* validate XML comments ([3d4d2d3](https://github.com/martinblech/xmltodict/commit/3d4d2d3a4cd0f68d1211dba549010261fa87b969))


### Documentation

* add SECURITY.md ([6413023](https://github.com/martinblech/xmltodict/commit/64130233c8fea272a5f82f2f585e1593523ec1b1))
* clarify behavior for empty lists ([2025b5c](https://github.com/martinblech/xmltodict/commit/2025b5cb5e64fc9c4d54b8644187a0a193bdd0ed))
* clarify process_comments docs ([6b464fc](https://github.com/martinblech/xmltodict/commit/6b464fce284a93dbb292f3d063c9f310a478a014))
* clarify strip whitespace comment behavior ([b3e2203](https://github.com/martinblech/xmltodict/commit/b3e22032d21cc387d6cecf3930116e8fdc3151cf))
* create AGENTS.md for coding agents ([0da66ee](https://github.com/martinblech/xmltodict/commit/0da66ee797ced7479312aecef92c6a25e235007c))
* replace travis with actions badge ([2576b94](https://github.com/martinblech/xmltodict/commit/2576b94c918fbd154489a95dbbb3feda8bd3cbd8))
* update CONTRIBUTING.md ([db39180](https://github.com/martinblech/xmltodict/commit/db3918057cf125af989a1263d52df8df5ef8c642))

## [1.0.0](https://github.com/martinblech/xmltodict/compare/v0.15.1...v1.0.0) (2025-09-12)


### ⚠ BREAKING CHANGES

* modernize for Python 3.9+; drop legacy compat paths

### Features

* **unparse:** add limited XML comment round-trip; unify `_emit` behavior ([e43537e](https://github.com/martinblech/xmltodict/commit/e43537eee61c20ef50f0e4242eb9223de7a6aefd))
* **unparse:** add selective `force_cdata` support (bool/tuple/callable) ([a497fed](https://github.com/martinblech/xmltodict/commit/a497fedb7d6103d68af155543ac3337a73778b19)), closes [#375](https://github.com/martinblech/xmltodict/issues/375)


### Bug Fixes

* **namespaces:** attach `[@xmlns](https://github.com/xmlns)` to declaring element when process_namespaces=True ([f0322e5](https://github.com/martinblech/xmltodict/commit/f0322e578184421693434902547f330f4f0a44c3)), closes [#163](https://github.com/martinblech/xmltodict/issues/163)
* **streaming:** avoid parent accumulation at item_depth; add regression tests ([220240c](https://github.com/martinblech/xmltodict/commit/220240c5eb2d12b75adf26cc84ec9c803ce8bb2b))
* **unparse:** handle non-string `#text` with attributes; unify value conversion ([927a025](https://github.com/martinblech/xmltodict/commit/927a025ae8a62cbb542d5caff38b29161a2096fa)), closes [#366](https://github.com/martinblech/xmltodict/issues/366)
* **unparse:** skip empty lists to keep pretty/compact outputs consistent ([ab4c86f](https://github.com/martinblech/xmltodict/commit/ab4c86fed24dc8ef0e932a524edfb01c6453ecf6))


### Reverts

* remove initial Release Drafter config ([c0b74ed](https://github.com/martinblech/xmltodict/commit/c0b74ed58f933bffd160c60a58620f672710ff7c))


### Documentation

* **readme:** add API reference for parse()/unparse() kwargs ([e5039ad](https://github.com/martinblech/xmltodict/commit/e5039ad3f5159cc45ac1d52c4aa901ca50d4c722))
* **readme:** mention types-xmltodict stub package ([58ec03e](https://github.com/martinblech/xmltodict/commit/58ec03e6d94f17ed359742d9ce2f99e796669694))


### Code Refactoring

* modernize for Python 3.9+; drop legacy compat paths ([7364427](https://github.com/martinblech/xmltodict/commit/7364427c86c62f55ad4c2dce96df6761da69c354))

## v0.15.1
* Security: Further harden XML injection prevention during unparse (follow-up to
  v0.15.0). In addition to '<'/'>' rejection, now also reject element and
  attribute names (including `@xmlns` prefixes) that:
  - start with '?' or '!'
  - contain '/' or any whitespace
  - contain quotes (' or ") or '='
  - are non-strings (names must be `str`; no coercion)

## v0.15.0
* Security: Prevent XML injection (CVE-2025-9375) by rejecting '<'/'>' in
  element and attribute names (including `@xmlns` prefixes) during unparse.
  This limits validation to avoiding tag-context escapes; attribute values
  continue to be escaped by the SAX `XMLGenerator`.
  Advisory: https://fluidattacks.com/advisories/mono

## v0.14.2
* Revert "Ensure significant whitespace is not trimmed"
  * This changed was backwards incompatible and caused downstream issues.

## v0.14.1
* Drop support for Python older than 3.6
* Additional ruff/Pyflakes/codespell fixes.
  * Thanks @DimitriPapadopoulos!

## v0.14.0

* Drop old Python 2 support leftover code and apply several RUFF code health fixes.
  * Thanks, @DimitriPapadopoulos!
* Add Python 3.11, 3.12 and 3.13 support and tests.
  * Thanks, @angvp!
* Tests in gh-action.
  * Thanks, @almaz.kun!
* Remove defusedexpat import.
  * Thanks, @hanno!
* Replace deprecated BadZipfile with BadZipFile.
  * Thanks, @hugovk!
* Support indent using integer format, enable `python -m unittest tests/*.py`.
  * Thanks, @hiiwave!
* Ensure significant whitespace is not trimmed
  * Thanks, @trey.franklin!
* added conda installation command
  * Thanks, @sugatoray!
* fix attributes not appearing in streaming mode
  * Thanks, @timnguyen001!
* Fix Travis CI status badge URL
* Update push_release.sh to use twine.

## v0.13.0

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

## v0.12.0

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

## v0.11.0

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

## v0.10.2

* Fixed defusedexpat expat import.
  * Thanks, @fiebiga!

## v0.10.1

* Use defusedexpat if available.
* Allow non-string attributes in unparse.
* Add postprocessor support for attributes.
* Make command line interface Python 3-compatible.

## v0.10.0

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

## v0.9.2

* Fix multiroot check for list values (edge case reported by @JKillian)

## v0.9.1

* Only check single root when full_document=True (Thanks @JKillian!)

## v0.9.0

* Added CHANGELOG.md
* Avoid ternary operator in call to ParserCreate().
* Adding Python 3.4 to Tox test environment.
* Added full_document flag to unparse (default=True).

## v0.8.7

* Merge pull request #56 from HansWeltar/master
* Improve performance for large files
* Updated README unparse example with pretty=True.

## v0.8.6

* Fixed extra newlines in pretty print mode.
* Fixed all flake8 warnings.

## v0.8.5

* Added Tox config.
* Let expat figure out the doc encoding.

## v0.8.4

* Fixed Jython TravisCI build.
* Moved nose and coverage to tests_require.
* Dropping python 2.5 from travis.yml.

## v0.8.3

* Use system setuptools if available.

## v0.8.2

* Switch to latest setuptools.

## v0.8.1

* Include distribute_setup.py in MANIFEST.in
* Updated package classifiers (python versions, PyPy, Jython).

## v0.8.0

* Merge pull request #40 from martinblech/jython-support
* Adding Jython support.
* Fix streaming example callback (must return True)

## v0.7.0

* Merge pull request #35 from martinblech/namespace-support
* Adding support for XML namespaces.
* Merge pull request #33 from bgilb/master
* fixes whitespace style
* changes module import syntax and assertRaises
* adds unittest assertRaises

## v0.6.0

* Merge pull request #31 from martinblech/document-unparse
* Adding documentation for unparse()
* Merge pull request #30 from martinblech/prettyprint
* Adding support for pretty print in unparse()

## v0.5.1

* Merge pull request #29 from dusual/master
* ordereddict import for less 2.6 if available

## v0.5.0

* Allow using alternate versions of `expat`.
* Added shameless link to GitTip.
* Merge pull request #20 from kevbo/master
* Adds unparse example to README

## v0.4.6

* fix try/catch block for pypi (throws AttributeError instead of TypeError)
* prevent encoding an already encoded string
* removed unnecessary try/catch for xml_input.encode(). check if file or string, EAFP style. (thanks @turicas)

## v0.4.5

* test with python 3.3 too
* avoid u'unicode' syntax (fails in python 3.2)
* handle unicode input strings properly
* add strip_whitespace option (default=True)
* Merge pull request #16 from slestak/master
* fix unittest
* working with upstream to improve #15
* remove pythonpath tweaks, change loc of #15 patch
* upstream  #15

## v0.4.4

* test attribute order roundtrip only if OrderedDict is available (python >= 2.7)
* Merge branch 'master' of github.com:martinblech/xmltodict
* preserve xml attribute order (fixes #13)

## v0.4.3

* fix #12: postprocess cdata items too
* added info about official fedora package

## v0.4.2

* Merge pull request #11 from ralphbean/master
* Include README, LICENSE, and tests in the distributed tarball.

## v0.4.1

* take all characters (no need to strip and filter)
* fixed CLI (marshal only takes dict, not OrderedDict)
* ignore MANIFEST

## v0.4

* #8 preprocessing callback in unparse()

## v0.3

* implemented postprocessor callback (#6)
* update readme with install instructions

## v0.2

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
