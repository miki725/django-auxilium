"""
Collection of simple utilities which modify some behaviour of funtions
"""

import copy
import inspect
import re
from functools import wraps


class Decorator(object):
    """
    Base class for various decorators.

    The most common pattern for creating decorators in Python can be summarized in the
    following snippet::

        from functools import wraps
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **args):
                # some logic here
                return f(*args, **kwargs)
            return wrapper

    The problem with the above approach is when decorators need to employ more difficult
    logic. That sometimes can cause decorator functions to become big hence making it
    difficult to maintain and test. This class is meant to simplify this task. It provides
    a way to make decorators by using classes. This means that decorator's various
    functionality can be split among class methods which can make the decorator's logic
    more transparent and more test-friendly. It also automatically wraps the decorated
    object using ``functools.wraps`` saving some coding lines. Finally, this class allows
    to create decorators where initializing the decorator is optional. This perhaps can
    better be illustrated in a snippet::

        @decorator             # not initialized
        def foo(): pass

        @decorator(foo='bar')  # initialized
        def cat(): pass

    Using this class is pretty simple. The most useful method you should know is
    ``get_wrapped_object``. Inside the method you can refer to ``self.to_wrap`` which
    is the object the method should wrap. The method itself should return the wrapped
    version of the ``to_wrap`` object. If your decorator need to accept additional
    parameters, both required and optional, you can use ``PARAMETERS`` and ``DEFAULTS``
    class attributes to set that up. Finally, to use the decorator, don't forget to use
    the ``to_decorator`` class method. You can refer to `Examples`_ to see a more full
    example of how to use this class.

    Examples
    --------

    ::

        >>> class D(Decorator):
        ...     PARAMETERS = ('debug',)
        ...     DEFAULTS = {'debug': False}
        ...     def get_wrapped_object(self):
        ...         def wrapped(*args, **kwargs):
        ...             print 'called wrapped with', args, kwargs
        ...             if self.parameters['debug']:
        ...                 print 'debug here'
        ...             return self.to_wrap(*args, **kwargs)
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

        >>> # initialized with keyword parameters
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
    PARAMETERS : tuple, list
        The iterable (tuple or list) which lists the parameters the decorator can accept.
        These parameters should be listed similar to a function definition and can contain
        only valid identifier names. The only exceptions to that are ``*args`` and
        ``**kwargs`` parameter names. To make some parameters optional, please use the
        ``DEFAULTS`` attribute dictionary. The following illustrates how this attribute
        can be used to mimic function definitions::

            def foo(bar, cat, dog='hello', *args, **kwargs): pass

            class D(Decorator):
                PARAMETERS = ('bar', 'cat', 'dog', '*args', '**kwargs')
                DEFAULTS = {'dog': 'hello'}
    DEFAULTS : dict
        Dictionary which specifies the default values for parameters defined in
        ``PARAMETERS`` which effectively can make them optional. These optional parameters
        however need to satisfy certain criteria:

        * must be defined after required parameters however before ``*args`` or
          ``**kwargs`` parameters
        * the keys must be present in ``PARAMETERS`` tuple/list
    parameters : dict
        Parsed parameters as specified using ``PARAMETERS`` and ``DEFAULTS``. For more
        information how parameters are parsed please refer to
        ``validate_parameter_config`` and ``get_parameters`` methods documentation.
    to_wrap : def
        The object to be decorated/wrapped. This attributes becomes available when the
        decorator is called on the object.
    """
    PARAMETERS = ()
    DEFAULTS = {}

    def __init__(self, *args, **kwargs):
        self.validate_parameter_config()
        self.set_parameters(*args, **kwargs)

    def __call__(self, f):
        self.to_wrap = f
        g = wraps(f)(self.get_wrapped_object())

        return g

    def validate_parameter_config(self):
        """
        Validate that the ``Decorator``'s ``PARAMETERS`` and ``DEFAULTS`` attributes are
        properly configured.

        In Python, you can have both optional and required function/method parameters.
        Required parameters are the parameters which must be supplied to the function.
        Optional parameters are not required to be supplied because they have a default
        value which will user can overwrite by supplying the parameter. Syntactically the
        required parameters must be defined before optional parameters in the function
        definition.

        The ``Decorator`` allows to create decorators to which both args and kwargs can
        be passed. The list of which parameters can be passed to the decorator can be
        defined using ``Decorator``'s  ``PARAMETERS`` and ``DEFAULTS`` attributes.
        ``PARAMETERS`` defines the tuple of accepted parameters and `DEFAULTS`` defines
        a dictionary of default values for some parameters. Both attributes allow to
        define equivalent function definitions to any Python functions/methods.
        For example, the following will result in equivalent function parameter
        definitions::

            def foo(a, b, c='foo', d='bar', *args, **kwargs): pass

            class D(Decorator):
                PARAMETERS = ('a', 'b', 'c', 'd', '*args', '**kwargs')
                DEFAULTS = {'c': 'foo', 'd': 'bar'}

        This method validates that the optional parameters within the ``PARAMETERS``
        are defined after all required parameters similar to how it is required in Python.

        Returns
        -------
        Does not return anything if validation is successful. Else exception is raise.

        Raises
        ------
        SyntaxError
            If the validation is not successful
        """
        identifiers = [p.replace('*', '') for p in self.PARAMETERS]
        if len(set(identifiers)) < len(identifiers):
            raise SyntaxError('Cannot redefine the same parameter')

        identifier_re_normal = re.compile(r'^[A-Za-z_]\w*$')
        identifier_re_arbitrary = re.compile(r'^(?:\*{1,2})?[A-Za-z_]\w*$')

        # check identifiers syntax
        for i, p in enumerate(self.PARAMETERS):
            if i < len(self.PARAMETERS) - 2:
                pattern = identifier_re_normal
            else:
                pattern = identifier_re_arbitrary

            if not pattern.findall(p):
                raise SyntaxError('Invalid identifier name "{}"'.format(p))

        # check args and kwargs
        arbitrary = self.PARAMETERS[-2:]
        if len(arbitrary) == 2:
            # both are arbitrary
            if arbitrary[0].startswith('*') and arbitrary[1].startswith('*'):
                first = arbitrary[0][1:]
                second = arbitrary[1][1:]
                if first.startswith('*') or not second.startswith('*'):
                    raise SyntaxError('*args have to be before **kwargs')

            # only one is arbitrary - the first cannot be arbitrary
            elif arbitrary[0].startswith('*'):
                raise SyntaxError('*args or **kwargs cannot be before regular parameters')

        # make sure defaults keys are valid
        for k in self.DEFAULTS.keys():
            if not k in self.PARAMETERS:
                raise SyntaxError('Defaults must be defined in parameters attribute')
            elif k.startswith('*'):
                raise SyntaxError('Invalid syntax for default parameter')

        if not self.DEFAULTS:
            return

        optional = False
        for p in self.PARAMETERS:
            if p.startswith('*'):
                continue

            if p in self.DEFAULTS:
                optional = True
            elif optional:
                raise SyntaxError('Optional parameter before required parameter')

    def get_parameters(self, *args, **kwargs):
        """
        Parses the decorator parameters as defined in ``PARAMETERS`` and ``DEFAULTS``
        class attributes.

        This method can be used as a hook to customize the behaviour of how parameters are
        parsed. The reason by this method exists compared to just customizing the
        ``__init__`` is because if it is used in conjunction with ``set_parameters``,
        it automatically saves the parameters into class attribute ``parameters`` hence
        making adding additional parameters to the decorator very easy.

        Parameters
        ----------
        *args : tuple
            Tuple of args to be parsed
        **kwargs : dict
            Dictionary of kwargs to be parsed

        Returns
        -------
        parameters : dict
            The dictionary of parsed args and kwargs

        Raises
        ------
        TypeError
            If there is an error parsing the parameters. The causes can be:

            * too many arguments - more parameters are given compared to the number of
              allowed parameters as defined in ``PARAMETERS``
            * required parameter is not supplied
        SyntaxError
            If one of the parameters is provided twice. For example::

                class D(Decorator):
                    PARAMETERS = ('foo', 'bar')
                d = D.to_decorator()

                @d(1, 2, bar=3)
                def foo(): pass
        """
        parameters = {}

        params_to_set = [p for p in self.PARAMETERS if not p.startswith('*')]

        params_arbitrary = [p for p in self.PARAMETERS if p.startswith('*')]
        args_parameter = [p[1:] for p in params_arbitrary
                          if p.startswith('*') and not p[1:].startswith('*')]
        args_parameter = args_parameter[0] if args_parameter else None
        kwargs_parameter = [p[2:] for p in params_arbitrary if p.startswith('**')]
        kwargs_parameter = kwargs_parameter[0] if kwargs_parameter else None

        # parse args including *args
        args_to_set = min(len(params_to_set), len(args))
        params_set = params_to_set[:args_to_set]
        parameters.update(
            dict(zip(params_to_set[:args_to_set], args[:args_to_set]))
        )
        for p in params_set:
            params_to_set.remove(p)

        # handle *args
        if len(args) > args_to_set:
            if args_parameter:
                parameters[args_parameter] = args[args_to_set:]
            else:
                raise TypeError('Too many arguments')

        # parse the remaining parameters from kwargs including **kwargs
        for p in params_to_set:
            if p in kwargs or p in self.DEFAULTS:
                if p in kwargs:
                    parameters[p] = kwargs.pop(p)
                elif p in self.DEFAULTS:
                    parameters[p] = self.DEFAULTS[p]
                params_set.append(p)

            else:
                raise TypeError('"{}" argument is not provided'.format(p))

        # handle **kwargs
        if kwargs:
            for k in kwargs.keys():
                if k in params_set:
                    raise SyntaxError('"{}" parameter is repeated'.format(k))
            if kwargs_parameter:
                parameters[kwargs_parameter] = kwargs
            else:
                raise TypeError('Too many arguments')

        return parameters

    def set_parameters(self, *args, **kwargs):
        """
        Save the output of ``get_parameters`` into ``parameters`` class attribute.

        Parameters
        ----------
        *args : tuple
        **kwargs : dict
        """
        self.parameters = self.get_parameters(*args, **kwargs)

    def get_wrapped_object(self):
        """
        Returns the wrapped version of the object to be decorated/wrapped.

        This is the meat of class because this method is the one which creates the
        decorator. Inside the method, you can refer to the object to be decorated via
        ``self.to_wrap``.

        .. note::
            This class automatically uses the ``functools.wraps`` to preserve the
            ``to_wrap``'s object useful attributes such as ``__doc__`` hence there
            is no need to do that manually. You can just return a wrapped object
            and the class will take care of the rest.

        Returns
        -------
        f : object
            Decorated/wrapped function
        """
        return self.to_wrap

    @classmethod
    def to_decorator(cls):
        """
        Return the actual decorator.

        This method is necessary because the decorator is a class. Consider the
        following::

            @ClassDecorator
            def foo(): pass

            print type(foo)
            # prints <__main__.ClassDecorator instance at 0x000000000>

        In the above, since ``foo`` will be passed to the decorator's class ``__init__``,
        the returned object will be an instance of the decorator's class instead of a
        wrapper function. To avoid that, this method constructs a wrapper function
        which guarantees that the output of the decorator will be the wrapped object::

            >>> class D(Decorator):
            ...     pass
            >>> d = D()
            >>> @d
            ... def foo(): pass
            >>> isinstance(foo, D)
            False
            >>> from types import FunctionType
            >>> type(foo) is FunctionType
            True
        """
        @wraps(cls)
        def wrapper(*args, **kwargs):
            if args and (callable(args[0]) or inspect.isclass(args[0])):
                return cls()(args[0])
            else:
                return cls(*args, **kwargs)

        return wrapper


