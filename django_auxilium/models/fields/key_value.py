from __future__ import unicode_literals, print_function
from django.db import models
from .data_type import DataType, DataTypeField as _DataTypeField

try:
    from south.modelsinspector import add_introspection_rules, add_ignored_fields
except ImportError:
    add_introspection_rules = add_ignored_fields = None


class ValueDescriptor(object):
    def __init__(self, field, datatype_field):
        self.field = field
        self.datatype_field = datatype_field
        self.value_attribute = '_{}'.format(field.attname)

    def get_datatype(self, instance):
        if hasattr(instance, self.datatype_field):
            datatype = getattr(instance, self.datatype_field)
            if isinstance(datatype, DataType):
                return datatype
        return None

    def __get__(self, instance, owner):
        if not instance:
            raise AttributeError(
                "The '{}' attribute can only be accessed from '{}' instances.".format(
                    self.field.name, owner.__name__
                ))

        return getattr(instance, self.value_attribute, self.field.default)

    def __set__(self, instance, value):
        datatype = self.get_datatype(instance)
        if not datatype:
            return

        if not isinstance(value, datatype.datatype):
            value = datatype.decode(value)

        setattr(instance, self.value_attribute, value)


class DataTypeField(_DataTypeField):
    pass


class ValueDataTypeField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.datatype_field = kwargs.pop('datatype_field')

        defaults = {
            'default': '',
        }
        defaults.update(kwargs)

        super(ValueDataTypeField, self).__init__(*args, **defaults)

    def _get_datatype_field(self):
        return DataTypeField()

    def _get_encoded_value(self, model_instance):
        value = getattr(model_instance, self.datatype_field).encode(
            self._get_val_from_obj(model_instance)
        )
        return value

    def pre_save(self, model_instance, add):
        value = self._get_encoded_value(model_instance)
        return value

    def value_to_string(self, obj):
        value = self._get_encoded_value(obj)
        return self.get_prep_value(value)

    def validate(self, value, model_instance):
        value = self._get_encoded_value(model_instance)
        return super(ValueDataTypeField, self).validate(value, model_instance)

    def contribute_to_class(self, cls, name):
        # add datatype field
        # also make sure its creation counter is lower than this field's
        # counter to make sure that datatype field is always created before
        # this field
        datatype_field = self._get_datatype_field()
        datatype_field.creation_counter = self.creation_counter
        self.creation_counter += 1
        models.Field.creation_counter += 1

        cls.add_to_class(self.datatype_field, datatype_field)

        super(ValueDataTypeField, self).contribute_to_class(cls, name)

        setattr(cls, self.name, ValueDescriptor(self, self.datatype_field))


if add_introspection_rules:
    add_introspection_rules(
        [
            (
                (ValueDataTypeField,),
                (),
                {'datatype_field': ('datatype_field', {})}
            ),
        ],
        [
            '^django_auxilium\.models\.fields\.key_value\.ValueDataTypeField'
        ]
    )
    add_ignored_fields([
        '^django_auxilium\.models\.fields\.key_value\.DataTypeField'
    ])
