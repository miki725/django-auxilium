from __future__ import unicode_literals, print_function
import re
from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _


class ColorSelector(forms.CharField):
    """
    Custom django field which is able to validate colors as input.
    """

    default_error_messages = {
        "invalid": _("Invalid color value."),
    }

    def __init__(self, *args, **kwargs):
        """
        Init method adds validation parameters to the class.
        The default color type is hex.

        Parameters
        ----------
        type : str
            The type of the color format. The supported formats are

            :hex:
                The hexadecimal notation of the color. Examples is::

                    ff0000

                This type also allows to specify these additional parameters:

                Parameters
                ----------

                hash_required : bool
                    If the `#` is required in the form
                hash_output : bool
                    If the `#` is required in the output

        Raises
        ------
        ValueError
            If unsupported ``type`` color type is provided
        """
        self.color_type = kwargs.pop('type', 'hex')

        if self.color_type == 'hex':
            for p in ['hash_required', 'hash_output']:
                setattr(self, p, kwargs.pop(p, None))

        else:
            raise ValueError('Unsupported color type.')

        super(self.__class__, self).__init__(*args, **kwargs)

    def to_python(self, value, *args, **kwargs):
        """
        Uses ``CharField`` validation. If successful this validates that the
        color is passed properly according to the appropriate parameters passed
        to the class in ``__init__`.
        """
        value = super(self.__class__, self).to_python(value, *args, **kwargs)
        if value in EMPTY_VALUES:
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
