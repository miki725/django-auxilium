from __future__ import unicode_literals, print_function
import re
from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _


class TimeField(forms.CharField):
    default_error_messages = {
        "invalid": _("Invalid time format"),
    }

    def to_python(self, value):
        data = super(self.__class__, self).to_python(value)
        if data in EMPTY_VALUES:
            return None

        data = data.lower()
        r = re.compile(r'(\d{1,2}):(\d{2}) ?((:?am)|(:?pm))')
        result = r.findall(data)

        if not result:
            raise forms.ValidationError(self.error_messages['invalid'])

        result = result[0]
        hour = '{0:02}'.format(int(result[0]))
        minutes = result[1]
        ampm = result[2]

        return '{0}:{1} {2}'.format(hour, minutes, ampm)
