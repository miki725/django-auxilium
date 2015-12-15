from __future__ import print_function, unicode_literals
import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from django_auxilium.utils.range import AlphabeticNumbers, Range


class RangeSelectorField(forms.CharField):
    """
    Range field which supports Excel-type rangeconfig selectors.

    The rangeconfig selection is made using the following format::

        <Column><Row>:<Column><Row>

    Examples
    --------

    ::

        A:A
        A1:A50
        1:50

    Parameters
    ----------
    max_rows : int, optional
        The maximum number of rows the range can have
    max_columns : int, optional
        The maximum number of columns the range can have
    max_either : int, optional
        The maximum number of rows and columns the range can have.
        For example if the value is 1 then either a single column or
        a single row can be selected.
    required_rows : bool, optional
        Whether rows must be supplied in the rangeconfig
    required_columns : bool, optional
        Whether columns must be supplied in the rangeconfig
    """

    default_error_messages = {
        "invalid": _("Invalid range value."),
        "values": _("Top-left coordinate must be first."),
        "max_rows": _("Too many rows selected. Maximum is {0}."),
        "max_columns": _("Too many columns selected. Maximum is {0}."),
        "max_either": _("Too many rows or columns selected. Maximum is {0}."),
        "max_total": _("Too many total cells selected. Maximum is {0}."),
        "required_rows": _("Row selection is required."),
        "required_columns": _("Column selection is required."),
    }

    def __init__(self, *args, **kwargs):
        self.max_rows = kwargs.pop('max_rows', None)
        self.max_columns = kwargs.pop('max_columns', None)
        self.max_either = kwargs.pop('max_either', None)
        self.required_rows = kwargs.pop('required_rows', False)
        self.required_columns = kwargs.pop('required_columns', False)

        super(RangeSelectorField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Convert range string value to ``Range`` rangeconfig value.

        Returns
        -------
        Range
        """
        value = super(RangeSelectorField, self).to_python(value)
        if value in self.empty_values:
            return

        # extract all components
        r = re.compile(
            r'^(?P<A>(?P<A1>[A-Z]+):(?P<A2>[A-Z]+))$'
            r'|^(?P<N>(?P<N1>\d+):(?P<N2>\d+))$'
            r'|^(?P<AN>(?P<AN_A1>[A-Z]+)(?P<AN_N1>\d+):(?P<AN_A2>[A-Z]+)(?P<AN_N2>\d+))$'
        )

        # make sure overall pattern is valid
        if not r.findall(value):
            raise forms.ValidationError(self.error_messages['invalid'])

        datarange = None

        # extract rangeconfig values
        m = r.match(value)
        for group in ['A', 'N', 'AN']:
            if not m.group(group):
                continue
            if group == 'A':
                datarange = Range(
                    AlphabeticNumbers.int_from_str(m.group('A1')),
                    None,
                    AlphabeticNumbers.int_from_str(m.group('A2')),
                    None
                )
            elif group == 'N':
                datarange = Range(
                    None,
                    int(m.group('N1')),
                    None,
                    int(m.group('N2'))
                )
            else:
                datarange = Range(
                    AlphabeticNumbers.int_from_str(m.group('AN_A1')),
                    int(m.group('AN_N1')),
                    AlphabeticNumbers.int_from_str(m.group('AN_A2')),
                    int(m.group('AN_N2'))
                )

        return datarange

    def validate(self, value):
        """
        Validate the rangeconfig value.

        Following is validated:

        * rows or columns are supplied depending on ``required_row``
          and ``required_columns`` parameters
        * rangeconfig is given as top-left to bottom-right
        * columns range is within ``max_columns``
        * rows range is within ``max_rows``
        * both columns and rows range is within ``max_either``
        """
        if value in self.empty_values:
            return

        if self.required_columns and not value.first_column:
            raise forms.ValidationError(
                self.error_messages['required_columns']
            )
        if self.required_rows and not value.first_row:
            raise forms.ValidationError(
                self.error_messages['required_rows']
            )

        # make sure the first rangeconfig coordinate is top-left
        for i, j in zip(value[:2], value[2:]):
            if i and j and i > j:
                raise forms.ValidationError(self.error_messages['values'])

        if self.max_columns and value.columns > self.max_columns:
            raise forms.ValidationError(
                self.error_messages['max_columns'].format(self.max_columns)
            )

        if self.max_rows and value.rows > self.max_rows:
            raise forms.ValidationError(
                self.error_messages['max_rows'].format(self.max_rows)
            )

        if self.max_either:
            if all([value.columns > self.max_either,
                    value.rows > self.max_either]):
                raise forms.ValidationError(
                    self.error_messages['max_either'].format(self.max_either)
                )
