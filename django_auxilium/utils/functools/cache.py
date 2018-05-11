from __future__ import print_function, unicode_literals
import abc
import types
from functools import partial, wraps

import six

from .decorators import HybridDecorator


class NotInCache(Exception):
    """
    Exception for when a value is not present in cache.

    Primary purpose of the exception is to normalize
    various exception types from different cache implementations.
    """


class BaseCache(six.with_metaclass(abc.ABCMeta, object)):
    """
    Base class for implementing cache implementations

    Parameters
    ----------
    parent : object
        A parent object where cache is stored
    attr : str
        Name of the attribute under which cache will be stored
        in the ``parent`` object
    """

    def __init__(self, parent, attr):
        self.parent = parent
        self.attr = attr

    def get(self, *args, **kwargs):
        """
        This method must be overwritten by subclasses which
        should return cache value

        ``args`` and ``kwargs`` are the parameters passed to
        the cached function and can be used by the method
        to extract the cache value from the ``parent`` object

        When cache value is not found, this method should raise
        :py:class:`NotInCache`
        """

    def set(self, value, *args, **kwargs):
        """
        This method must be overwritten by subclasses which
        should set the cache for the given parameters

        ``args`` and ``kwargs`` are the parameters passed to
        the cached function and can be used by the method
        to correctly store the cache value in the ``parent`` object
        """

    def delete(self, *args, **kwargs):
        """
        This method must be overwritten by subclasses which
        should delete cache value for the given parameters

        ``args`` and ``kwargs`` are the parameters passed to
        the cached function and can be used by the method
        to determine which cache value from the ``parent`` object
        to remove

        When cache value is not found, this method should raise
        :py:class:`NotInCache`
        """


class Caching(BaseCache):
    """
    Caching implementation which stores single cache value
    on the parent object

    The cache is simply stored on the given attribute.
    When the attribute is present on the ``parent`` object,
    that indicates that the cache was set and that value
    is used for cache. When not present, that means
    cache is missing and hence :py:class:`NotInCache` is raised
    in most use-cases.
    """

    def get(self, *args, **kwargs):
        """
        Get the cache value from the ``parent`` object

        Raises
        ------
        NotInCache
            When the cache is not set
        """
        try:
            return getattr(self.parent, self.attr)
        except AttributeError:
            raise NotInCache

    def set(self, value, *args, **kwargs):
        """
        Store the cache value on the ``parent`` object
        """
        setattr(self.parent, self.attr, value)
        return value

    def delete(self, *args, **kwargs):
        """
        Delete the cache value from the ``parent`` object

        Raises
        ------
        NotInCache
            When the cache is not set and so cannot be deleted
        """
        try:
            return self.parent.__dict__.pop(self.attr)
        except KeyError:
            raise NotInCache


class Memoizing(BaseCache):
    """
    Caching implementation which stores single cache value
    for a set of given parameters on the parent object
    hence is called memoization

    The cache is stored on the given attribute as a dictionary.
    Keys are string representations of the given parameters
    to the cached function and the values are their corresponding
    cache values. When the key is in the dictionary,
    that is used as cache value. Otherwise, in most cases
    :py:class:`NotInCache` is raised.
    """

    def _get_key(self, *args, **kwargs):
        return repr(args) + repr(sorted(kwargs.items()))

    def get(self, *args, **kwargs):
        """
        Get the cache value from the ``parent`` object
        by computing the key from the given parameters

        Raises
        ------
        NotInCache
            When the cache is not set
        """
        key = self._get_key(*args, **kwargs)
        try:
            return getattr(self.parent, self.attr)[key]
        except (AttributeError, TypeError, KeyError):
            raise NotInCache

    def set(self, value, *args, **kwargs):
        """
        Store the cache value on the ``parent`` object
        for the key as computed for the given parameters
        """
        key = self._get_key(*args, **kwargs)
        try:
            store = getattr(self.parent, self.attr)
        except AttributeError:
            store = {}
            setattr(self.parent, self.attr, store)
        store[key] = value
        return value

    def delete(self, *args, **kwargs):
        """
        Delete the cache value from the ``parent`` object
        for the key as computed by the given parameters

        Raises
        ------
        NotInCache
            When the cache is not set and so cannot be deleted
        """
        key = self._get_key(*args, **kwargs)
        try:
            return getattr(self.parent, self.attr).pop(key)
        except (AttributeError, TypeError, KeyError):
            raise NotInCache