class HybridDecorator(Decorator):
    """
    Class for implementing decorators which can decorate both regular functions as well
    as class methods.

    This decorator automatically determines if the object to be decorated is a stand-alone
    function or a class method by adding an ``in_class`` attribute.

    Extends ``Decorator``.

    Attributes
    ----------
    in_class : bool
        ``True`` if the object to be decorated is a class method, or ``False`` if it is a
        standalone function
    """

    def __is_in_class(self):
        """
        Method determines if the object to be wrapped is a class method or a stand-alone
        function.

        .. warning::
            This method should not be used by itself because it uses frames to determine
            its output. If it is called in a different frames stack depth, then the output
            might not be as expected. Its output is automatically stored into ``in_class``
            class attribute so please refer to its output at that attribute.
        """
        frames = inspect.stack()
        defined_in_class = False

        diff = 0

        for cls in inspect.getmro(self.__class__):
            if cls is HybridDecorator:
                break
            if 'get_wrapped_object' in cls.__dict__:
                diff += 1

        frame_depth = 4 + diff

        if len(frames) > frame_depth:
            maybe_class_frame = frames[frame_depth]
            statement_list = maybe_class_frame[4]
            first_statment = statement_list[0]
            if first_statment.strip().startswith('class '):
                defined_in_class = True

        return defined_in_class

    def get_wrapped_object(self):
        """
        Same as in super class except it also stores the output of ``__is_in_class`` in
        ``in_class`` class attribute.
        """
        self.in_class = self.__is_in_class()
        return super(HybridDecorator, self).get_wrapped_object()


