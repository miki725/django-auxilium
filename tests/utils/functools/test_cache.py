from __future__ import absolute_import, print_function
import types
from functools import partial

import pytest

from django_auxilium.utils.functools.cache import (
    CacheDecorator,
    CacheDescriptor,
    Caching,
    MemoizeDecorator,
    MemoizeDescriptor,
    Memoizing,
    NotInCache,
)


class Bunch(object):
    pass


class TestCaching(object):
    def setup_method(self, method):
        self.object = Bunch()
        self.cache = Caching(self.object, 'cache')

    def test_get_not_present(self):
        with pytest.raises(NotInCache):
            self.cache.get()

    def test_get_present(self):
        self.object.cache = 'foo'

        assert self.cache.get() == 'foo'

    def test_delete_not_present(self):
        with pytest.raises(NotInCache):
            self.cache.delete()

    def test_delete_present(self):
        self.object.cache = 'foo'

        assert self.cache.delete() == 'foo'
        assert not hasattr(self.object, 'cache')

    def test_set(self):
        assert self.cache.set('foo') == 'foo'
        assert self.object.cache == 'foo'


class TestMemoizing(object):
    def setup_method(self, method):
        self.object = Bunch()
        self.cache = Memoizing(self.object, 'cache')
        self.key = "('foo',)[]"

    def test_get_key(self):
        assert self.cache._get_key('foo') == "('foo',)[]"
        assert self.cache._get_key('foo', 'bar') == "('foo', 'bar')[]"
        assert self.cache._get_key(foo='bar') == "()[('foo', 'bar')]"
        assert self.cache._get_key(foo='bar', hello='there') == "()[('foo', 'bar'), ('hello', 'there')]"
        assert self.cache._get_key('foo', foo='bar') == "('foo',)[('foo', 'bar')]"

    def test_get_not_present(self):
        with pytest.raises(NotInCache):
            self.cache.get('foo')

    def test_get_present(self):
        self.object.cache = {self.key: 'foo'}

        assert self.cache.get('foo') == 'foo'

    def test_delete_not_present(self):
        with pytest.raises(NotInCache):
            self.cache.delete()

    def test_delete_present(self):
        self.object.cache = {self.key: 'foo'}

        assert self.cache.delete('foo') == 'foo'
        assert self.object.cache == {}

    def test_set(self):
        assert self.cache.set('foo', 'foo') == 'foo'
        assert self.object.cache == {self.key: 'foo'}


class TestCacheDescriptor(object):
    def setup_method(self, method):
        def bar(self):
            """
            hello world
            """
            return 'bar'

        class Foo(object):
            foo = CacheDescriptor(bar)

        self.bar = bar
        self.klass = Foo
        self.instance = Foo()
        self.descriptor = Foo.__dict__['foo']

    def test_init(self):
        assert self.descriptor.method is self.bar
        assert self.descriptor.cache_class is Caching
        assert not self.descriptor.as_property
        assert self.descriptor.cache_attribute.startswith('bar_cache_')

    def test_get_cache(self):
        actual = self.descriptor.get_cache(self.instance)

        assert isinstance(actual, Caching)
        assert actual.parent is self.instance
        assert actual.attr == self.descriptor.cache_attribute

    def test_getter_cache_present(self):
        setattr(self.instance, self.descriptor.cache_attribute, 'haha')

        actual = self.descriptor.getter(self.instance)

        assert actual == 'haha'
        assert hasattr(self.instance, self.descriptor.cache_attribute)
        assert getattr(self.instance, self.descriptor.cache_attribute) == 'haha'

    def test_getter_cache_not_present(self):
        assert not hasattr(self.instance, self.descriptor.cache_attribute)

        actual = self.descriptor.getter(self.instance)

        assert actual == 'bar'
        assert hasattr(self.instance, self.descriptor.cache_attribute)
        assert getattr(self.instance, self.descriptor.cache_attribute) == 'bar'

    def test_pop_cache_present(self):
        setattr(self.instance, self.descriptor.cache_attribute, 'haha')

        actual = self.descriptor.pop(self.instance)

        assert actual == 'haha'
        assert not hasattr(self.instance, self.descriptor.cache_attribute)

    def test_pop_cache_not_present(self):
        assert not hasattr(self.instance, self.descriptor.cache_attribute)

        with pytest.raises(NotInCache):
            self.descriptor.pop(self.instance)

    def test_get_class(self):
        assert self.klass.foo is self.bar

    def test_get_instance(self):
        assert isinstance(self.instance.foo, partial)
        assert isinstance(self.instance.foo.func, types.MethodType)
        assert self.instance.foo.func.__self__ is self.instance

        assert isinstance(self.instance.foo.pop, partial)
        assert isinstance(self.instance.foo.pop.func, types.MethodType)
        assert self.instance.foo.pop.func.__self__ is self.instance

        assert self.instance.foo.__doc__ == self.bar.__doc__

        assert self.instance.foo() == 'bar'

    def test_delete(self):
        with pytest.raises(AttributeError):
            del self.instance.foo

    def test_get_class_property(self):
        self.descriptor.as_property = True

        assert self.klass.foo is self.descriptor

    def test_get_instance_property(self):
        self.descriptor.as_property = True

        assert self.instance.foo == 'bar'

    def test_set_read_only_method(self):
        self.descriptor.as_property = False

        with pytest.raises(AttributeError):
            self.instance.foo = 'foo'

    def test_set_writable_property(self):
        self.descriptor.as_property = True

        self.instance.foo = 'foo'

        assert self.instance.foo == 'foo'

    def test_delete_property_not_present(self):
        self.descriptor.as_property = True

        with pytest.raises(NotInCache):
            del self.instance.foo

    def test_delete_property_present(self):
        self.descriptor.as_property = True
        setattr(self.instance, self.descriptor.cache_attribute, 'haha')

        del self.instance.foo

        assert not hasattr(self.instance, self.descriptor.cache_attribute)


