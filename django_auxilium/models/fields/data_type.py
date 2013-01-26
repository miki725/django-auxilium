import json
from django.db import models


class DataType(object):
    SUPPORTED_TYPES = {
        u'unicode': unicode,
        u'str': str,
        u'bool': bool,
        u'int': int,
        u'float': float,
        u'list': list,
    }
    INVERSE_SUPPORTED_TYPES = dict(zip(SUPPORTED_TYPES.values(), SUPPORTED_TYPES.keys()))
    TYPE_CHOICES = zip(SUPPORTED_TYPES.keys(), SUPPORTED_TYPES.keys())

    def __init__(self, datatype=None):
        if not datatype:
            datatype = unicode

        t_datatype = type(datatype)

        if t_datatype in [str, unicode]:
            self.datatype = self.SUPPORTED_TYPES[datatype]

        elif t_datatype is type and datatype in self.INVERSE_SUPPORTED_TYPES.keys():
            self.datatype = datatype

        elif t_datatype is DataType:
            self.datatype = datatype.datatype

        else:
            raise TypeError('Unsupported {}'.format(str(t_datatype)))

    def encode(self, value):
        if value is None:
            return None

        if self.datatype is list:
            return json.dumps(value)
        else:
            return unicode(value)

    def decode(self, value, *args, **kwargs):
        if value is None:
            return None

        if self.datatype is list:
            return json.loads(value)
        elif self.datatype is bool:
            return True if value == 'True' else False
        else:
            return self.datatype(value, *args, **kwargs)

    def __unicode__(self):
        return self.INVERSE_SUPPORTED_TYPES[self.datatype]

    def __str__(self):
        return str(self.__unicode__())

    def __len__(self):
        return len(self.__unicode__())

    def __call__(self, *args, **kwargs):
        if not args and not kwargs:
            return self.__unicode__()

        return self.decode(*args, **kwargs)


class DataTypeField(models.CharField):
    __metaclass__ = models.SubfieldBase
    description = 'Field for storing python data-types in db with capability to get the data-type back'

    def __init__(self, **kwargs):
        defaults = {}
        overwrites = {
            'max_length': 32,
            'choices': DataType.TYPE_CHOICES,
            'default': u'unicode'
        }
        defaults.update(kwargs)
        defaults.update(overwrites)
        super(DataTypeField, self).__init__(**overwrites)

    def to_python(self, value):
        if value is type(None):
            return DataType()

        return DataType(value)

    def get_prep_value(self, value):
        return unicode(DataType(value))

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return self.get_prep_value(val)

    def validate(self, value, model_instance):
        value = unicode(value)
        return super(DataTypeField, self).validate(value, model_instance)


class ValueDataTypeField(models.TextField):
    def pre_save(self, model_instance, add):
        return model_instance.__dict__.get(self.attname)