class CacheDescriptor(object):
    """
    Cache descriptor to be used to add instance-level cache
    to class methods.

    .. note::
        This descriptor could be used independently (and there are
        even some examples below) however it is meant to be used
        along with :py:class:`CacheDecorator` which provides much
        cleaner API.

    Examples
    --------
    ::

        >>> def bar(self):
        ...     print('computing')
        ...     return 'bar'

        >>> class Foo(object):
        ...     foo = CacheDescriptor(bar)

        >>> f = Foo()
        >>> print(f.foo())
        computing
        bar
        >>> print(f.foo())
        bar
        >>> print(f.foo.pop())
        bar
        >>> print(f.foo())
        computing
        bar
        >>> f.foo.push('another value')
        >>> print(f.foo())
        another value

    Parameters
    ----------
    method : function
        Callable which this descriptor is meant to wrap and cache
    cache_class : type, optional
        Caching implementation cache which should be used to
        apply caching. By default :py:attr:`.default_cache_class` is used.
    as_property : bool, optional
        Whether to implement the descriptor as a property.
        By default it is ``False``.

        .. warning::
            This option as ``True`` can only be used with some
            caching implementations such as :py:class:`Caching`.
            Other implementations do not suppose this.
    """
    cache_attribute_pattern = '{name}_cache_{hash}'
    """
    String pattern for constructing the cache attribute
    name under which cache will be stored on the instance.
    This attribute is meant to be changed in subclasses
    to customize the functionality.
    """
    default_cache_class = Caching
    """
    Cache implementation class which will be used
    for the caching.
    This attribute is meant to be changed in subclasses
    to customize the functionality.
    """

    def __init__(self, method, cache_class=None, as_property=False):
        self.method = method
        self.cache_attribute = self.cache_attribute_pattern.format(
            name=method.__name__,
            hash=abs(hash(method.__name__)),
        )
        self.cache_class = cache_class or self.default_cache_class
        self.as_property = as_property

    def get_cache(self, instance):
        """
        Helper method which given returns cache implementation instance
        for the given instance with given parameters
        """
        return self.cache_class(instance, self.cache_attribute)

    def getter(self, instance, *args, **kwargs):
        """
        Wrapper method around the decorator-wrapped callable
        (``method`` parameter) which returns cache value when available
        or otherwise computes and stores the value in cache by evaluating
        wrapped method
        """
        cache = self.get_cache(instance)

        try:
            return cache.get(*args, **kwargs)
        except NotInCache:
            return cache.set(self.method(instance, *args, **kwargs), *args, **kwargs)

    def pop(self, instance, *args, **kwargs):
        """
        Method for popping cache value corresponding to the given
        parameters from the instance as implemented by the
        caching implementation
        """
        cache = self.get_cache(instance)
        return cache.delete(*args, **kwargs)

    def push(self, instance, value, *args, **kwargs):
        """
        Method for setting custom cache value given function parameters
        """
        cache = self.get_cache(instance)
        cache.set(value, *args, **kwargs)

    def _wrap(self, wrapping, proxy, instance):
        f = types.MethodType(proxy, instance)
        return wraps(wrapping)(partial(f))

    def __get__(self, instance, owner):
        if self.as_property:
            if instance is None:
                return self
            else:
                return self.getter(instance)

        else:
            if instance is None:
                return self.method
            else:
                f = self._wrap(self.method, self.getter, instance)
                f.pop = self._wrap(self.__class__.pop, self.pop, instance)
                f.push = self._wrap(self.__class__.push, self.push, instance)
                return f

    def __set__(self, instance, value):
        if self.as_property:
            cache = self.get_cache(instance)
            # no args and kwargs since this is only for case when cache is used as property
            return cache.set(value)

        # required to be overwritten for pypy
        # see https://bitbucket.org/pypy/pypy/issues/2033/attributeerror-object-attribute-is-read
        # even though ticket is resolved its still affecting pypy3
        raise AttributeError

    def __delete__(self, instance):
        if self.as_property:
            self.pop(instance)
        else:
            raise AttributeError


