from functools import WRAPPER_ASSIGNMENTS
from django.test import TestCase
from django_auxilium.utils.functools.decorators import (Decorator, HybridDecorator,
                                                        Cache, Memoize)


class DecoratorTest(TestCase):
    def test_set_kwargs(self):
        """
        Make sure the ``set_kwargs`` properly sets the ``ARGUMENTS`` attribute.
        """
        keys = ['foo', 'bar', 'hello', 'world']
        defaults = keys[:]
        values = keys[::-1]

        # if not ARGUMENTS, then kwargs should be empty
        d = Decorator()
        d.set_kwargs(dict(zip(keys, values)))
        self.assertEqual(d.kwargs, {})

        d.ARGUMENTS = dict(zip(keys, defaults))
        d.set_kwargs(dict(zip(keys, values)))
        self.assertEqual(d.kwargs, dict(zip(keys, values)))

    def test_get_wrapped_f(self):
        """
        Make sure in ``Decorator``, ``get_wrapped_f`` returns the input.
        """
        d = Decorator()
        for i in range(5):
            self.assertEqual(d.get_wrapped_f(i), i)

    def test_to_decorator(self):
        """
        Make sure ``to_decorator`` normalizes the wrapper
        """
        d = Decorator.to_decorator()

        def f():
            pass

        self.assertTrue(f is d(f))
        self.assertTrue(f is d()(f))

    def test_wraps(self):
        """
        Make sure the decorator correctly wraps the input function by
        preserving private attributes like ``__doc__``.
        """
        class D(Decorator):
            def get_wrapped_f(self, f):
                return lambda a: a

        d = D.to_decorator()

        def f():
            """
            Foo here
            """
            pass

        g = d(f)
        h = d()(f)

        for i in WRAPPER_ASSIGNMENTS:
            self.assertNotEqual(f, g)
            self.assertNotEqual(f, h)
            self.assertEqual(getattr(f, i), getattr(g, i))
            self.assertEqual(getattr(f, i), getattr(h, i))

    def test_call(self):
        """
        Make sure ``__call__`` returns the output of the wrapped function
        """
        d = Decorator()

        def f():
            return 'foo'
        g = d(f)

        self.assertEqual(f(), g())
        self.assertEqual(f, d.to_wrap)


class HybridDecoratorTest(TestCase):
    def test_is_in_class(self):
        """
        Make sure that ``is_in_class`` correctly determines it's output.

        Since that method builds on top of ``inspect.frames()``, the only way
        to test it is to use the decorator in full.
        That method by itself cannot be tested.
        """
        d = HybridDecorator()

        class Foo(object):
            @d
            def foo(self):
                return 'foo'

        self.assertTrue(d.in_class)

        # --------------------------------

        class D(HybridDecorator):
            pass
        d = D()

        class Foo(object):
            @d
            def foo(self):
                return 'foo'

        self.assertTrue(d.in_class)

        # --------------------------------

        class D(HybridDecorator):
            def get_wrapped_f(self, f):
                return super(D, self).get_wrapped_f(f)
        d = D()

        class Foo(object):
            @d
            def foo(self):
                return 'foo'

        self.assertTrue(d.in_class)

        # --------------------------------

        d = HybridDecorator()

        @d
        def f():
            return 'bar'

        self.assertFalse(d.in_class)


