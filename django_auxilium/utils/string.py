# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import six

from .functools import Decorator


class TextOnion(Decorator):
    """
    Simple text onion decorator.

    This decorator ensures that the decorated
    function always receives text string even
    if the decorator receives binary text.
    Once the wrapped function computes the result,
    decorator returns the same data-type as it
    has received.
    """

    def get_wrapped_object(self):
        def wrapped(string):
            is_binary = False
            if isinstance(string, six.binary_type):
                is_binary = True
                string = string.decode('utf-8')

            string = self.to_wrap(string)

            if is_binary:
                string = string.encode('utf-8')

            return string

        return wrapped


text_onion = TextOnion.as_decorator()
