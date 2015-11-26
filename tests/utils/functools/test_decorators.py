from __future__ import print_function, unicode_literals
from functools import WRAPPER_ASSIGNMENTS

import mock
from django.test import TestCase

from django_auxilium.utils.functools.decorators import (
    Decorator,
    HybridDecorator,
)


class TestDecorator(object):
    def test_get_wrapped_object(self):
        """
        Make sure in ``Decorator``, ``get_wrapped_object`` returns the input.
        """
        d = Decorator()
        d.to_wrap = mock.sentinel.object

        assert d.get_wrapped_object() is mock.sentinel.object

    def test_as_decorator(self):
        """
        Make sure ``to_decorator`` normalizes the wrapper
        """
        d = Decorator.as_decorator()

        def f():
            pass

        assert f is d(f)
        assert f is d()(f)

        class F(object):
            pass

        assert F is d(F)
        assert F is d()(F)

    def test_wraps(self):
        """
        Make sure the decorator correctly wraps the input function by
        preserving private attributes like ``__doc__``.
        """

        class D(Decorator):
            def get_wrapped_object(self):
                return lambda a: a

        d = D.as_decorator()

        def f():
            """
            Foo here
            """
            pass

        g = d(f)
        h = d()(f)

        for i in WRAPPER_ASSIGNMENTS:
            assert f is not g
            assert f is not h
            assert getattr(f, i) == getattr(g, i)
            assert getattr(f, i) == getattr(h, i)

    def test_call(self):
        """
        Make sure ``__call__`` returns the output of the wrapped function
        """
        d = Decorator()

        def f():
            return 'foo'

        g = d(f)

        assert f() is g()
        assert f is d.to_wrap


class TestHybridDecorator(TestCase):
    def setup_method(self, method):
        self.decorator = HybridDecorator()

    def test_pre_wrap_function(self):
        def foo():
            pass

        self.decorator(foo)

        assert not self.decorator.in_class

    def test_pre_wrap_function_with_parameters(self):
        def foo(bar):
            pass

        self.decorator(foo)

        assert not self.decorator.in_class

    def test_pre_wrap_method(self):
        def foo(self):
            pass

        self.decorator(foo)

        assert self.decorator.in_class

    def test_pre_wrap_provided(self):
        def foo(self):
            pass

        self.decorator.is_method = True
        self.decorator(foo)

        assert self.decorator.in_class
