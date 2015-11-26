"""
Collection of simple utilities which modify some behaviour of functions
"""

from __future__ import print_function, unicode_literals
import inspect
import logging
from functools import partial, wraps


log = logging.getLogger(__name__)


class Decorator(object):
    """
    Base class for various decorators.

    Its aim is to do the same for decorators as Django class-based-views
    did to function-based-views.

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
    a way to make decorators by using classes. Its aim is to do the same for decorators
    as Django class-based-views did to function-based-views. This means that decorator's various
    functionality can be split among class methods which can make the decorator's logic
    more transparent and more test-friendly. It also automatically wraps the decorated
    object using ``functools.wraps`` saving some coding lines. Finally, this class allows
    to create decorators where initializing the decorator is optional. This perhaps can
    better be illustrated in a snippet::

        @decorator             # not initialized
        def happy(): pass

        @decorator(foo='bar')  # initialized
        def bunnies(): pass

    Using this class is pretty simple. The most useful method you
    should know is :py:meth:`.get_wrapped_object`. Inside the method
    you can refer to :py:attr:`.to_wrap` which is the object the
    method should wrap. The method itself should return the wrapped
    version of the :py:attr:`.to_wrap` object. If your decorator
    needs to accept additional parameters, you can overwrite
    decorators ``__init__``. Finally, to use the decorator, don't
    forget to use the :py:meth:`as_decorator` class method.
    You can refer to **Examples** to see a more full
    example of how to use this class.

    Examples
    --------

    ::

        >>> class D(Decorator):
        ...     def __init__(self, happy=False):
        ...         self.happy = happy
        ...     def get_wrapped_object(self):
        ...         def wrapped(*args, **kwargs):
        ...             print('called wrapped with', args, kwargs)
        ...             if self.happy:
        ...                 print('Bunnies are very happy today!')
        ...             return self.to_wrap(*args, **kwargs)
        ...         return wrapped
        ...
        >>> decorator = D.as_decorator()

        >>> # not initialized (default values will be used if defined)
        >>> @decorator
        ... def sum(a, b):
        ...    return a + b

        >>> sum(5, 6)
        called wrapped with (5, 6) {}
        11

        >>> # initialized with no parameters (default values will be used if defined)
        >>> @decorator()
        ... def sum(a, b):
        ...    return a + b

        >>> sum(7, 8)
        called wrapped with (7, 8) {}
        15

        >>> # initialized with keyword parameters
        >>> @decorator(happy=True)
        ... def sum(a, b):
        ...    "Sum function"
        ...    return a + b

        >>> sum(9, 10)
        called wrapped with (9, 10) {}
        Bunnies are very happy today!
        19

        >>> sum.__doc__ == 'Sum function'
        True

    Attributes
    ----------
    to_wrap : object
        The object to be decorated/wrapped. This attributes becomes available when the
        decorator is called on the object.
    """

    def __call__(self, f):
        self.to_wrap = f

        self.pre_wrap()
        if inspect.isclass(f):
            return self.get_wrapped_object()
        else:
            return wraps(f)(self.get_wrapped_object())

    def pre_wrap(self):
        """
        Hook for executing things before wrapping objects
        """

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
    def as_decorator(cls, *a, **kw):
        """
        Return the actual decorator.

        This method is necessary because the decorator is a class. Consider the
        following::

            >>> class ClassDecorator(object):
            ...     def __init__(self, obj):
            ...         self.to_wrap = obj

            >>> @ClassDecorator
            ... def foo(): pass
            >>> isinstance(foo, ClassDecorator)
            True

        In the above, since ``foo`` will be passed to the decorator's class ``__init__``,
        the returned object will be an instance of the decorator's class instead of a
        wrapper function. To avoid that, this method constructs a wrapper function
        which guarantees that the output of the decorator will be the wrapped object::

            >>> class D(Decorator):
            ...     pass
            >>> d = D.as_decorator()
            >>> @d
            ... def foo(): pass
            >>> isinstance(foo, D)
            False
        """
        klass = partial(cls, *a, **kw)

        @wraps(cls)
        def wrapper(*args, **kwargs):
            if args and (callable(args[0]) or inspect.isclass(args[0])):
                return klass()(args[0])
            else:
                return klass(*args, **kwargs)

        return wrapper


class HybridDecorator(Decorator):
    """
    Class for implementing decorators which can decorate both regular functions as well
    as class methods.

    This decorator automatically determines if the object to be decorated is a stand-alone
    function or a class method by adding an :py:attr:`in_class` attribute.

    Parameters
    ----------
    is_method : bool, optional
        Explicitly specify whether the decorator is being used on class
        method or a standalone function.
        When not specified, :py:meth:`.pre_wrap` is used to automatically
        determine that. Please look at its documentation for the
        explanation of its limitations.

    Attributes
    ----------
    in_class : bool
        ``True`` if the object to be decorated is a class method, or ``False`` if it is a
        standalone function
    """

    def __init__(self, is_method=None):
        self.is_method = None

    def pre_wrap(self):
        """
        Method which determines whether the ``to_wrap`` is a class
        method or a standalone function

        .. warning::
            This method uses pretty primitive technique to determine
            whether the wrapped callable is a class method or a function
            and so it might not work in all cases.
            It checks the first parameter name of the callable
            and if it is either ``'self'`` or ``'cls'`` it is
            most likely a method.

            If you need more precise behavior you are encouraged to
            use ``is_method`` decorator parameter.
        """
        if self.is_method is None:
            try:
                arg = inspect.getargspec(self.to_wrap).args[0]
            except IndexError:
                self.in_class = False
            else:
                self.in_class = arg in ['self', 'cls']
        else:
            self.in_class = self.is_method
