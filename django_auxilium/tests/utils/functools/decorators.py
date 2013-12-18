from __future__ import unicode_literals, print_function
from functools import WRAPPER_ASSIGNMENTS
from django.test import TestCase
from django_auxilium.utils.functools.decorators import (Decorator, HybridDecorator,
                                                        Cache, Memoize)


class DecoratorTest(TestCase):
    def test_validate_parameter_config(self):
        """
        Make sure ``validate_parameter_config`` validates the parameters config
        """
        d = Decorator()

        d.PARAMETERS = ('foo', '*foo')
        with self.assertRaisesMessage(SyntaxError, 'Cannot redefine the same parameter'):
            d.validate_parameter_config()

        d.PARAMETERS = ('foo*',)
        with self.assertRaisesMessage(SyntaxError, 'Invalid identifier name "foo*"'):
            d.validate_parameter_config()

        for p in ['*foo', '**foo']:
            d.PARAMETERS = (p,)
            self.assertEqual(d.validate_parameter_config(), None)

        d.PARAMETERS = ('foo', '*bar', 'cat',)
        m = '*args or **kwargs cannot be before regular parameters'
        with self.assertRaisesMessage(SyntaxError, m):
            d.validate_parameter_config()

        d.PARAMETERS = ('foo', 'bar', '**cat', '*dog')
        m = '*args have to be before **kwargs'
        with self.assertRaisesMessage(SyntaxError, m):
            d.validate_parameter_config()

        d.PARAMETERS = ('foo', 'bar', '*cat', '**dog')
        self.assertEqual(d.validate_parameter_config(), None)

        d.DEFAULTS = {'snake': None}
        m = 'Defaults must be defined in parameters attribute'
        with self.assertRaisesMessage(SyntaxError, m):
            d.validate_parameter_config()

        d.DEFAULTS = {'*cat': None}
        m = 'Invalid syntax for default parameter'
        with self.assertRaisesMessage(SyntaxError, m):
            d.validate_parameter_config()

        d.DEFAULTS = {'foo': None}
        m = 'Optional parameter before required parameter'
        with self.assertRaisesMessage(SyntaxError, m):
            d.validate_parameter_config()

        d.DEFAULTS = {'bar': None}
        self.assertEqual(d.validate_parameter_config(), None)

    def test_get_parameters(self):
        """
        Make sure ``get_parameters`` properly parses the given parameters
        """
        d = Decorator()
        with self.assertRaisesMessage(TypeError, 'Too many arguments'):
            d.get_parameters(*('foo',))
        d.PARAMETERS = ('foo',)
        self.assertEqual(d.get_parameters(*('foo',)), {'foo': 'foo'})
        d.DEFAULTS = {'foo': 'bar'}
        self.assertEqual(d.get_parameters(), {'foo': 'bar'})

        d = Decorator()
        with self.assertRaisesMessage(TypeError, 'Too many arguments'):
            d.get_parameters(**{'foo': 'bar'})
        d.PARAMETERS = ('foo',)
        self.assertEqual(d.get_parameters(**{'foo': 'bar'}), {'foo': 'bar'})
        d.DEFAULTS = {'foo': 'bar'}
        self.assertEqual(d.get_parameters(), {'foo': 'bar'})

        d = Decorator()
        d.PARAMETERS = ('foo',)
        with self.assertRaisesMessage(TypeError, '"foo" argument is not provided'):
            d.get_parameters()

        d = Decorator()
        d.PARAMETERS = ('foo',)
        with self.assertRaisesMessage(SyntaxError, '"foo" parameter is repeated'):
            d.get_parameters(*('foo',), **{'foo': 'foo'})

    def test_set_parameters(self):
        """
        Make sure ``set_parameters`` sets the output of ``get_parameters`` to
        ``parameters`` attribute.
        """
        d = Decorator()
        d.get_parameters = lambda a: a

        for i in range(5):
            d.set_parameters(i)
            self.assertEqual(d.parameters, i)

    def test_get_wrapped_object(self):
        """
        Make sure in ``Decorator``, ``get_wrapped_object`` returns the input.
        """
        d = Decorator()
        for i in range(5):
            d.to_wrap = i
            self.assertEqual(d.get_wrapped_object(), i)

    def test_to_decorator(self):
        """
        Make sure ``to_decorator`` normalizes the wrapper
        """
        d = Decorator.to_decorator()

        def f():
            pass

        self.assertTrue(f is d(f))
        self.assertTrue(f is d()(f))

        class F(object):
            pass

        self.assertTrue(F is d(F))
        self.assertTrue(F is d()(F))

    def test_wraps(self):
        """
        Make sure the decorator correctly wraps the input function by
        preserving private attributes like ``__doc__``.
        """

        class D(Decorator):
            def get_wrapped_object(self):
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

    def test_wrapping_classes(self):
        """
        Python's ``functools.wraps`` can't wrap classes. This method tests how classes
        are wrapped.
        """

        class Foo(object):
            pass

        d = Decorator.to_decorator()
        d(Foo)
        self.assertTrue(True)


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
            def get_wrapped_object(self):
                return super(D, self).get_wrapped_object()

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

    def test_is_in_class_with_decorator(self):
        class Foo(HybridDecorator):
            def get_wrapped_object(self):
                obj = super(Foo, self).get_wrapped_object()
                obj.decorator = self
                return obj

        d = Foo().to_decorator()

        @d()
        def f():
            return 'bar'

        self.assertFalse(f.decorator.in_class)

        def f():
            return 'bar'

        f = d()(f)

        self.assertFalse(f.decorator.in_class)

        @d
        def f():
            return 'bar'

        self.assertFalse(f.decorator.in_class)

        def f():
            return 'bar'

        f = d(f)

        self.assertFalse(f.decorator.in_class)

        class Bar(object):
            @d()
            def foo(self):
                return 'foo'

        self.assertTrue(Bar.foo.decorator.in_class)

        class Bar(object):
            @d
            def foo(self):
                return 'foo'

        self.assertTrue(Bar.foo.decorator.in_class)


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

        self.assertTrue(getattr(foo, '_foo') is d.get_cache(foo))

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

    def test_get_wrapped_object(self):
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
        d.parameters['recompute'] = True
        self.assertEqual(foo.f(), foo.values[1])
        d.parameters['recompute'] = False
        d.parameters['recompute_parameter'] = 'bar'
        self.assertEqual(foo.f(bar=True), foo.values[2])

        # is_cached
        self.assertTrue(getattr(foo.f, d.parameters['is_cached']))
        d = Cache()
        d.parameters['is_cached'] = 'hello'
        Foo, foo = prepare(d)
        foo.f()
        self.assertTrue(getattr(Foo.f, 'hello'))

        # cache_attr
        self.assertTrue(hasattr(foo.f, d.parameters['cache_attr']))
        d = Cache()
        d.parameters['cache_attr'] = 'hello'
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

        self.assertFalse('(5,){}' in getattr(foo, '_foo'))
        self.assertFalse(d.in_cache(getattr(foo, '_foo'), foo, 5))
        foo.foo(5)
        self.assertTrue('(5,){}' in getattr(foo, '_foo'))
        self.assertTrue(d.in_cache(getattr(foo, '_foo'), foo, 5))

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
