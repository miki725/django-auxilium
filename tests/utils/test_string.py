from __future__ import absolute_import, print_function, unicode_literals

import six

from django_auxilium.utils.string import text_onion


def test_text_onion():
    @text_onion
    def foo(a):
        assert isinstance(a, six.text_type)
        return a

    assert foo('foo') == 'foo'
    assert foo(b'foo') == b'foo'
