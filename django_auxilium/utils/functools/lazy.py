"""
lazy - Decorators and utilities for lazy evaluation in Python

The list of special methods is compiled from
http://code.activestate.com/recipes/496741-object-proxying/
"""

from __future__ import unicode_literals, print_function
from django.utils.functional import Promise
from django_auxilium.utils.functools import Decorator
import six


SPECIAL_METHODS = [
    '__abs__',
    '__add__',
    '__and__',
    '__call__',
    '__cmp__',
    '__coerce__',
    '__contains__',
    '__delitem__',
    '__delslice__',
    '__div__',
    '__divmod__',
    '__eq__',
    '__float__',
    '__floordiv__',
    '__ge__',
    '__getitem__',
    '__getslice__',
    '__gt__',
    '__hash__',
    '__hex__',
    '__iadd__',
    '__iand__',
    '__idiv__',
    '__idivmod__',
    '__ifloordiv__',
    '__ilshift__',
    '__imod__',
    '__imul__',
    '__int__',
    '__invert__',
    '__ior__',
    '__ipow__',
    '__irshift__',
    '__isub__',
    '__iter__',
    '__itruediv__',
    '__ixor__',
    '__le__',
    '__len__',
    '__long__',
    '__lshift__',
    '__lt__',
    '__mod__',
    '__mul__',
    '__ne__',
    '__neg__',
    '__oct__',
    '__or__',
    '__pos__',
    '__pow__',
    '__radd__',
    '__rand__',
    '__rdiv__',
    '__rdivmod__',
    '__reduce__',
    '__reduce_ex__',
    '__repr__',
    '__reversed__',
    '__rfloorfiv__',
    '__rlshift__',
    '__rmod__',
    '__rmul__',
    '__ror__',
    '__rpow__',
    '__rrshift__',
    '__rshift__',
    '__rsub__',
    '__rtruediv__',
    '__rxor__',
    '__setitem__',
    '__setslice__',
    '__str__',
    '__sub__',
    '__truediv__',
    '__unicode__',
    '__xor__',
    'next',
]


class LazyWrapper(Promise):
    """
    Wrapper class for lazy objects as returned by the lazy decorator below.
    """

    def __init__(self, pt, f, args, kwargs):
        self._lazy_func = f
        self._lazy_args = args
        self._lazy_kwargs = kwargs
        self._lazy_computed = False
        self._lazy_value = None

    def _lazy_compute(self):
        if not self._lazy_computed:
            self._lazy_value = self._lazy_func(*self._lazy_args, **self._lazy_kwargs)
            self._lazy_computed = True
            self._lazy_compute = lambda: True

    def __getattribute__(self, name):
        get = lambda x: object.__getattribute__(self, x)

        # retrieve lazy attributes as normal
        if name.startswith('_lazy_'):
            return get(name)

        # get the attribute from the computed value
        get('_lazy_compute')()
        return get('_lazy_value').__getattribute__(name)

    def __setattr__(self, name, val):
        # set lazy attributes normally
        if name.startswith('_lazy_'):
            object.__setattr__(self, name, val)

        else:
            self._lazy_compute()
            setattr(self._lazy_value, name, val)

    @classmethod
    def _lazy_proxy(cls, possible_types):
        def make_method(name):
            def method(self, *args, **kwargs):
                self._lazy_compute()
                return getattr(self._lazy_value, name)(*args, **kwargs)

            method.__name__ = str(name)
            return method

        namespace = {}
        for t in possible_types:
            for name in SPECIAL_METHODS:
                if hasattr(t, name) and name not in namespace:
                    namespace[name] = make_method(name)

        return type(str('{}({})'.format(cls.__name__,
                                        '|'.join([i.__name__ for i in possible_types]))),
                    (cls,), namespace)

    def __new__(cls, possible_types, *args, **kwargs):
        try:
            iter(possible_types)
            iterable = True
        except TypeError:
            iterable = False

        if not iterable:
            possible_types = [possible_types]

        klass = cls._lazy_proxy(possible_types)
        ins = object.__new__(klass)
        klass.__init__(ins, possible_types, *args, **kwargs)
        return ins


class LazyDecorator(Decorator):
    """
    Lazy evaluation decorator.

    Unfortunately in order to enable support for Python 3 in this decorator, this
    decorator has required parameters as described in parameters section. Even though
    that complicates the decorator's usage a bit however, it allows for support for
    Python 3 which is a bigger advantage.

    Parameters
    ----------
    types : tuple, list
        Iterable of possible output data-types of the output of the input function

    Examples
    --------

    ::

        >>> lazy = LazyDecorator

        >>> @lazy([six.text_type, int])
        ... def a(bar):
        ...   print('invoking a with {0}'.format(bar))
        ...   if isinstance(bar, int):
        ...       return bar + 5
        ...   else:
        ...       return bar + 'foo'

        >>> l = a('bar')
        >>> isinstance(l, six.text_type)
        invoking a with bar
        True
        >>> print(l)
        barfoo

        >>> l = a(5)
        >>> isinstance(l, int)
        invoking a with 5
        True
        >>> print(l)
        10
    """
    PARAMETERS = ('types',)

    def get_wrapped_object(self):
        def wrapper(*args, **kwargs):
            return LazyWrapper(self.parameters['types'], self.to_wrap, args, kwargs)

        return wrapper


lazy = LazyDecorator


def flazy(f, possible_types):
    """
    Wrapper function for the ``LazyDecorator``.

    It has the same API as Django's ``lazy`` function so the same code can be reused
    with this decorator if necessary.

    Examples
    --------

    ::

        >>> from django_auxilium.utils.functools import flazy as lazy

        >>> # old code
        >>> def f():
        ...     print('inside f')
        ...     return 5
        >>> g = lazy(f, int)

        >>> h = g()
        >>> print(h)
        inside f
        5
    """
    return LazyDecorator(possible_types)(f)