class TestMemoizeDescriptor(object):
    def setup_method(self, method):
        def bar(self, a):
            """
            hello world
            """
            return 'bar'

        class Foo(object):
            foo = MemoizeDescriptor(bar)

        self.bar = bar
        self.klass = Foo
        self.instance = Foo()
        self.descriptor = Foo.__dict__['foo']

    def test_init(self):
        assert self.descriptor.method is self.bar
        assert self.descriptor.cache_class is Memoizing
        assert self.descriptor.cache_attribute.startswith('bar_memoize_')


class TestCacheDecorator(object):
    def test_function(self):
        self.counter = 0

        @CacheDecorator()
        def foo():
            self.counter += 1
            return self.counter

        assert isinstance(foo.decorator, CacheDecorator)
        assert isinstance(foo.decorator.cache, Caching)
        assert foo.decorator.cache.parent is foo.decorator
        assert foo.decorator.cache.attr == 'cached_value'

        assert hasattr(foo, 'pop')
        assert foo.pop.__self__ is foo.decorator

        assert foo() == 1
        assert foo() == 1
        assert foo.pop() == 1
        assert foo() == 2

    def test_method(self):
        class Foo(object):
            def __init__(self):
                self.counter = 0

            @CacheDecorator()
            def foo(self):
                self.counter += 1
                return self.counter

        descriptor = Foo.__dict__['foo']

        assert isinstance(descriptor, CacheDescriptor)
        assert not descriptor.as_property

    def test_property(self):
        class Foo(object):
            def __init__(self):
                self.counter = 0

            @CacheDecorator(as_property=True)
            def foo(self):
                self.counter += 1
                return self.counter

        descriptor = Foo.__dict__['foo']

        assert isinstance(descriptor, CacheDescriptor)
        assert descriptor.as_property


class TestMemoizeDecorator(object):
    def test_function(self):
        self.counter = 0

        @MemoizeDecorator()
        def foo(a):
            self.counter += 1
            return self.counter

        assert isinstance(foo.decorator, MemoizeDecorator)
        assert isinstance(foo.decorator.cache, Memoizing)
        assert foo.decorator.cache.parent is foo.decorator
        assert foo.decorator.cache.attr == 'cached_value'

        assert hasattr(foo, 'pop')
        assert foo.pop.__self__ is foo.decorator

        assert foo('a') == 1
        assert foo('b') == 2
        assert foo('a') == 1
        assert foo.pop('a') == 1
        assert foo('b') == 2
        assert foo('a') == 3

    def test_method(self):
        class Foo(object):
            def __init__(self):
                self.counter = 0

            @MemoizeDecorator()
            def foo(self, a):
                self.counter += 1
                return self.counter

        descriptor = Foo.__dict__['foo']

        assert isinstance(descriptor, MemoizeDescriptor)
        assert not descriptor.as_property
