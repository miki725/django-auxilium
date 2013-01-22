"""
Collection of simple utilities which modify some behaviour of funtions
"""

from functools import wraps


def memoize(f):
    """
    Memoization function. It converts input function to a memoized version.
    This means that this function uses cache in order to be able to do result
    lookups instead of computing the result from scratch. If however the cache
    does not have the result for the given input, then it is computed from scratch.

    Parameters
    ----------
    f : def
        Function to be memoized

    Returns
    -------
    mem : def
        Memoized version of the input function
    """
    cache = {}

    @wraps(f)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in cache:
            return cache[key]
        result = f(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper


def cache(f):
    """
    Cache the output of the function. Once the function wrapped function is executed,
    all subsequent calls are not computed but the cached value is returned.

    Parameters
    ----------
    f : def
        Function to be cached

    Returns
    -------
    cache : def
        Cache version of the given function
    """
    attr = '_%s' % f.__name__

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, attr):
            return getattr(self, attr)

        value = f(self, *args, **kwargs)
        setattr(self, attr, value)

        return value

    return wrapper
