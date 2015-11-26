from __future__ import absolute_import, print_function, unicode_literals

import six

from django_auxilium.utils.functools.lazy import LazyWrapper, flazy, lazy


class Foo(six.text_type):
    pass


def test_lazy():
    @lazy(six.text_type)
    def foo():
        return Foo('foo')

    f = foo()

    assert issubclass(type(f), LazyWrapper)
    assert f == 'foo'
    assert f.startswith('f')

    f.foo = 'hello'
    assert f.foo == 'hello'


def test_flazy():
    def _foo():
        return Foo('foo')

    foo = flazy(_foo, six.text_type)

    f = foo()

    assert issubclass(type(f), LazyWrapper)
    assert f == 'foo'
    assert f.startswith('f')

    f.foo = 'hello'
    assert f.foo == 'hello'
