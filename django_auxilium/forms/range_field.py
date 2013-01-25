from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _
from django_auxilium.utils.range import AlphabeticNumbers


class RangeSelector(forms.CharField):
    """
    Custom Django form field which extends the ``CharField`` to support
    validation for Excel-type rangeconfig selectors.
    The rangeconfig selection is made using the following format::

        <Column><Row>:<Column><Row>

    Examples::

        A:A
        A1:A50
        1:50
    """

    default_error_messages = {
        "invalid": _(u"Invalid range value."),
        "values": _(u"Top-left coordinate must be first."),
        "max_rows": _(u"Too many rows selected. Maximum is {}."),
        "max_cols": _(u"Too many columns selected. Maximum is {}."),
        "max_either": _(u"Too many rows or columns selected. Maximum is {}."),
    }

    def __init__(self, *args, **kwargs):
        """
        Init methods adds support for checking the maximum number
        of rows or columns.

        Parameters
        ----------
        max_rows : int
            The maximum number of rows the range can have
        max_cols : int
            The maximum number of columns the range can have
        max_either : int
            The maximum number of rows or columns the range can have.
            For example if the value is 1 then either a single column or
            a single row can be selected.
        """
        max_rows = kwargs.pop('max_rows', None)
        max_cols = kwargs.pop('max_cols', None)
        max_either = kwargs.pop('max_either', None)

        self.max_rows = max_rows
        self.max_cols = max_cols
        self.max_either = max_either

        super(self.__class__, self).__init__(*args, **kwargs)

        # add css class to widget
        self.widget.attrs['class'] = 'rangeselector'

    def to_python(self, data, *args, **kwargs):
        """
        Uses ``CharField`` character validation. If is successful, this
        functionvalidates the rangeconfig selection. It makes sure that either
        column or row is provided and that they are both in increasing order -
        that top-left coordinate is indeed top-left since it coordinates have
        to be smaller compared to bottom-right.
        """
        data = super(self.__class__, self).to_python(data, *args, **kwargs)
        if data in EMPTY_VALUES:
            return ''

        # extract all components
        import re

        r = re.compile(
            r'^(?P<A>(?P<A1>[A-Z]+):(?P<A2>[A-Z]+))$|^(?P<N>(?P<N1>\d+):(?P<N2>\d+))$|^(?P<AN>(?P<AN_A1>[A-Z]+)(?P<AN_N1>\d+):(?P<AN_A2>[A-Z]+)(?P<AN_N2>\d+))$'
        )

        # make sure overall pattern is valid
        if not r.findall(data):
            raise forms.ValidationError(self.error_messages['invalid'])

        datarange = None

        # extract rangeconfig values
        m = r.match(data)
        for group in ['A', 'N', 'AN']:
            if not m.group(group):
                continue
            if group == 'A':
                datarange = (
                    AlphabeticNumbers.int_from_str(m.group('A1')),
                    None,
                    AlphabeticNumbers.int_from_str(m.group('A2')),
                    None
                )
            elif group == 'N':
                datarange = (
                    None,
                    int(m.group('N1')),
                    None,
                    int(m.group('N2'))
                )
            else:
                datarange = (
                    AlphabeticNumbers.int_from_str(m.group('AN_A1')),
                    int(m.group('AN_N1')),
                    AlphabeticNumbers.int_from_str(m.group('AN_A2')),
                    int(m.group('AN_N2'))
                )

        # make sure the first rangeconfig coordinate is top-left
        for i in range(2):
            if datarange[i]:
                if datarange[2 + i] < datarange[i]:
                    raise forms.ValidationError(self.error_messages['values'])

        # functions for validating rows and columns
        def validateMaxRows(n):
            if datarange[1]:
                if datarange[3] - datarange[1] + 1 > n:
                    return False
                return True
            return None

        def validateMaxCols(n):
            if datarange[0]:
                if datarange[2] - datarange[0] + 1 > n:
                    return False
                return True
            return None

        # validate the maximum rows and columns
        if self.max_cols:
            if validateMaxCols(self.max_cols) is False:
                raise forms.ValidationError(self.error_messages['max_cols'].format(self.max_cols))
        if self.max_rows:
            if validateMaxRows(self.max_rows) is False:
                raise forms.ValidationError(self.error_messages['max_rows'].format(self.max_rows))
        if self.max_either:
            if not validateMaxRows(self.max_either) and not validateMaxCols(self.max_either):
                raise forms.ValidationError(self.error_messages['max_either'].format(self.max_either))

        return datarange
