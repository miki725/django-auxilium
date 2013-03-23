from __future__ import unicode_literals, print_function
from django.db import models
from .fields import ValueDataTypeField


class KeyValueModel(models.Model):
    """
    Base Django model for storing key-value data.

    This model stores key-value records where the key can be any string and the value can
    be any primitive data-type. This model does not lock the value to a specific
    data-type.  That is useful when you need to store arbitrary key-value data however
    the data-type of values is not known ahead of time. One example of such use is storing
    image metadata which can be stored as key-value pairs however different EXIF keys
    might require to store values associated with them using different data-types.

    Since relational databases do not allow to specify multiple data-types for a table
    column, this model stores all values as strings and then converts values to a correct
    data-type in Python. In order to do that, this models actually stores two fields
    for the value - one field stores the string-casted value and the other stores the
    data-type to which the value should be casted. The casting process is completely
    transparent to the user. You simply retrieve the ``value`` attribute and it is
    automatically casted to a proper data-type. Behind the hood, this is accomplished
    using Python descriptors.

    Attributes
    ----------
    key : str
        The key value of the parameter to be stored
    value : ValueDataTypeField
        Value of the key-value pair

        .. note::
            The field allows values to be ``None`` (null). Even though this is not
            recommended behavior for strings values because it introduces two false
            boolean conditions - ``None`` and ``''`` (empty string), but this is
            necessary in order to store null non-string values such as ``int``.
    value_type : DataTypeField
        The data-type of the value. This is used in order to be able to encode and decode
        the ``value`` attribute. The default data-type is ``unicode``.

        .. note::
            This field is automatically added by the ``ValueDataTypeField`` field.
    """
    key = models.CharField(max_length=32)
    value = ValueDataTypeField(datatype_field='value_type', null=True, blank=True)

    class Meta(object):
        abstract = True

    def set_value(self, value, set_type=True):
        """
        Set value of the value attribute.

        This method allows to set the value as well as change the datatype attribute
        at the same time.

        Parameters
        ----------
        value : any
            The value to be set in ``value``
        set_type : bool
            If the ``value_type`` should be set to the type of the given value parameter.
            For example if integer number is given to the value, the ``value_type``
            will be set to an ``int``.
            Default is ``True``.
        """
        if set_type:
            self.value_type = type(value)

        self.value = value
