from __future__ import unicode_literals, print_function
import json
import six
import types
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    add_introspection_rules = None


@python_2_unicode_compatible
class DataType(object):
    SUPPORTED_TYPES = {
        'text': six.text_type,
        'bool': bool,
        'int': int,
        'float': float,
        'list': list,
    }
    INVERSE_SUPPORTED_TYPES = dict(zip(SUPPORTED_TYPES.values(), SUPPORTED_TYPES.keys()))
    TYPE_CHOICES = zip(SUPPORTED_TYPES.keys(), SUPPORTED_TYPES.keys())

    def __init__(self, datatype=None):
        if not datatype:
            datatype = six.text_type

        t_datatype = type(datatype)
        is_text = isinstance(datatype, six.string_types)

        if t_datatype is DataType:
            self.datatype = datatype.datatype

        elif is_text and datatype in self.SUPPORTED_TYPES.keys():
            self.datatype = self.SUPPORTED_TYPES[datatype]

        elif t_datatype is type and datatype in self.INVERSE_SUPPORTED_TYPES.keys():
            self.datatype = datatype

        else:
            raise TypeError('Unsupported {0}'.format(six.text_type(t_datatype)))

    def get_custom_method(self, direction):
        method_name = '{0}_{1}'.format(direction,
                                       self.INVERSE_SUPPORTED_TYPES[self.datatype])

        if hasattr(self, method_name) and callable(getattr(self, method_name)):
            return getattr(self, method_name)
        else:
            return None

    def encode_list(self, value):
        return json.dumps(value)

    def encode(self, value):
        if value is None:
            return None

        method = self.get_custom_method('encode')
        if method:
            return method(value)
        else:
            return six.text_type(value)

    def decode_list(self, value):
        return json.loads(value)

    def decode_bool(self, value):
        return True if value == 'True' else False

    def decode(self, value, *args, **kwargs):
        if value is None:
            return None

        method = self.get_custom_method('decode')
        if method:
            return method(value)
        else:
            return self.datatype(value, *args, **kwargs)

    def __str__(self):
        return self.INVERSE_SUPPORTED_TYPES[self.datatype]

    def __len__(self):
        return len(six.text_type(self))

    def __call__(self, *args, **kwargs):
        if not args and not kwargs:
            return six.text_type(self)

        return self.decode(*args, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, DataType):
            return False

        return self.datatype == other.datatype

    def __ne__(self, other):
        return not self.__eq__(other)


class DataTypeField(six.with_metaclass(models.SubfieldBase,
                                       models.CharField)):
    description = 'Field for storing Python data-type primitives in the db'

    def __init__(self, **kwargs):
        defaults = {
            'max_length': 32,
            'choices': DataType.TYPE_CHOICES,
            'default': 'text'
        }
        defaults.update(kwargs)
        super(DataTypeField, self).__init__(**defaults)

    def to_python(self, value):
        if isinstance(value, types.NoneType):
            return DataType()

        return DataType(value)

    def get_prep_value(self, value):
        return six.text_type(DataType(value))

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return self.get_prep_value(val)

    def validate(self, value, model_instance):
        value = six.text_type(value)
        return super(DataTypeField, self).validate(value, model_instance)


if add_introspection_rules:
    add_introspection_rules(
        [
            (
                (DataTypeField,),
                (),
                {}
            ),
        ],
        [
            '^django_auxilium\.models\.fields\.data_type\.DataTypeField'
        ]
    )
