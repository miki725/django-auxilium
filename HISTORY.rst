.. :changelog:

History
-------

0.1.3 (2018-05-24)
~~~~~~~~~~~~~~~~~~

* Fixed: Django 2.0 support for minify middleware.

0.1.2 (2017-11-22)
~~~~~~~~~~~~~~~~~~

* Fixed: Not removing all spaces between html tags.
  Sometimes spaces matter for formatting.
  For example ``<strong>Hello</strong> <i>World</i>`` cannot be minified any further.

0.1.1 (2016-09-26)
~~~~~~~~~~~~~~~~~~

* Fixed: Cache properties now allow to set cache value via ``foo = bar``
  syntax when cache descriptor has ``as_property == True``

0.1.0 (2015-11-26)
~~~~~~~~~~~~~~~~~~

* First release on PyPI.
