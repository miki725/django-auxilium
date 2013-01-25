"""
Collection of simple utilities which modify some behaviour of funtions
"""

import copy
import inspect
from functools import wraps


class Decorator(object):
    """
    Class for implementing decorators capable of accepting optional keyword parameters.

    .. warning:: Currently, positional parameters are not supported

    This class generates a decorator function which properly wraps the given function
    by preserving it's private attributes like ``__doc__`` since it automatically utilizes
    ``functools.wraps`` method. Also if ``to_decorator`` is used, then the decorator can be
    used without initializing the class instance (see `examples`_).

    Examples
    --------

    >>> class D(Decorator):
    ...     ARGUMENTS = {'debug': False}
    ...     def get_wrapped_f(self, f):
    ...         def wrapped(*args, **kwargs):
    ...             print 'called wrapped with', args, kwargs
    ...             if self.kwargs['debug']:
    ...                 print 'debug here'
    ...             return f(*args, **kwargs)
    ...         return wrapped
    ...
    >>> decorator = D().to_decorator()

    >>> # not initialized (default values will be used if defined)
    >>> @decorator
    ... def sum(a, b):
    ...    return a + b

    >>> sum(5, 6)
    called wrapped with (5, 6) {}
    11

    >>> # initialized with no parameters (default values will be used if defined)
    >>> @decorator
    ... def sum(a, b):
    ...    return a + b

    >>> sum(7, 8)
    called wrapped with (7, 8) {}
    15

    # initialized with keyword parameters
    >>> @decorator(debug=True)
    ... def sum(a, b):
    ...    "Sum function"
    ...    return a + b

    >>> sum(9, 10)
    called wrapped with (9, 10) {}
    debug here
    19

    >>> sum.__doc__ == 'Sum function'
    True

    Attributes
    ----------
    ARGUMENTS : dict
        Dictionary of accepted arguments (``kwargs``) and their default values
    to_wrap : def
        The function to be wrapped
    """
    ARGUMENTS = {}

    def __init__(self, *args, **kwargs):
        self.set_kwargs(kwargs)

    def __call__(self, *args, **kwargs):
        f = args[0]
        self.to_wrap = f
        g = wraps(f)(self.get_wrapped_f(f))

        return g

    def set_kwargs(self, kwargs):
        """
        Hook for extending the class for customizing how kwargs are initialized.

        By default the kwargs keys are lookedup from class' ``ARGUMENTS`` attribute.
        If the kwargs with that kep is found, it's value is used and if not, the default
        value is used as defined in class' ``ARGUMENTS`` attribute.

        Parameters
        ----------
        kwargs : dict
            Dictionary of kwargs as passed by the decorator
        """
        self.kwargs = {}
        for k in self.ARGUMENTS.keys():
            self.kwargs[k] = kwargs.pop(k, self.ARGUMENTS[k])

    def get_wrapped_f(self, f):
        """
        Hook for extending the class for customizing the wrapper function, which is the whole
        point of decorators.

        .. note::
            This class automatically wraps the function so ``functools.wraps``
            does not have to be applied.

        Parameters
        ----------
        f : def
            Function to be wrapped

        Returns
        -------
        f : def
            Wrapped function. The default implementation just return the given function
        """
        return f

    @classmethod
    def to_decorator(cls):
        """
        This method should be used to get the actual decorator function. The wrapper generated
        by this functions allows to optionaly initialize the decorator class. See the class
        description for more details.
        """
        @wraps(cls)
        def wrapper(*args, **kwargs):
            if args and callable(args[0]):
                return cls(**kwargs)(args[0])
            else:
                return cls(**kwargs)

        return wrapper


class HybridDecorator(Decorator):
    """
    Class for implementing decorators which can decorate both regular functions as well
    as class methods.

    This decorator automatically determines if the function to be wrapped is a stand-alone
    function or a class method by adding a ``in_class`` attribute.

    Extends ``Decorator``.

    Attributes
    ----------
    in_class : bool
        If the function to be wrapped is defined in a class or as a stand-alone function
    """
    def __is_in_class(self):
        """
        Method determines if the function to be wrapped is a class method or a stand-alone function.

        .. warning::
            This method should not be used by itself because it uses frames to determine it's output.
            If it is called in a different frames stack depth, then the output might not be correct.
            It's output is automatically stored into class' ``in_class`` attribute.
        """
        frames = inspect.stack()
        defined_in_class = False

        diff = 0

        for cls in inspect.getmro(self.__class__):
            if cls is HybridDecorator:
                break
            if 'get_wrapped_f' in cls.__dict__:
                diff += 1

        frame_depth = 4 + diff

        if len(frames) > frame_depth:
            maybe_class_frame = frames[frame_depth]
            statement_list = maybe_class_frame[4]
            first_statment = statement_list[0]
            if first_statment.strip().startswith('class '):
                defined_in_class = True

        return defined_in_class

    def get_wrapped_f(self, f):
        """
        Same as in super class except it also stores the output of ``is_in_class`` in
        ``in_class`` class attribute.
        """
        self.in_class = self.__is_in_class()
        return super(HybridDecorator, self).get_wrapped_f(f)


