# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import six

from .functools import Decorator


class StringOnion(Decorator):
    def get_wrapped_object(self):
        super(StringOnion, self).get_wrapped_object()

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


string_onion = StringOnion.to_decorator()
