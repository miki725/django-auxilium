from __future__ import print_function, unicode_literals

import pytest
from django import forms

from django_auxilium.forms.color import ColorCharField


class TestColorCharField(object):
    """
    Test the color selector validation
    """

    def test_empty(self):
        field = ColorCharField(required=False)
        data = ['', None]
        for d in data:
            assert field.clean(d) == ''

    def test_type(self):
        valid_types = ['hex']
        for v in valid_types:
            field = ColorCharField(required=False, type=v)
            assert isinstance(field, ColorCharField)

        invalid_types = ['a', 'b']
        for i in invalid_types:
            with pytest.raises(ValueError):
                ColorCharField(required=False, type=i)

    def test_hex(self):
        field = ColorCharField()
        valid_values = ['#aaaaaa', 'aaaaaa']

        for v in valid_values:
            assert field.clean(v) == (v[1:].upper() if v[0] == '#' else v.upper())

        invalid_values = ['aa', '00ff0z']
        for i in invalid_values:
            with pytest.raises(forms.ValidationError):
                field.clean(i)

    def test_hex_hash_required(self):
        field = ColorCharField(required=False, hash_required=True)
        valid_values = ['#aaaaaa', '#bbbbbb']
        for v in valid_values:
            assert field.clean(v) == (v[1:].upper() if v[0] == '#' else v.upper())

        invalid_values = ['aaaaaa', 'bbbbbb']
        for i in invalid_values:
            with pytest.raises(forms.ValidationError):
                field.clean(i)

        field = ColorCharField(required=False, hash_required=False)
        data = valid_values + invalid_values
        for v in data:
            assert field.clean(v) == (v[1:].upper() if v[0] == '#' else v.upper())

    def test_hex_hash_output(self):
        field = ColorCharField(required=False, hash_output=True)
        data = ['#aaaaaa', '#bbbbbb', 'aaaaaa', 'bbbbbb']
        for v in data:
            assert field.clean(v) == (v.upper() if v[0] == '#' else '#' + v.upper())

        field = ColorCharField(required=False, hash_output=False)
        for v in data:
            assert field.clean(v) == (v[1:].upper() if v[0] == '#' else v.upper())
