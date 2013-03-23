from __future__ import unicode_literals, print_function
from django import forms
from django.test import TestCase
from django_auxilium.forms.range import RangeSelector


class RangeSelector_Test(TestCase):
    """
    Test the rangeconfig selector validation
    """

    @classmethod
    def setUpClass(cls):
        cls.form = RangeSelector(required=False)

    def test_empty(self):
        data = ['', None]
        for d in data:
            self.assertEqual(self.form.clean(d), '')

    def test_invalid_input(self):
        data = [':', 'A', '1', 'A:1', 'B:A', '2:1', 'BB:AA']
        for d in data:
            with self.assertRaises(forms.ValidationError):
                self.form.clean(d)

    def test_columns(self):
        data = [
            ('A:A', (1, None, 1, None)),
            ('A:B', (1, None, 2, None)),
            ('AA:BB', (27, None, 54, None))
        ]
        for d in data:
            self.assertEqual(self.form.clean(d[0]), d[1])

    def test_rows(self):
        data = [
            ('1:1', (None, 1, None, 1)),
            ('1:2', (None, 1, None, 2)),
            ('11:22', (None, 11, None, 22))
        ]
        for d in data:
            self.assertEqual(self.form.clean(d[0]), d[1])

    def test_both(self):
        data = [
            ('A1:A1', (1, 1, 1, 1)),
            ('A1:B2', (1, 1, 2, 2)),
            ('AA11:BB22', (27, 11, 54, 22))
        ]
        for d in data:
            self.assertEqual(self.form.clean(d[0]), d[1])

    def test_max_rows(self):
        form = RangeSelector(max_rows=2)
        valid_data = [
            ('1:1', (None, 1, None, 1)),
            ('1:2', (None, 1, None, 2)),
            ('2:3', (None, 2, None, 3)),
        ]
        invalid_data = ['1:3', '11:22']

        for d in valid_data:
            self.assertEqual(form.clean(d[0]), d[1])
        for i in invalid_data:
            with self.assertRaises(forms.ValidationError):
                form.clean(i)

    def test_max_cols(self):
        form = RangeSelector(max_cols=2)
        valid_data = [
            ('A:A', (1, None, 1, None)),
            ('A:B', (1, None, 2, None)),
            ('B:C', (2, None, 3, None)),
        ]
        invalid_data = ['A:C', 'AA:BB']

        for d in valid_data:
            self.assertEqual(form.clean(d[0]), d[1])
        for i in invalid_data:
            with self.assertRaises(forms.ValidationError):
                form.clean(i)

    def test_max_both(self):
        form = RangeSelector(max_rows=2, max_cols=2)
        valid_data = [
            ('A1:A1', (1, 1, 1, 1)),
            ('A1:B2', (1, 1, 2, 2)),
            ('B2:C3', (2, 2, 3, 3)),
        ]
        invalid_data = ['A1:C3', 'AA11:BB22']
        for d in valid_data:
            self.assertEqual(form.clean(d[0]), d[1])
        for i in invalid_data:
            with self.assertRaises(forms.ValidationError):
                form.clean(i)

    def test_max_either(self):
        form = RangeSelector(max_either=2)
        valid_data = [
            ('A:A', (1, None, 1, None)),
            ('1:1', (None, 1, None, 1)),
            ('A1:A50', (1, 1, 1, 50)),
            ('A1:AA1', (1, 1, 27, 1)),
        ]
        invalid_data = ['A1:C3', 'AA11:BB22']
        for d in valid_data:
            self.assertEqual(form.clean(d[0]), d[1])
        for i in invalid_data:
            with self.assertRaises(forms.ValidationError):
                form.clean(i)
