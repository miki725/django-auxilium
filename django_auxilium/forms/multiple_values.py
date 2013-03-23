from __future__ import unicode_literals, print_function
import re
from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _


retype = type(re.compile(''))


class MultipleValuesField(forms.CharField):
    """
    Form field to allow users to enter multiple values.

    The best approach to enter multiple values is to provide a user with multiple
    input fields however sometimes that is not feasible. In that case this field
    provides a way for a user to enter multiple values in a single input field. The
    values can be delimited by either a constant character(s) or even by a regular
    expression.

    Parameters
    ----------
    delimiter : str, re, optional
        The delimiter according to which the values are split. It can also be given as a
        compiled regular expression (e.g. ``re.compile('\W+')``).
        Default is ``,`` (comma).
    mapping : dict, callable, optional
        By default all split values are casted to a Python string. The mapping allows to
        change that so that individual values will be mapped to different data-types.
        Mapping can be defined as a callable which will should accept one parameter, the
        value, and return the input value properly casted. Mapping can also be defined
        as a dictionary. In that case, if the individual value exists as a key of the
        dictionary, the value associated with the key will be used as a final casted
        value. Please note that if the key is not found in the dictionary, then the input
        value will be used.
        Default is ``None``.
    max_values : int, optional
        The maximum allowed number of values. Default is ``None``.
    min_values : int, optional
        The minimum required number of provided values. Default is ``None``.
    strip : bool, optional
        If ``True``, then once the user string is split, all values are stripped
        of whitespace on either side of the string before being converted to Python value
        by using Python's string ``strip()``.
        Default is ``True``.
    disregard_empty : bool, optional
        If ``True``, then once input string is split, all false evaluated values are
        disregarded. Default is ``True``.
    invalid_values : list, optional
        If provided, this list determines which values are invalid and if any are
        encountered, a ``ValidationError`` will be raised.
    """
    default_error_messages = {
        'max_values': _('More values than allowed. Entered {} and allowed {}.'),
        'min_values': _('More values are necessary. Entered {} and need at least {}.'),
        'invalid_value': _('{} {} an invalid value.'),
    }

    def __init__(self,
                 delimiter=',',
                 mapping=None,
                 max_values=None,
                 min_values=None,
                 strip=True,
                 disregard_empty=True,
                 invalid_values=None,
                 *args, **kwargs):
        self.delimiter = delimiter
        self.mapping = mapping or {}
        self.max_values = max_values
        self.min_values = min_values
        self.strip = strip
        self.disregard_empty = disregard_empty
        self.invalid_values = set(invalid_values) if invalid_values else set()

        super(MultipleValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value, *args, **kwargs):
        value = super(MultipleValuesField, self).to_python(value, *args, **kwargs)
        if value in EMPTY_VALUES:
            return []

        if isinstance(self.delimiter, retype):
            values = self.delimiter.split(value)
        else:
            values = value.split(self.delimiter)

        if self.strip:
            values = [i.strip() for i in values]

        if self.disregard_empty:
            values = [i for i in values if i]

        if self.mapping:
            if not callable(self.mapping):
                values = [self.mapping.get(i, i) for i in values]
            else:
                values = [self.mapping(i) for i in values]

        return values

    def validate(self, values):
        super(MultipleValuesField, self).validate(values)

        if self.min_values and len(values) < self.min_values:
            raise forms.ValidationError(
                self.error_messages['max_values'].format(len(values), self.min_values)
            )

        if self.max_values and len(values) > self.max_values:
            raise forms.ValidationError(
                self.error_messages['max_values'].format(len(values), self.max_values)
            )

        if self.invalid_values:
            invalid_values = set(values).intersection(self.invalid_values)
            if invalid_values:
                raise forms.ValidationError(
                    self.error_messages['invalid_value'].format(
                        ", ".join([str(i) for i in invalid_values]),
                        'is' if len(invalid_values) == 1 else 'are')
                )

    def run_validators(self, values):
        for v in values:
            super(MultipleValuesField, self).run_validators(v)
