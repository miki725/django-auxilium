from django.db import models
from fields.data_type import DataTypeField, ValueDataTypeField


class KeyValueModel(models.Model):
    """
    Base Django model for storing key-value data.

    Attributes
    ----------
    key : str
        The key value of the parameter to be stored
    value : str, optional
        The actual value of the parameter to be stored casted as string
        The field can be None. This is necessary for non-string data-types.
        Even though Django does not recommend this, it is needed in this case.
    value_type : str, optional
        The data-type of the value. This is used to be able to get properly casted value back from the database.
        Default if str.
    """
    key = models.CharField(max_length=32)
    value = ValueDataTypeField(null=True, blank=True)
    value_type = DataTypeField()

    class Meta(object):
        abstract = True

    def setValue(self, value, set_type=True):
        """
        Set value of the value attribute. Also can change the value_type attribute to the type of the
        given value.

        Parameters
        ----------
        value : any
            The value to be set in ``value``
        set_type : bool
            If the ``value_type`` should be set to the type of the given value. For example if integer number is
            given to the value, the ``value_type`` will be set to int.
        """
        if set_type:
            self.value_type = type(value)
            self.value = self.value_type.encode(value)
        else:
            self.value = value

    def __setattr__(self, key, value):
        """
        Overwrites the ``__setattr__`` method for ``value`` and ``value_type`` attributes.
        This method ensures that ``value`` is always casted as string and the given value to
        ``value`` is of allowed type. On all other attributes, ``object.__setattr__`` is called.
        """
        if key == 'value' and not value is None:
            object.__setattr__(self, 'value', unicode(value))

        else:
            object.__setattr__(self, key, value)

    def __getattribute__(self, item):
        """
        Overwrite python ``__getattribute__`` for so that the ``value`` attribute is always returned properly casted
        as specified in ``value_type`` attribute. On all other attributes, ``object.__getattribute__`` is called.
        """

        if item == 'value':
            value_type = object.__getattribute__(self, 'value_type')
            value = object.__getattribute__(self, 'value')
            return value_type(value)

        return object.__getattribute__(self, item)
