import re
from django import forms
from django.test import TestCase
from django_auxilium.forms.multiple_values import MultipleValuesField


class MultipleValuesField_Test(TestCase):
    def test_empty(self):
        form = MultipleValuesField(required=False)
        data = ['', None]
        for d in data:
            self.assertEqual(form.clean(d), [])

    def test_delimiter(self):
        delimiters = [',', ';', ':']
        data = ['foo', 'bar', 'foo2', 'bar2']
        for i in delimiters:
            form = MultipleValuesField(delimiter=i)
            value = i.join(data)
            self.assertListEqual(form.clean(value), data)

        delimiter = re.compile('\W+')
        data = 'hello world, how  are you?'
        expected = ['hello', 'world', 'how', 'are', 'you']
        form = MultipleValuesField(delimiter=delimiter)
        self.assertListEqual(form.clean(data), expected)

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

        form = MultipleValuesField(mapping=mapping)
        self.assertListEqual(form.clean(value), expected)

        form = MultipleValuesField(mapping=mapping_callable)
        self.assertListEqual(form.clean(value), expected)

    def test_max_values(self):
        expected = ['foo', 'bar', 'foo2', 'bar2']
        data = ','.join(expected)

        form = MultipleValuesField(max_values=2)
        with self.assertRaises(forms.ValidationError):
            form.clean(data)

        form = MultipleValuesField(max_length=10)
        self.assertListEqual(form.clean(data), expected)

    def test_min_values(self):
        expected = ['foo', 'bar', 'foo2', 'bar2']
        data = ','.join(expected)

        form = MultipleValuesField(min_values=10)
        with self.assertRaises(forms.ValidationError):
            form.clean(data)

        form = MultipleValuesField(min_length=2)
        self.assertListEqual(form.clean(data), expected)

    def test_strip(self):
        data = ['foo', 'bar', 'foo2   ', '   bar2']
        true_expected = [i.strip() for i in data]
        false_expected = data
        value = ','.join(data)

        form = MultipleValuesField(strip=True)
        self.assertListEqual(form.clean(value), true_expected)

        form = MultipleValuesField(strip=False)
        self.assertListEqual(form.clean(value), false_expected)

    def test_disregard_empty(self):
        value = 'foo,,,,,    ,,,bar,,,,'
        true_expected = [i for i in value.split(',') if i]
        false_expected = value.split(',')

        form = MultipleValuesField(disregard_empty=True, strip=False)
        self.assertListEqual(form.clean(value), true_expected)

        form = MultipleValuesField(disregard_empty=False, strip=False)
        self.assertListEqual(form.clean(value), false_expected)

    def test_invalid_values(self):
        data = ['foo', 'bar', 'foo2']
        value = ','.join(data)
        invalid = ['bar', 'foo2']

        form = MultipleValuesField(invalid_values=invalid)
        with self.assertRaises(forms.ValidationError):
            form.clean(value)
