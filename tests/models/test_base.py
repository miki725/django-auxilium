from __future__ import absolute_import, print_function, unicode_literals

import six

from django_auxilium.models.base import TitleDescriptionModel


class TestTitleDescriptionModel(object):
    def test_str(self):
        m = TitleDescriptionModel(title='foo')

        assert six.text_type(m) == 'foo'