class Cache(HybridDecorator):
    """
    Examples
    --------

    >>> @Cache()
    ... def compute():
    ...     return 'foo'

    >>> compute()
    'foo'

    >>> @Cache(debug=True)
    ... def compute():
    ...     return 'foo'

    >>> compute()
    Computing value for the first time since it's not in cache.
    'foo'
    >>> compute()
    Getting value from cache
    'foo'
    """
    ARGUMENTS = dict(HybridDecorator.ARGUMENTS)
    ARGUMENTS.update({
        'debug': False,
        'default_cache_value': None,
        'cache_attr_pattern': '_{}',
        'recompute': False,
        'recompute_parameter': 'recompute',
        'is_cached': 'is_cached',
        'cache_attr': 'cache_attr',
    })

    def get_wrapped_f(self, f):
        self.cache_attr = self.kwargs['cache_attr_pattern'].format(f.__name__)  # <<==

        f = super(Cache, self).get_wrapped_f(f)
        self.init_cache()

        setattr(f, self.kwargs['is_cached'], True)
        if self.in_class:
            setattr(f, self.kwargs['cache_attr'], self.cache_attr)

        def wrapper(*args, **kwargs):
            if not hasattr(self, 'cache'):
                self.init_cache(*args, **kwargs)

            recompute = kwargs.pop(self.kwargs['recompute_parameter'], self.kwargs['recompute'])

            cache = self.get_cache(*args, **kwargs)
            if not recompute and self.in_cache(cache, *args, **kwargs):
                if self.kwargs['debug']:
                    print 'Getting value from cache'
                return self.from_cache(cache, *args, **kwargs)

            if self.kwargs['debug']:
                print 'Computing value for the first time since it\'s not in cache.'
            value = f(*args, **kwargs)
            self.to_cache(cache, value, *args, **kwargs)

            return value

        return wrapper

    def init_cache(self, *args, **kwargs):
        if self.in_class and args:
            if not hasattr(args[0], self.cache_attr):
                setattr(args[0], self.cache_attr, copy.copy(self.kwargs['default_cache_value']))
        elif not self.in_class:
            if not hasattr(self, 'cache'):
                self.cache = copy.copy(self.kwargs['default_cache_value'])

    def get_cache(self, *args, **kwargs):
        if self.in_class:
            return getattr(args[0], self.cache_attr)
        else:
            return self.cache

    def in_cache(self, cache, *args, **kwargs):
        return bool(cache)

    def to_cache(self, cache, value, *args, **kwargs):
        if self.in_class:
            setattr(args[0], self.cache_attr, value)
        else:
            self.cache = value

    def from_cache(self, cache, *args, **kwargs):
        return cache


class Memoize(Cache):
    """
    Examples
    --------

    >>> @Memoize()
    ... def sum(a, b):
    ...     return a + b

    >>> sum(1, 2)
    3

    >>> @Memoize(debug=True)
    ... def sum(a, b):
    ...     return a + b

    >>> sum(3, 4)
    Computing value for the first time since it's not in cache.
    7
    >>> sum(3, 4)
    Getting value from cache
    7
    """
    ARGUMENTS = dict(Cache.ARGUMENTS)
    ARGUMENTS.update({
        'default_cache_value': {},
        'is_cached': 'is_memoized',
        'cache_attr': 'memoize_attr',
    })

    def in_cache(self, cache, *args, **kwargs):
        if self.in_class:
            self.cache_key = str(args[1:]) + str(kwargs)
        else:
            self.cache_key = str(args) + str(kwargs)
        return self.cache_key in cache

    def from_cache(self, cache, *args, **kwargs):
        key = self.cache_key
        del self.cache_key
        return cache[key]

    def to_cache(self, cache, value, *args, **kwargs):
        key = self.cache_key
        del self.cache_key
        cache[key] = value


cache = Cache.to_decorator()
memoize = Memoize.to_decorator()