class CacheTest(TestCase):
    def test_init_cache(self):
        """
        Make sure the cache is initialized properly for both class and non-class methods.
        """
        d = Cache()

        @d
        def f():
            return 'foo'

        self.assertTrue(hasattr(d, 'cache'))

        # ----------------------------------

        d = Cache()

        class Foo(object):
            @d
            def foo(self):
                return 'bar'
        foo = Foo()

        self.assertFalse(hasattr(d, 'cache'))
        self.assertFalse(hasattr(Foo, '_foo'))
        self.assertFalse(hasattr(foo, '_foo'))
        foo.foo()
        self.assertTrue(hasattr(foo, '_foo'))

    def test_get_cache(self):
        """
        Make sure the correct cache object is returned
        """
        d = Cache()

        def f():
            return 'foo'
        d(f)

        self.assertTrue(d.cache is d.get_cache(f))

        # ----------------------------------

        d = Cache()

        class Foo(object):
            @d
            def foo(self):
                return 'bar'
        foo = Foo()
        foo.foo()

        self.assertTrue(foo._foo is d.get_cache(foo))

    def test_in_cache(self):
        """
        Make sure it is determined correctly if the cache was computed previously
        """
        d = Cache()

        def f():
            return 'foo'
        g = d(f)

        self.assertFalse(d.in_cache(d.cache, f))
        g()
        self.assertTrue(d.in_cache(d.cache, f))

    def test_to_cache(self):
        """
        Make sure the value is written correctly to the cache
        """
        d = Cache()

        def f():
            return 'foo'
        g = d(f)

        d.to_cache(d.cache, 'bar', f)
        self.assertEqual(g(), 'bar')

        # ----------------------------------

        d = Cache()

        class Foo(object):
            @d
            def foo(self):
                return 'bar'
        foo = Foo()

        d.to_cache(None, 'hello', foo)
        self.assertEqual(foo.foo(), 'hello')

    def test_from_cache(self):
        """
        Make sure the cache is returned
        """
        d = Cache()

        for i in range(5):
            self.assertEqual(d.from_cache(i), i)

    def test_get_wrapped_f(self):
        """
        Make sure the cached value is returned instead recomputing it
        """

        d = Cache()

        def prepare(d):
            class Foo(object):
                def __init__(self):
                    self.i = 0
                    self.values = ['foo', 'bar', 'hello']

                @d
                def f(self):
                    v = self.values[self.i]
                    self.i += 1
                    return v

            foo = Foo()

            return Foo, foo

        Foo, foo = prepare(d)

        # cache is looked up
        self.assertEqual(foo.f(), foo.values[0])
        self.assertEqual(foo.f(), foo.values[0])

        # recompute
        foo.i = 0
        self.assertEqual(foo.f(recompute=True), foo.values[0])
        d.kwargs['recompute'] = True
        self.assertEqual(foo.f(), foo.values[1])
        d.kwargs['recompute'] = False
        d.kwargs['recompute_parameter'] = 'bar'
        self.assertEqual(foo.f(bar=True), foo.values[2])

        # is_cached
        self.assertTrue(getattr(foo.f, d.kwargs['is_cached']))
        d = Cache()
        d.kwargs['is_cached'] = 'hello'
        Foo, foo = prepare(d)
        foo.f()
        self.assertTrue(getattr(Foo.f, 'hello'))

        # cache_attr
        self.assertTrue(hasattr(foo.f, d.kwargs['cache_attr']))
        d = Cache()
        d.kwargs['cache_attr'] = 'hello'
        Foo, foo = prepare(d)
        foo.f()
        self.assertTrue(hasattr(Foo.f, 'hello'))


class MemoizeTest(TestCase):
    def test_in_cache(self):
        """
        Make sure it is determined correctly if the cache was computed previously
        """
        d = Memoize()

        def f(a):
            return a
        g = d(f)

        self.assertFalse('(5,){}' in d.cache)
        self.assertFalse(d.in_cache(d.cache, 5))
        g(5)
        self.assertTrue('(5,){}' in d.cache)
        self.assertTrue(d.in_cache(d.cache, 5))

        d = Memoize()

        class Foo(object):
            @d
            def foo(self, a):
                return a
        foo = Foo()
        foo.foo(4)

        self.assertFalse('(5,){}' in foo._foo)
        self.assertFalse(d.in_cache(foo._foo, foo, 5))
        foo.foo(5)
        self.assertTrue('(5,){}' in foo._foo)
        self.assertTrue(d.in_cache(foo._foo, foo, 5))

    def test_from_cache(self):
        """
        Make sure tha the correct value is returned
        """
        d = Memoize()

        def f(a):
            return a
        g = d(f)

        g(5)

        self.assertTrue(d.in_cache(d.cache, 5))
        self.assertEqual(d.from_cache(d.cache, 5), 5)

    def test_to_cache(self):
        """
        Make sure the value is written correctly to the cache
        """
        d = Memoize()

        def f(a):
            return a
        d(f)

        self.assertFalse('(5,){}' in d.cache)
        self.assertFalse(d.in_cache(d.cache, 5))
        d.to_cache(d.cache, 5, 5)
        self.assertTrue('(5,){}' in d.cache)
