Django Auxilium
===============

.. image:: https://travis-ci.org/miki725/django-auxilium.png?branch=develop
    :target: https://travis-ci.org/miki725/django-auxilium
    :alt: Build Status

About
-----

Django Auxilium is a set of utilities packages as a Django app which
help working in Django. The word Auxilium means help in Latin.
How this project came about is because I used to have an app for each
of my Django projects called ``data_structures`` where I kept all of my
utility methods and classes, but after doing a couple of projects,
maintaining the same folder within all of the project became non-productive,
hence I refactored it into a separate reusable package.

Requirements
------------

To install this package, the only dependency is Django itself. This dependency
is included in the ``setup.py``, hence if you install this package via ``pip``
like illustrated below, Django will be installed automatically if you don't have
it installed already.::

    pip install django-auxilium

To install `development <http://github.com/miki725/django-auxilium/archive/develop.tar.gz#egg=django_auxilium-dev>`_
version you can install via::

    pip install django-auxilium==dev

In order to run tests however, additional Python packages are required. You can
see the full list of all required packages in ``requirements.txt``. You can also
install all of them in one swoop via ``pip``::

    pip install -r requirements.txt

For instruction on how to run the test suite, please read the `Tests`_ section.

Installation
------------

Install
~~~~~~~

Install this library using ``pip``. As described in `Requirements`_, installing using
``pip`` will also install all necessary requirement::

    pip install django-auxilium

If you want to install from source code, you can also install using setup tools::

    python setup.py install

Add to ``INSTALLED_APPS``
~~~~~~~~~~~~~~~~~~~~~~~~~

In order to activate this app, add it to the ``INSTALLED_APPS`` within the Django's
``settings.py``::

    INSTALLED_APPS = (
        ... ,
        'django_auxilium',
        ...
    )

Tests
-----

The tests themselves are included as ``tests`` package within ``django_auxilium``
package as illustrated in the folder structure below::

    django_auxilium/
        django_auxilium/
            tests/             # tests package
                __init.py
            __init__.py
        setup.py
        requirements.py
        README.rst
        ...

This library uses both unittests and doctests. If it is installed into a Django
project (it's in the ``INSTALLED_APPS``), you can run the tests using the
``manage.py`` ``test`` command::

    python manage.py test django_auxilium

You can also run the tests independent of a Django project. For that, the test
runner includes bare minimum ``settings.py`` module which only sets required
settings to run the tests. The test runner uses
`django_nose <http://pypi.python.org/pypi/django-nose>`_ as well as
`coverage.py <http://nedbatchelder.com/code/coverage/>`_.
To run the test runner, just execute the ``runtests.sh`` script inside the
``tests`` folder::

    django_auxilium/
        django_auxilium/
            ...
        tests/
            settings.py        # bare settings.py necessary for Django
            runtests.sh        # test runner
        setup.py
        requirements.py
        README.rst
        ...

