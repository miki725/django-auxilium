from __future__ import print_function, unicode_literals
import re

from django import forms
from django.utils.translation import ugettext_lazy as _


class ColorCharField(forms.CharField):
    """
    Custom django field which is able to validate colors as input.

    Parameters
    ----------
    type : str
        The type of the color format. The supported formats are

        :hex:
            The hexadecimal notation of the color. Examples is::

                ff0000
                #00ff00

            This type also allows to specify these additional parameters:

            Parameters
            ----------

            hash_required : bool
                If the ``#`` is required in the value
                (e.g. ``'#ff0000'``)
            hash_output : bool
                If the ``#`` is required in the output
                validated value in ``to_python``


    Raises
    ------
    ValueError
        If unsupported ``type`` color type is provided
    """

    default_error_messages = {
        'invalid': _('Invalid color value.'),
    }

    def __init__(self, *args, **kwargs):
        self.color_type = kwargs.pop('type', 'hex')

        if self.color_type == 'hex':
            kwargs['min_length'] = 6
            kwargs['max_length'] = 7
            for p in ['hash_required', 'hash_output']:
                setattr(self, p, kwargs.pop(p, None))

        else:
            raise ValueError('Unsupported color type.')

        super(ColorCharField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Convert to a validated string color value.
        """
        value = super(ColorCharField, self).to_python(value)
        if value in self.empty_values:
            return ''

        if self.color_type == 'hex':
            value = value.upper()

            # calculate the validation regex
            if self.hash_required:
                r = re.compile(r'^#[0-9A-F]{6}$')
            else:
                r = re.compile(r'^#?[0-9A-F]{6}$')

            # validate the format of the string
            if not r.findall(value):
                raise forms.ValidationError(self.error_messages['invalid'])

            # remove hash if exists
            if value[0] == '#':
                value = value[1:]

            # add hash only if required for output
            if self.hash_output:
                value = '#' + value

        return value