class MemoizeDescriptor(CacheDescriptor):
    """
    Cache descriptor to be used to add instance-level cache
    to class methods which considers method parameters
    when caching values.

    In other words, this descriptor caches method results
    per given parameters.

    .. note::
        This descriptor could be used independently (and there are
        even some examples below) however it is meant to be used
        along with :py:class:`MemoizeDecorator` which provides much
        cleaner API.

    Examples
    --------
    ::

        >>> def bar(self, x):
        ...     print('computing for', x)
        ...     return x + 'bar'

        >>> class Foo(object):
        ...     foo = MemoizeDescriptor(bar)

        >>> f = Foo()
        >>> print(f.foo('foo'))
        computing for foo
        foobar
        >>> print(f.foo('awesome'))
        computing for awesome
        awesomebar
        >>> print(f.foo('foo'))
        foobar
        >>> print(f.foo.pop('foo'))
        foobar
        >>> print(f.foo('foo'))
        computing for foo
        foobar
        >>> print(f.foo('awesome'))
        awesomebar
    """
    cache_attribute_pattern = '{name}_memoize_{hash}'
    """
    String pattern for constructing the cache attribute
    name under which cache will be stored on the instance.
    This attribute is meant to be changed in subclasses
    to customize the functionality.
    """
    default_cache_class = Memoizing
    """
    Cache implementation class which will be used
    for the caching.
    This attribute is meant to be changed in subclasses
    to customize the functionality.
    """


class BaseCacheDecorator(HybridDecorator):
    """
    Base decorator for caching callables so that they only execute once
    and all subsequent calls return cached value

    This is very useful for expensive functions
    """
    cache_descriptor_class = None
    """
    Descriptor class to be used when caching is applied to class methods.
    This attribute is meant to be changed in subclasses.
    """
    cache_class = Caching
    """
    Caching implementation to use when wrapping standalone functions.
    This attribute is meant to be changed in subclasses.
    """

    def get_cache_descriptor(self):
        """
        Hook for instantiating cache descriptor class
        """
        return self.cache_descriptor_class(self.to_wrap)

    def get_wrapped_object(self):
        """
        Main method for wrapping the given object.

        This method has separate code paths for the following scenarios:

        :class method:
            When wrapping class method descriptor is returned
            as created by :py:meth:`get_cache_descriptor`.
            That descriptor is then responsible for maintaining
            cache state for the class instance.
        :function:
            When wrapping standalone function, this method
            returns a wrapping function which caches the
            value on this decorator instance.
            That means that the cache becomes global
            since functions in Python are singletons.
        """
        to_wrap = super(BaseCacheDecorator, self).get_wrapped_object()

        if self.in_class:
            return self.get_cache_descriptor()

        else:
            self.cache = self.cache_class(self, 'cached_value')

            def wrapper(*args, **kwargs):
                try:
                    return self.cache.get(*args, **kwargs)
                except NotInCache:
                    return self.cache.set(to_wrap(*args, **kwargs), *args, **kwargs)

            wrapper.pop = self.pop
            wrapper.decorator = self
            return wrapper

    def pop(self, *args, **kwargs):
        """
        Method for popping cache value corresponding to the given parameters
        """
        return self.cache.delete(*args, **kwargs)