class Cache(HybridDecorator):
    """
    Examples
    --------

    ::

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
    PARAMETERS = ('debug', 'default_cache_value', 'cache_attr_pattern', 'recompute',
                  'recompute_parameter', 'is_cached', 'cache_attr')
    DEFAULTS = dict(HybridDecorator.DEFAULTS)
    DEFAULTS.update({
        'debug': False,
        'default_cache_value': None,
        'cache_attr_pattern': '_{}',
        'recompute': False,
        'recompute_parameter': 'recompute',
        'is_cached': 'is_cached',
        'cache_attr': 'cache_attr',
    })

    def get_wrapped_object(self):
        f = self.to_wrap
        self.cache_attr = self.parameters['cache_attr_pattern'].format(f.__name__)

        f = super(Cache, self).get_wrapped_object()
        self.init_cache()

        setattr(f, self.parameters['is_cached'], True)
        if self.in_class:
            setattr(f, self.parameters['cache_attr'], self.cache_attr)

        def wrapper(*args, **kwargs):
            if not hasattr(self, 'cache'):
                self.init_cache(*args, **kwargs)

            recompute = kwargs.pop(self.parameters['recompute_parameter'],
                                   self.parameters['recompute'])

            cache = self.get_cache(*args, **kwargs)
            if not recompute and self.in_cache(cache, *args, **kwargs):
                if self.parameters['debug']:
                    print 'Getting value from cache'
                return self.from_cache(cache, *args, **kwargs)

            if self.parameters['debug']:
                print 'Computing value for the first time since it\'s not in cache.'
            value = f(*args, **kwargs)
            self.to_cache(cache, value, *args, **kwargs)

            return value

        return wrapper

    def init_cache(self, *args, **kwargs):
        if self.in_class and args:
            if not hasattr(args[0], self.cache_attr):
                setattr(args[0], self.cache_attr,
                        copy.copy(self.parameters['default_cache_value']))
        elif not self.in_class:
            if not hasattr(self, 'cache'):
                self.cache = copy.copy(self.parameters['default_cache_value'])

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

    ::

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
    DEFAULTS = dict(Cache.DEFAULTS)
    DEFAULTS.update({
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
