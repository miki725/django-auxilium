from __future__ import unicode_literals, print_function
import json
import six
from django.core.validators import EMPTY_VALUES
from django.db import models
from django_auxilium.forms import (MultipleValuesField as FMultipleValuesField,
                                   MultipleValuesWidget)

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    add_introspection_rules = None


def identity(x):
    return x


class MultipleValuesField(models.TextField):
    FORM_ATTRIBUTES = {
        'delimiter': (',', None),
        'separator': (',', None),
        'mapping': ({}, None),
        'max_values': (None, None),
        'min_values': (None, None),
        'strip': (True, None),
        'disregard_empty': (True, None),
        'invalid_values': ([], set),
    }

    def __init__(self, *args, **kwargs):
        for attr, (default, wrapper) in self.FORM_ATTRIBUTES.items():
            if not wrapper:
                wrapper = identity
            setattr(self, attr, wrapper(kwargs.pop(attr, default)))

        super(MultipleValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(MultipleValuesField, self).to_python(value)
        if value in EMPTY_VALUES:
            return []

        if isinstance(value, six.string_types):
            value = json.loads(value)

        elif isinstance(value, (list, tuple)):
            pass

        else:
            raise TypeError('Unsupported {0}'.format(six.text_type(type(value))))

        return value

    def from_db_value(self, value, *args, **kwargs):
        return self.to_python(value)

    def get_prep_value(self, value):
        try:
            iter(value)
            iterable = True
        except TypeError:
            iterable = False

        if iterable:
            value = json.dumps(list(value))

        value = super(MultipleValuesField, self).get_prep_value(value)
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': FMultipleValuesField,
        }
        for attr in self.FORM_ATTRIBUTES.keys():
            defaults[attr] = getattr(self, attr)
        defaults.update(kwargs)
        defaults.update({
            'widget': MultipleValuesWidget,
        })
        return super(MultipleValuesField, self).formfield(**defaults)


if add_introspection_rules:
    dummy = MultipleValuesField()
    kwargs = {}
    for attr in MultipleValuesField.FORM_ATTRIBUTES.keys():
        if attr in ['mapping']:
            continue
        kwargs[attr] = (attr, {'default': getattr(dummy, attr)})

    add_introspection_rules(
        [
            (
                (MultipleValuesField,),
                (),
                kwargs
            ),
        ],
        [
            '^django_auxilium\.models\.fields\.multiple_values\.MultipleValuesField'
        ]
    )