class CacheDecorator(BaseCacheDecorator):
    """
    Decorator for caching callables so that they only execute once
    and all subsequent calls return cached value.

    .. note::
        This caching decorator does not account function parameters
        to cache values. If you need to cache different calls
        per given parameters, please look at :py:class:`MemoizeDecorator`

    Examples
    --------

    When caching standalone functions::

        >>> @CacheDecorator.as_decorator()
        ... def compute():
        ...     print('computing here')
        ...     return 'foo'

        >>> print(compute())
        computing here
        foo
        >>> print(compute())
        foo

        >>> print(compute.pop())
        foo

        >>> print(compute())
        computing here
        foo

    When caching class methods::

        >>> class Foo(object):
        ...     @CacheDecorator.as_decorator()
        ...     def foo(self):
        ...         print('computing here')
        ...         return 'foo'

        >>> f = Foo()
        >>> print(f.foo())
        computing here
        foo
        >>> print(f.foo())
        foo

        >>> print(f.foo.pop())
        foo

        >>> print(f.foo())
        computing here
        foo

    Parameters
    ----------
    as_property : bool
        Boolean whether to create a property descriptor
        when using it on a class method

        .. warning::
            This is only meant to be used when the wrapping
            method does not accept any parameters since there
            is no way in Python to pass parameters to properties
    """
    cache_descriptor_class = CacheDescriptor
    """
    Descriptor class to be used when caching is applied to class methods
    """
    cache_class = Caching
    """
    Caching implementation to use when wrapping standalone functions.
    """

    def __init__(self, as_property=False, *args, **kwargs):
        self.as_property = as_property
        super(CacheDecorator, self).__init__(*args, **kwargs)

    def get_cache_descriptor(self):
        """
        Custom implementation for getting the cache descriptor
        which allows to use ``as_property`` parameter
        """
        return self.cache_descriptor_class(
            self.to_wrap, as_property=self.as_property,
        )


class MemoizeDecorator(BaseCacheDecorator):
    """
    Decorator for memoizing functions so that they only execute once
    and all subsequent calls with same parameters

    This is very useful for expensive functions which accept parameters

    Examples
    --------

    When caching standalone functions::

        >>> @MemoizeDecorator.as_decorator()
        ... def compute(x):
        ...     print('computing for', x)
        ...     return x + 'foo'

        >>> print(compute('bar'))
        computing for bar
        barfoo
        >>> print(compute('awesome'))
        computing for awesome
        awesomefoo
        >>> print(compute('bar'))
        barfoo

        >>> print(compute.pop('bar'))
        barfoo

        >>> print(compute('bar'))
        computing for bar
        barfoo
        >>> print(compute('awesome'))
        awesomefoo

    When caching class methods::

        >>> class Foo(object):
        ...     @MemoizeDecorator.as_decorator()
        ...     def foo(self, x):
        ...         print('computing for', x)
        ...         return x + 'foo'

        >>> f = Foo()
        >>> print(f.foo('bar'))
        computing for bar
        barfoo
        >>> print(f.foo('awesome'))
        computing for awesome
        awesomefoo

        >>> print(f.foo('bar'))
        barfoo
        >>> print(f.foo('awesome'))
        awesomefoo

        >>> print(f.foo.pop('bar'))
        barfoo

        >>> print(f.foo('bar'))
        computing for bar
        barfoo
        >>> print(f.foo('awesome'))
        awesomefoo
    """
    cache_descriptor_class = MemoizeDescriptor
    """
    Descriptor class to be used when caching is applied to class methods
    """
    cache_class = Memoizing
    """
    Caching implementation to use when wrapping standalone functions.
    """


cache = CacheDecorator.as_decorator()
memoize = MemoizeDecorator.as_decorator()
cache_property = CacheDecorator.as_decorator(as_property=True)
"""
Shortcut for :py:data:`cache` which automatically creates
properties when used on class methods.

These are equivalent::

    @cache(as_property=True)
    def foo(self): pass

    @cache_property
    def bar(self): pass
"""
cache_method = CacheDecorator.as_decorator(is_method=True)
"""
Shortcut for :py:data:`cache` which automatically indicates
that the cached object is a method.

These are equivalent::

    class Foo(object):
        @cache(is_method=True)
        def foo(self): pass

    class Foo(object):
        @cache_method
        def bar(self): pass
"""
