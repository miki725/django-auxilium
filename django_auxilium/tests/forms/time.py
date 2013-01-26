from django import forms
from django.core.validators import EMPTY_VALUES
from django.test import TestCase
from django_auxilium.forms.time import TimeField


class TimeFieldTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.form = TimeField()

    def test_empty(self):
        for i in EMPTY_VALUES:
            with self.assertRaises(forms.ValidationError):
                self.form.clean(i)

    def test_time(self):
        values = {
            '5:00 am': '05:00 am',
            '5:00am': '05:00 am',
            '5:00 pm': '05:00 pm',
        }
        invalid_values = ('foo', '5:00', '5', '5:')

        for v, exp in values.items():
            self.assertEqual(self.form.clean(v), exp)
        for i in invalid_values:
            with self.assertRaises(forms.ValidationError):
                self.form.clean(i)
