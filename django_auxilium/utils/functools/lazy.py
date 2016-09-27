from __future__ import print_function

import six
from django.utils.functional import Promise

from django_auxilium.utils.functools import Decorator


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
"""
The list of special methods is compiled from
`<http://code.activestate.com/recipes/496741-object-proxying/>`_
"""


class LazyWrapperMeta(type(Promise)):
    """
    Metaclass for ``LazyWrapper``

    The reason we need metaclass is because we need to customize
    some magic methods for ``LazyWrapper`` for particular
    types while creating class which is what metaclasses are for!

    This metaclass expects all subclasses of ``LazyWrapper``
    to supply ``possible_types`` attribute which this
    metaclass will use to customize the created class.
    """

    def __new__(mcs, name, bases, attrs):
        _super = super(LazyWrapperMeta, mcs).__new__

        try:
            LazyWrapper

        except NameError:
            # defining LazyWrapper itself
            return _super(mcs, name, bases, attrs)

        else:
            possible_types = attrs.pop('possible_types')

            name += str('({})'.format(i.__name__ for i in possible_types))
            attrs.update(mcs._make_proxy_methods(possible_types))

            return _super(mcs, name, bases, attrs)

    @classmethod
    def _make_proxy_methods(mcs, possible_types):
        """
        Helper method for creating magic methods for proxy class
        for specific ``possible_types``.

        This is necessary because all magic methods of specified
        ``possible_types`` need to be replaced and since different data-types
        in Python implement different magic methods, we need to construct
        a dedicated class for each of the types and cannot simply
        reuse ``LazyWrapper`` itself.

        See Also
        --------
        _make_proxy_method
            That method explains in more detail why private magic
            methods need to be replaced.
        """
        methods = {}

        for t in possible_types:
            for name in SPECIAL_METHODS:
                if hasattr(t, name) and name not in methods:
                    methods[name] = mcs._make_proxy_method(name)

        return methods

    @staticmethod
    def _make_proxy_method(name):
        """
        This static method helps to create magic proxy methods
        which need to be overwritten on the proxy lazy class object.

        This is necessary because not all Python operations
        call ``__getattribute__``. For example doing ``print(obj)``
        never calls ``obj.__getattribute__('__str__')``
        but directly gets ``__str__`` which it then calls.
        Therefore simply overwriting ``__getattribute__``
        cant make objects lazy for all of the Python built-in
        operations and so the only solution is to explicitly
        replace such magic methods with versions which will
        evaluate lazy object first.
        """
        def method(self, *args, **kwargs):
            self._lazy_compute()
            return getattr(self._lazy_value, name)(*args, **kwargs)

        method.__name__ = str(name)
        return method


class LazyWrapper(six.with_metaclass(LazyWrapperMeta, Promise)):
    """
    Wrapper class for lazy objects as returned by the :py:class:`LazyDecorator`

    The job of this wrapper is to **not** execute the inner
    function to get the result until absolutely necessary.
    For example simply storing a variable will not trigger
    inner function to be executed until something is done
    with the variable such as printing it, etc.

    Parameters
    ----------
    f : def
        Function which this lazy object wraps
    args : tuple
        Tuple of arguments which were passed to the
        function for execution
    kwargs : dict
        Dict of keyword arguments which were passed to the
        function for execution
    """

    def __init__(self, f, args, kwargs):
        self._lazy_func = f
        self._lazy_args = args
        self._lazy_kwargs = kwargs
        self._lazy_value = None

    def _lazy_compute(self):
        """
        Compute the wrapped function and replace this method
        with noop so that future executions are fast
        """
        self._lazy_value = self._lazy_func(*self._lazy_args, **self._lazy_kwargs)
        self._lazy_computed = True
        self._lazy_compute = lambda: True

    def __getattribute__(self, name):
        """
        This method returns only lazy attributes from ``self``
        and for everything else returns attribute from the
        computed lazy object.
        """
        def get(x):
            return object.__getattribute__(self, x)

        # retrieve lazy attributes as normal
        if name.startswith('_lazy_'):
            return get(name)

        # get the attribute from the computed value
        get('_lazy_compute')()
        return get('_lazy_value').__getattribute__(name)

    def __setattr__(self, name, val):
        """
        This method allows to set lazy attributes on ``self``
        and for everything else sets them on computed
        lazy value.
        """
        # set lazy attributes normally
        if name.startswith('_lazy_'):
            object.__setattr__(self, name, val)

        else:
            self._lazy_compute()
            setattr(self._lazy_value, name, val)


class LazyDecorator(Decorator):
    """
    Lazy evaluation decorator.

    Parameters
    ----------
    types : tuple, list
        Iterable of possible output data-types of the output of the input function

    Examples
    --------

    ::

        >>> lazy = LazyDecorator

        >>> @lazy([six.string_types, int])
        ... def a(bar):
        ...   print('invoking a with {0}'.format(bar))
        ...   if isinstance(bar, int):
        ...       return bar + 5
        ...   else:
        ...       return bar + 'foo'

        >>> l = a('bar')
        >>> isinstance(l, six.string_types)
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
    def __init__(self, types):
        self.types = self.get_possible_types(types)
        self.lazy_wrapper_class = self.get_lazy_wrapper_class()

    def get_possible_types(self, possible_types):
        """
        Get possible types as a list

        Parameters
        ----------
        possible_types : list, any
            Either a list of possible types or a single possible type

        Returns
        -------
        list
            List of possible types. If the input ``possible_types``
            was given as a single possible types, a list
            with a single item is returned.
        """
        return possible_types if isinstance(possible_types, (list, tuple)) else [possible_types]

    def get_lazy_wrapper_class(self):
        """
        Construct lazy wrapper class for the given possible types

        Returns
        -------
        type
            Lazy wrapper class specifically made for the
            possible types
        """
        return type(
            str('LazyWrapper'),
            (LazyWrapper,),
            {'possible_types': self.types}
        )

    def get_wrapped_object(self):
        """
        Get the wrapped callable which instead of computing
        values right away returns a lazy wrapper.
        """
        def wrapper(*args, **kwargs):
            return self.lazy_wrapper_class(self.to_wrap, args, kwargs)

        return wrapper


lazy = LazyDecorator


def flazy(f, possible_types):
    """
    Wrapper function for the :py:class:`LazyDecorator`

    It has the same API as Django's ``lazy`` function so the same code can be reused
    with this decorator if necessary.

    Examples
    --------

    ::

        >>> def f():
        ...     print('inside f')
        ...     return 5
        >>> g = flazy(f, int)
        >>> h = g()
        >>> print(str(h))
        inside f
        5
    """
    return LazyDecorator(possible_types)(f)
