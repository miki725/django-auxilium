"""
lazy - Decorators and utilities for lazy evaluation in Python
Alberto Bertogli (albertito@blitiri.com.ar) [http://blitiri.com.ar/git/r/pymisc/b/master/t/f=lazy.py.html]
"""

from functools import wraps


class _LazyWrapper:
    """
    Lazy wrapper class for the decorator defined below.
    It's closely related so don't use it.

    We don't use a new-style class, otherwise we would have to implement
    stub methods for __getattribute__, __hash__ and lots of others that
    are inherited from object by default. This works too and is simple.
    I'll deal with them when they become mandatory.
    """
    def __init__(self, f, args, kwargs):
        self._override = True
        self._isset = False
        self._value = None
        self._func = f
        self._args = args
        self._kwargs = kwargs
        self._override = False

    def _checkset(self):
        if not self._isset:
            self._override = True
            self._value = self._func(*self._args, **self._kwargs)
            self._isset = True
            self._checkset = lambda: True
            self._override = False

    def __getattr__(self, name):
        if self.__dict__['_override']:
            return self.__dict__[name]
        self._checkset()
        return self._value.__getattribute__(name)

    def __setattr__(self, name, val):
        if name == '_override' or self._override:
            self.__dict__[name] = val
            return
        self._checkset()
        setattr(self._value, name, val)
        return


def lazy(f):
    """
    Lazy evaluation decorator

    example usage:

    >>> @lazy
    ... def a(bar):
    ...   print "invoking a with {0}".format(bar)
    ...   return bar + "foo"

    >>> baz = a("foo")
    >>> baz
    invoking a with foo
    <lib.lazy_util._LazyWrapper instance at 0x7f6249c595a8>
    """
    @wraps(f)
    def newf(*args, **kwargs):
        return _LazyWrapper(f, args, kwargs)

    return newf
