from __future__ import unicode_literals, print_function
from django import forms
from django.test import TestCase
from django_auxilium.forms.color import ColorSelector


class ColorSelector_Test(TestCase):
    """
    Test the color selector validation
    """

    def test_empty(self):
        form = ColorSelector(required=False)
        data = ['', None]
        for d in data:
            self.assertEqual(form.clean(d), '')

    def test_type(self):
        valid_types = ['hex']
        for v in valid_types:
            form = ColorSelector(required=False, type=v)
            self.assertTrue(isinstance(form, ColorSelector))
        invalid_types = ['a', 'b']
        for i in invalid_types:
            with self.assertRaises(ValueError):
                ColorSelector(required=False, type=i)

    def test_hex(self):
        form = ColorSelector()
        valid_values = ['#aaaaaa', 'aaaaaa']
        for v in valid_values:
            self.assertEqual(form.clean(v),
                             v[1:].upper() if v[0] == '#' else v.upper())
        invalid_values = ['aa', '00ff0z']
        for i in invalid_values:
            with self.assertRaises(forms.ValidationError):
                form.clean(i)

    def test_hex_hash_required(self):
        form = ColorSelector(required=False, hash_required=True)
        valid_values = ['#aaaaaa', '#bbbbbb']
        for v in valid_values:
            self.assertEqual(form.clean(v),
                             v[1:].upper() if v[0] == '#' else v.upper())
        invalid_values = ['aaaaaa', 'bbbbbb']
        for i in invalid_values:
            with self.assertRaises(forms.ValidationError):
                form.clean(i)

        form = ColorSelector(required=False, hash_required=False)
        data = valid_values + invalid_values
        for v in data:
            self.assertEqual(form.clean(v),
                             v[1:].upper() if v[0] == '#' else v.upper())

    def test_hex_hash_output(self):
        form = ColorSelector(required=False, hash_output=True)
        data = ['#aaaaaa', '#bbbbbb', 'aaaaaa', 'bbbbbb']
        for v in data:
            self.assertEqual(form.clean(v),
                             v.upper() if v[0] == '#' else '#' + v.upper())

        form = ColorSelector(required=False, hash_output=False)
        for v in data:
            self.assertEqual(form.clean(v),
                             v[1:].upper() if v[0] == '#' else v.upper())
