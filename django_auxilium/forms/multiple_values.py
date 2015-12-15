from __future__ import print_function, unicode_literals
import re

import six
from django import forms
from django.utils.translation import ugettext_lazy as _


retype = type(re.compile(''))


class MultipleValuesCharField(forms.CharField):
    """
    Form field to allow users to enter multiple values.

    The best approach to enter multiple values is to provide a user with multiple
    input fields however sometimes that is not feasible. In that case this field
    provides a way for a user to enter multiple values in a single input field. The
    values can be delimited by either a constant character(s) or even by a regular
    expression.

    Examples
    --------

    ::

        MultipleValuesCharField(delimiter=',')
        MultipleValuesCharField(delimiter=',', min_values=1, max_values=10)
        MultipleValuesCharField(delimiter=re.compile(r'\W+'), separator='\\n')
        MultipleValuesCharField(mapping=int)
        MultipleValuesCharField(mapping=lambda i: i == 5)
        MultipleValuesCharField(mapping={'foo': 'bar'})

    Parameters
    ----------
    delimiter : str, Regex, optional
        The delimiter according to which the values are split. It can also be given as a
        compiled regular expression (e.g. ``re.compile('\W+')``).
        Default is ``','`` (comma).
    separator : str
        Iff the delimiter is a regular expression, then this value will be used to
        separate values within the widget when rendering values back in the UI.
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
        Useful to blacklist specific values for being validated.
        If more complex logic is required, please consider using ``mapping``
        as a callable function.
    """
    default_error_messages = {
        'max_values': _('Ensure this value has at least {0} values (it has {1}).'),
        'min_values': _('Ensure this value has at most {0} values (it has {1}).'),
        'invalid_value': _('{0} is an invalid value.'),
        'invalid_values': _('{0} are invalid values.'),
    }

    def __init__(self,
                 delimiter=',',
                 separator=',',
                 mapping=None,
                 max_values=None,
                 min_values=None,
                 strip=True,
                 disregard_empty=True,
                 invalid_values=None,
                 *args, **kwargs):
        self.delimiter = delimiter
        self.separator = delimiter if not isinstance(delimiter, retype) else separator
        self.mapping = mapping or {}
        self.max_values = max_values
        self.min_values = min_values
        self.disregard_empty = disregard_empty
        self.invalid_values = set(invalid_values) if invalid_values else set()

        super(MultipleValuesCharField, self).__init__(*args, **kwargs)

        self.strip = strip

    def to_python(self, value):
        """
        Convert the input value to a list of values.

        Also does basic validation via the ``mapping`` especially
        when it is a callable and so can raise exceptions.

        Returns
        -------
        list
        """
        value = super(MultipleValuesCharField, self).to_python(value)
        if value in self.empty_values:
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
                invalid_values = []
                for i, v in enumerate(values):
                    try:
                        values[i] = self.mapping(v)
                    except Exception:
                        invalid_values.append(v)
                if invalid_values:
                    error_message = 'invalid_value' if len(invalid_values) == 1 else 'invalid_values'
                    raise forms.ValidationError(
                        self.error_messages[error_message].format(
                            ', '.join([six.text_type(i) for i in invalid_values])
                        )
                    )

        return values

    def validate(self, values):
        """
        Validate values

        Primarily this method validates:

        * that ``min_values`` and ``max_values`` are honored
        * that ``invalid_values`` were not supplied
        """
        if values in self.empty_values:
            if self.required:
                raise forms.ValidationError(
                    self.error_messages['required'], code='required'
                )
            else:
                return

        if self.min_values and len(values) < self.min_values:
            raise forms.ValidationError(
                self.error_messages['min_values'].format(len(values), self.min_values)
            )

        if self.max_values and len(values) > self.max_values:
            raise forms.ValidationError(
                self.error_messages['max_values'].format(len(values), self.max_values)
            )

        if self.invalid_values:
            invalid_values = set(values) & self.invalid_values
            if invalid_values:
                error_message = 'invalid_value' if len(invalid_values) == 1 else 'invalid_values'
                raise forms.ValidationError(
                    self.error_messages[error_message].format(
                        ', '.join(map(six.text_type, invalid_values))
                    )
                )

    def run_validators(self, values):
        """
        Run regular Django field validators for each of the values.
        """
        for v in values:
            super(MultipleValuesCharField, self).run_validators(v)

    def prepare_value(self, values):
        """
        Prepare values to be displayed in the UI.

        By default this method joins all the values by the
        ``separator`` if the values is a list or tuple.
        Otherwise, this method returns the value itself.
        Having this method does not require to define a
        custom widget for this form field.
        """
        if isinstance(values, (list, tuple)):
            return self.separator.join(values)
        return values
