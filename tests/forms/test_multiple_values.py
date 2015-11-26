from __future__ import print_function, unicode_literals
import random
import re

import pytest
import six
from django import forms

from django_auxilium.forms.multiple_values import MultipleValuesCharField


class TestMultipleValuesCharField(object):
    def test_empty(self):
        field = MultipleValuesCharField(required=False)
        data = ['', None]
        for d in data:
            assert field.clean(d) == []

    def test_delimiter(self):
        delimiters = [',', ';', ':']
        data = ['foo', 'bar', 'foo2', 'bar2']
        for i in delimiters:
            field = MultipleValuesCharField(delimiter=i)
            value = i.join(data)
            assert field.clean(value) == data

        delimiter = re.compile('\W+')
        data = 'hello world, how  are you?'
        expected = ['hello', 'world', 'how', 'are', 'you']
        field = MultipleValuesCharField(delimiter=delimiter)
        assert field.clean(data) == expected

    def test_mapping(self):
        mapping = {
            '1': 1
        }

        def mapping_callable(value):
            if value == '1':
                return 1
            else:
                return value

        data = ['foo', '1', 'bar']
        expected = ['foo', 1, 'bar']
        value = ','.join(data)

        field = MultipleValuesCharField(mapping=mapping)
        assert field.clean(value) == expected

        field = MultipleValuesCharField(mapping=mapping_callable)
        assert field.clean(value) == expected

        field = MultipleValuesCharField(mapping=int)
        expected = random.sample(six.moves.range(100000), 5)
        value = ','.join([six.text_type(i) for i in expected])
        assert field.clean(value) == expected

        with pytest.raises(forms.ValidationError):
            field.clean('foo')

    def test_max_values(self):
        expected = ['foo', 'bar', 'foo2', 'bar2']
        data = ','.join(expected)

        field = MultipleValuesCharField(max_values=2)
        with pytest.raises(forms.ValidationError):
            field.clean(data)
        with pytest.raises(forms.ValidationError):
            field.clean('')

        field = MultipleValuesCharField(max_length=10)
        assert field.clean(data) == expected

        field = MultipleValuesCharField(max_length=10, required=False)
        assert field.clean('') == []

    def test_min_values(self):
        expected = ['foo', 'bar', 'foo2', 'bar2']
        data = ','.join(expected)

        field = MultipleValuesCharField(min_values=10)
        with pytest.raises(forms.ValidationError):
            field.clean(data)
        with pytest.raises(forms.ValidationError):
            field.clean('')

        field = MultipleValuesCharField(min_length=2)
        assert field.clean(data) == expected

        field = MultipleValuesCharField(min_length=2, required=False)
        assert field.clean('') == []

    def test_strip(self):
        data = ['foo', 'bar', 'foo2   ', '   bar2']
        true_expected = [i.strip() for i in data]
        false_expected = data
        value = ','.join(data)

        field = MultipleValuesCharField(strip=True)
        assert field.clean(value) == true_expected

        field = MultipleValuesCharField(strip=False)
        assert field.clean(value) == false_expected

    def test_disregard_empty(self):
        value = 'foo,,    ,bar,'
        true_expected = ['foo', '    ', 'bar']
        false_expected = ['foo', '', '    ', 'bar', '']

        field = MultipleValuesCharField(disregard_empty=True, strip=False)
        assert field.clean(value) == true_expected

        field = MultipleValuesCharField(disregard_empty=False, strip=False)
        assert field.clean(value) == false_expected

    def test_invalid_values(self):
        data = ['foo', 'bar', 'foo2']
        value = ','.join(data)
        invalid = ['bar', 'foo2']

        field = MultipleValuesCharField(invalid_values=invalid)
        with pytest.raises(forms.ValidationError):
            field.clean(value)

    def test_prepare_value(self):
        field = MultipleValuesCharField()
        assert field.prepare_value('foo') == 'foo'
        assert field.prepare_value(['foo', 'bar']) == 'foo,bar'
