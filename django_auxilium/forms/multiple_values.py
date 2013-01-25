from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _


class MultipleValuesField(forms.CharField):
    """
    Form field to allow users enter values as comma separated values. Inherits from
    ``CharField`` so accepts al ``CharField`` parameters.

    Parameters
    ----------
    delimiter : str
        The delimiter according to which the values are split. Default is ``,``.
    mapping : dict, callable, optional
        By default all split values are casted to string. If mapping is provided,
        it allows to define a mapping for specific strings to values they should return.
        If callable is provided instead of a ``dict``, then to get the correct Python value,
        it is called with the string value. Default is ``None``.
    max_values : int, optional
        The maximum allowed number of values. Default is ``None``.
    min_values : int, optional
        The minimum required number of provided values. Default is ``None``.
    strip : bool, optional
        If ``True``, then once the user string is split, all values are stripped
        of whitespace on either side of the string before being converted to Python value.
        Default is ``True``.
    disregard_empty : bool, optional
        If ``True``, then once user string is split, all false-equivalent values are disregarded.
        Default is ``True``.
    invalid_values : list, optional
        If provided, then all converted values are checked against this list and if any values
        exist, then error is reported. Default is ``None``.
    """
    default_error_messages = {
        'max_values': _(u'More values than allowed. Entered {} and allowed {}.'),
        'min_values': _(u'More values are necessary. Entered {} and need at least {}.'),
        'invalid_value': _(u'{} {} an invalid value.'),
    }

    def __init__(self,
                 delimiter=u',',
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

        values = value.split(self.delimiter)

        if self.strip:
            values = [i.strip() for i in values]

        if self.disregard_empty:
            values = [i for i in values if i]

        if self.min_values and len(values) < self.min_values:
            raise forms.ValidationError(self.error_messages['max_values'].format(len(values), self.min_values))

        if self.max_values and len(values) > self.max_values:
            raise forms.ValidationError(self.error_messages['max_values'].format(len(values), self.max_values))

        if self.mapping:
            if not callable(self.mapping):
                values = [self.mapping.get(i, i) for i in values]
            else:
                values = [self.mapping(i) for i in values]

        if self.invalid_values:
            invalid_values = set(values).intersection(self.invalid_values)
            if invalid_values:
                raise forms.ValidationError(
                    self.error_messages['invalid_value'].format(", ".join([str(i) for i in invalid_values]),
                                                                'is' if len(invalid_values) == 1 else 'are'))

        return values
