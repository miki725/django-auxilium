from __future__ import unicode_literals, print_function
from django import forms


class MultipleValuesWidget(forms.Textarea):
    def __init__(self, separator=',', *args, **kwargs):
        self.separator = separator
        super(MultipleValuesWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = self.separator.join(value)
        return super(MultipleValuesWidget, self).render(name, value, attrs)
