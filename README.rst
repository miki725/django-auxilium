Django Auxilium
===============

.. image:: https://badge.fury.io/py/django-auxilium.svg
    :target: https://badge.fury.io/py/django-auxilium
    :alt: PyPI version
.. image:: https://travis-ci.org/miki725/django-auxilium.svg?branch=develop
    :target: https://travis-ci.org/miki725/django-auxilium
    :alt: Build Status
.. image:: https://coveralls.io/repos/miki725/django-auxilium/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/miki725/django-auxilium?branch=master
    :alt: Coverage

* Free software: MIT license
* GitHub: https://github.com/miki725/django-auxilium
* Documentation: http://django-auxilium.readthedocs.org/

About
-----

Django Auxilium is a set of utilities packages as a Django app which
help working with Django. The word "auxilium" means help in Latin.
How this project came about is because I used to have an app for each
of my Django projects called ``core`` or ``common`` where I kept all of my
utility methods and classes, but after doing a couple of projects,
maintaining the same folder within all of the project became non-productive,
hence I refactored it into a separate reusable package.

Docs
----

For some of the highlights about the library and the most useful features
you are encouraged to take a look at the documentation, particularly
`Highlights <http://django-auxilium.readthedocs.org/en/latest/highlights.html>`_ document.

Installation
------------

Easiest way to install is by using ``pip``::

    $ pip install django-auxilium

If you want to install from source code, you can also install using setup tools::

    $ python setup.py install

Tests
-----

Before running tests you need to install all test dependencies::

    $ pip install -r requirements-dev.txt
    # or
    $ make install

Then to run tests you can use ``Makefile``::

    $ make test

.. note::
    This library uses both functional and doctests
