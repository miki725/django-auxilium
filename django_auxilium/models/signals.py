from __future__ import print_function, unicode_literals
import inspect
from collections import namedtuple

import six
from django.db import models
from django.dispatch.dispatcher import Signal

from django_auxilium.utils.functools import Decorator, cache


FieldSpec = namedtuple('FieldSpec', ['name', 'field'])
"""
Field specification which is used by file descriptors to reference
the field name and field object itself during decorator operations.
"""


class FileFieldAutoDelete(Decorator):
    """
    Model decorator which automatically setups all the necessary signals to automatically
    remove files associated with given fields when model instance is removed.

    Starting with Django 1.3 when model records are deleted via querysets (e.g.
    ``model.objects.filter(...).delete()``), the model's ``delete()`` method is no longer
    called. As a consequence, if the model has any file fields, those files will not
    be removed even if it is specified in the ``delete()`` method. The new way to remove
    files associated with a model is to use Django signals framework, or more specifically
    the ``post_delete`` signal. This decorator automatically connects the ``post_delete``
    signal which will remove the file associated with the specified file field.

    More about this can be found at Django 1.3
    `release notes <https://docs.djangoproject.com/en/dev/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files>`_.

    Examples
    --------

    ::

        >>> @file_field_auto_delete  # equivalent to @file_field_auto_delete('*')
        ... class FooModel(models.Model):
        ...     file = models.FileField(upload_to='foo')

        >>> @file_field_auto_delete('file')
        ... class FooModel(models.Model):
        ...     file = models.FileField(upload_to='foo')

    Parameters
    ----------
    fields : str, list
        Either a single file field which should be removed on delete
        or a list of fields. Also ``'*'`` can be used in order to delete all
        ``FileField`` on the model.
    signal : Signal, optional
        Djagno signal class which should be used to attach the receiver signal handler to.
        By default is ``post_delete`` signal.
    signal_name_pattern : str, optional
        The name given to the signal function which will automatically remove the file.
        This can be a string formatted string. Into it, two parameters will be passed
        which are ``model`` and ``field``. ``model`` is a model class (not instance) to
        which the signal is being connected to and ``field`` is a name of the file field
        (or ``'_'`` delimited field names if multiple fields are given).
        The default pattern is ``post_delete_{model.__name__}_delete_{field}`` which
        results in patterns like ``'post_delete_Model_delete_file_field'``. The reason
        why this pattern might be useful is because it can be used to disconnect the
        signal receiver at a later time.

    Attributes
    ----------
    field_names : list
        List of normalized field names which should be removed on change
    fields : list
        List of validated :py:class:`.FieldSpec` which signal
        will use to remove changed files
    signal_name_pattern : str
        Same as the ``signal_name_pattern`` parameter
    """

    def __init__(self, fields='*', signal=None, signal_name_pattern=None):
        self.fields = []
        self.field_names = fields
        self.signal = signal or models.signals.post_delete
        self.signal_name_pattern = signal_name_pattern or 'post_delete_{model.__name__}_delete_{field}'

    def get_wrapped_object(self):
        """
        Return the given model

        Since signals are connected externally of a model class,
        the model class is not modified.

        See Also
        --------
        validate_model
        get_field_names
        validate_fields
        connect_signal_function
        """
        self.validate_model()
        self.field_names = self.get_field_names()
        self.validate_fields()
        self.fields = self.get_fields()
        self.connect_signal_function()

        return self.to_wrap

    def get_fields(self):
        """
        Get list of :py:class:`.FieldSpec` for all the fields
        to be removed
        """
        return [
            FieldSpec(name, self.get_field_by_name(name))
            for name in self.field_names
        ]

    def get_field_names(self):
        """
        Get list of field names to be removed in the created signal

        This method is primarily used to normalize the list of
        fields in case it is provided as a string, list or a
        wildcard ``'*'``.

        Returns
        -------
        list
            List of field names which should be removed
            in the created signal
        """
        if isinstance(self.field_names, (list, tuple)):
            return self.field_names

        elif self.field_names == '*':
            return [
                i.name for i in
                self.to_wrap._meta.fields
                if isinstance(i, models.FileField)
            ]

        else:
            return [self.field_names]

    def get_field_by_name(self, name):
        """
        Get a Django model field for the given field name
        from the decorated model

        Parameters
        ----------
        name : str
            Name of the field to get

        Returns
        -------
        Field
            Django model field instance
        """
        return next(iter(filter(
            lambda f: f.name == name,
            self.to_wrap._meta.fields
        )), None)

    def validate_model(self):
        """
        Validate the input to the decorator which is suppose to be a model

        Make sure the given class is a subclass of Django's ``Model`` class.

        Raises
        ------
        TypeError
            If ``to_wrap`` is either not a class or not a Django's
            ``model.Model`` class.
        """
        if not inspect.isclass(self.to_wrap):
            raise TypeError('This decorator can only be applied to classes')
        if not issubclass(self.to_wrap, models.Model):
            raise TypeError('This decorator can only be applied to Django models')

    def validate_fields(self):
        """
        Validate all the fields on the model

        This method is expected to be called after :py:meth:`validate_model`
        and it assumes that ``self.to_wrap`` is a valid Django model.
        This method validates that the given fields are present in the model
        and that they are a subclass of Django's ``FileField`` field class.

        See Also
        --------
        validate_field
        """
        for field in self.field_names:
            self.validate_field(field)

    def validate_field(self, name):
        """
        Validate a single field on the model

        This method is expected to be called after :py:meth:`validate_model`
        and it assumes that ``self.to_wrap`` is a valid Django model.
        It also validates that the given field name is present in the model
        and that it subclasses Django's ``FileField`` field class.

        Raises
        ------
        AttributeError
            When the field cannot be found on the model
        TypeError
            When the field is not a ``FileField``
        """
        field = self.get_field_by_name(name)

        if field is None:
            raise AttributeError('Field "{0}" cannot be found'.format(name))

        if not isinstance(field, models.FileField):
            m = 'Field "{0}" must be a subclass of Django ``FileField``'
            raise TypeError(m.format(name))

    def get_signal_name(self):
        """
        Using the :py:attr:`signal_name_pattern` pattern,
        return the formatted signal name.

        Returns
        -------
        name : str
            The name of the signal
        """
        return self.signal_name_pattern.format(
            model=self.to_wrap,
            field='_'.join(i.name for i in self.fields),
        )

    @cache
    def get_signal_function(self):
        """
        Get the actual function which will be connected to the Django's signal which
        conforms to the ``post_delete`` signal signature::

            def receiver(sender, instance, *args, **kwargs): pass
        """

        def remove(sender, instance, *args, **kwargs):
            """
            Automatically remove the file field when model instance is deleted.
            """
            for name, field in self.fields:
                value = getattr(instance, name, None)
                if value:
                    method = getattr(value, 'delete', None)
                    if method and callable(method):
                        method(save=False)

        return remove

    def connect_signal_function(self):
        """
        Connect the signal as returned by :py:meth:`get_signal_function`
        into the Django's signal's framework.
        """
        signal_name = self.get_signal_name()
        signal_function = self.get_signal_function()
        self.signal.connect(
            signal_function,
            sender=self.to_wrap,
            weak=False,
            dispatch_uid=signal_name
        )


class FileFieldAutoChangeDelete(FileFieldAutoDelete):
    """
    Model decorator which automatically setups all the necessary signals to automatically
    remove files associated with given fields when they change on model save.

    Unlike :py:class:`FileFieldAutoDelete` which removed file fields on
    model deletion, this decorator removes files if they are changed.
    The premise is that if the file field is editable if it is changed
    either in Django Admin or in custom logic, unless custom logic
    is applied, by default Django would not remove the old file
    hence over time many orphan files can accumulate on the server.
    Locally it might not be a big deal however when external (especially paid)
    storage backend is used, extra files can make a real difference over time.
    This decorator automatically handles that and removes old files when
    they are changed.

    In order to do that however model has to track when files change
    on the model and Django models do not do that out of the box.
    You can either implement that functionality yourself on the model
    by implementing the following methods:

    * ``is_dirty()`` - should return a ``bool`` if any of the model
      fields have changed. Usually this will require to track model
      fields during ``__init__`` which will be used to initialize
      model instance when querying model from db and then comparing
      those values with the new values when this method is called.
    * ``get_dirty_fields()`` - should return a ``dict`` where the
      keys are the field names and the values are old field values.

    Alternatively you can use a third-party package which implements
    that API. This decorator is tested with
    `django-dirtyfields <https://pypi.python.org/pypi/django-dirtyfields/>`_.

    .. warning::
        As mentioned above, this decorator **requires** ``is_dirty()``
        and ``get_dirty_fields()`` to be implemented on the model.
        Even though we recommend to use ``django-dirtyfields`` for that
        functionality, this library does not ship with ``django-dirtyfields``
        pre-installed and you will need to install it independently.

    .. note::
        This decorator does not remove files on delete as well.
        If you would like to both remove files on both delete and change
        you will need to apply both :py:class:`FileFieldAutoDelete` and this
        decorator at the same time.

    Examples
    --------

    ::

        >>> from dirtyfields import DirtyFieldsMixin

        >>> @file_field_auto_change_delete  # equivalent to @file_field_auto_change_delete('*')
        ... class FooModel(DirtyFieldsMixin, models.Model):
        ...     file = models.FileField(upload_to='foo')

        >>> @file_field_auto_change_delete('file')
        ... class FooModel(DirtyFieldsMixin, models.Model):
        ...     file = models.FileField(upload_to='foo')

        >>> # remote both on delete and change
        >>> @file_field_auto_delete
        ... @file_field_auto_change_delete
        ... class FooModel(DirtyFieldsMixin, models.Model):
        ...     file = models.FileField(upload_to='foo')

    Parameters
    ----------
    fields : str, list
        Same as :py:class:`FileFieldAutoDelete` ``fields`` parameter
    signal : Signal, optional
        Same as :py:class:`FileFieldAutoDelete` ``signal`` parameter.
        By default is ``post_save`` signal.
    signal_name_pattern : str, optional
        The name given to the signal function which will automatically remove the file.
        This can be a string formatted string. Into it, two parameters will be passed
        which are ``model`` and ``field``. ``model`` is a model class (not instance) to
        which the signal is being connected to and ``field`` is a name of the file field
        (or ``'_'`` delimited field names if multiple fields are given).
        The default pattern is ``post_save_{model.__name__}_delete_{field}`` which
        results in patterns like ``'post_save_Model_delete_file_field'``. The reason
        why this pattern might be useful is because it can be used to disconnect the
        signal receiver at a later time.
    """

    def __init__(self, *args, **kwargs):
        kwargs['signal'] = kwargs.pop('signal', models.signals.post_save)
        kwargs['signal_name_pattern'] = kwargs.pop(
            'signal_name_pattern',
            'post_save_{model.__name__}_changedelete_{field}'
        )
        super(FileFieldAutoChangeDelete, self).__init__(*args, **kwargs)

    def validate_model(self):
        """
        Validate that the model is a valid Django model and that
        it implements necessary API in order to track that model fields
        have changed before saving.
        """
        super(FileFieldAutoChangeDelete, self).validate_model()

        if not all([callable(getattr(self.to_wrap, 'is_dirty', None)),
                    callable(getattr(self.to_wrap, 'get_dirty_fields', None))]):
            raise ValueError(
                'Given model must implement `is_dirty` and '
                '`get_dirty_fields` methods. '
                'You can install "django-dirtyfields" which implements '
                'checking if fields changed before save.'
            )

    @cache
    def get_signal_function(self):
        """
        Get the actual function which will be connected to the Django's signal which
        conforms to the ``post_save`` signal signature::

            def receiver(sender, instance, *args, **kwargs): pass
        """
        def autoremove(sender, instance, *args, **kwargs):
            if instance.is_dirty():
                dirty_fields = instance.get_dirty_fields()
                for name, field in self.fields:
                    # while removing file Django also deletes
                    # reference to it on the model
                    # hence new file will be lost
                    # so we save it and then restore
                    # after removing old file
                    new = getattr(instance, name)
                    old = dirty_fields.get(name, None)
                    if old:
                        # the way Django pickles FileField, it does not
                        # preserve all instance attributes
                        # since they are normally reset by the
                        # FileFieldDescriptor hence we need to manually
                        # restore them here because get_dirty_fields()
                        # probably returns copies of the fields
                        # since it needs to compare them to determine
                        # what is dirty and what is not
                        old.instance = instance
                        old.field = field
                        old.storage = field.storage
                        old.delete(save=False)
                        setattr(instance, name, new)

        return autoremove


class AutoSignals(Decorator):
    """
    Decorator for automatically attaching signals to the model class.

    Usual Django convention is to include all signals in ``signals.py``.
    That works really well in most cases however here are *potential*
    disadvantages:

    * it couples logic to a model class in different Python module
    * signals need to be imported somewhere in app initialization process

    These issues can be resolved by moving the signal receivers to
    ``models.py`` however some issues with that are:

    * signals need to be defined after model definitions
    * if there are many models, it could be hard to find associated signals

    This decorator attempts to solve that by moving the signal receiver
    definitions to the model itself which are retrieved via
    class method ``get_signals``. It allows to tightly couple model
    signal receivers within the model which in some cases might be
    better compared to using ``signals.py`` module.

    ``get_signals`` expected to return a list of signals which should
    be attached to the model class. That could either be achieved
    by returning either receiver handler callables or signal dict
    parameters. Here is a description of what each of them can do:

    :Callables:
        An example::

            >>> @auto_signals
            ... class MyModel(models.Model):
            ...     @staticmethod
            ...     def do_pre_save(sender, instance, *args, **kwargs):
            ...         print('triggered pre_save')
            ...     @staticmethod
            ...     def do_post_save(sender, instance, *args, **kwargs):
            ...         print('triggered post_save')
            ...     @classmethod
            ...     def get_signals(cls):
            ...         return [cls.do_pre_save, cls.do_post_save]

        When ``get_signals`` returns a list of signal receivers,
        each receiver function name should contain the signal name
        to which it needs to connect to. By default this decorator
        supports all Django model signals. If different signals need
        to be supported, please use ``signal_pool`` parameter.
    :Dictionary:
        An example::

            >>> @auto_signals
            ... class MyModel(models.Model):
            ...     @classmethod
            ...     def get_signals(cls):
            ...         def so_something(sender, instance, *args, **kwargs):
            ...             print('doing something')
            ...         def do_something_else_post_save(sender, instance, *args, **kwargs):
            ...             print('doing something else')
            ...         return [
            ...             {
            ...                 'receiver': so_something,
            ...                 'weak': False,
            ...                 'dispatch_uid': 'my_signal_uuid',
            ...                 'signal': 'pre_save',
            ...             },
            ...             {
            ...                 'receiver': do_something_else_post_save,
            ...                 'weak': False,
            ...                 'dispatch_uid': 'my_other_signal_uuid',
            ...             },
            ...         ]

        When ``get_signals`` returns a list of signal dictionaries,
        each ``dict`` should be parameters which will be passed to
        Django's ``Signal.connect``. The only exception is the optional
        ``signal`` key which when given should either be a name of the
        supported signal as per ``signal_pool`` or actual signal object.
        When not provided, this decorator will figure out the signal
        from the receiver's name, same as when ``get_signals`` returns
        a list of callables as described above.

    Parameters
    ----------
    getter : str, optional
        Name of the class method on the decorated model which
        should return signals to be connected
    signal_pool : dict, optional
        Dictionary of supported signals. Keys should be signal
        names and values should be actual signal objects.
        By default all model signals are supported.
    """

    def __init__(self, getter='get_signals', signal_pool=None):
        self.getter = getter
        if signal_pool is None:
            signal_pool = {
                k: v for k, v in vars(models.signals).items()
                if isinstance(v, Signal)
            }
        self.signal_pool = signal_pool

    def validate_model(self):
        """
        Validate that the decorated object is a valid Django model
        class and that it implements signal getter.
        """
        if not inspect.isclass(self.to_wrap):
            raise TypeError('This decorator can only be applied to classes')
        if not issubclass(self.to_wrap, models.Model):
            raise TypeError('Decorator can only be applied to Django models')
        if not hasattr(self.to_wrap, self.getter):
            raise AttributeError(
                'Provided model must implement "{0}" method'
                ''.format(self.getter)
            )
        if not callable(getattr(self.to_wrap, self.getter)):
            raise TypeError(
                'Provided model must implement "{0}" method'
                ''.format(self.getter)
            )

    def get_wrapped_object(self):
        """
        Return the given model

        Since signals are connected externally of a model class,
        the model class is not modified.

        See Also
        --------
        validate_model
        connect_signals
        """
        self.validate_model()
        self.connect_signals()
        return self.to_wrap

    def connect_signals(self):
        """
        Connect all signals as returned by the signal getter
        on the decorated model

        See Also
        --------
        connect_signal
        """
        signals = getattr(self.to_wrap, self.getter)()
        if not isinstance(signals, (list, tuple)):
            signals = [signals]
        for signal in signals:
            self.connect_signal(signal)

    def connect_signal(self, signal):
        """
        Connect individual signal to the decorated model

        Parameters
        ----------
        signal : dict, function
            Either a dict or a function of the receiver signal handler.
            For more information about how each of those are handled,
            please :py:class:`AutoSignals` description.
        """
        kwargs = {
            'sender': self.to_wrap,
        }

        if isinstance(signal, dict):
            kwargs.update(signal)
        elif callable(signal):
            kwargs.update({
                'receiver': signal,
            })
        else:
            raise TypeError(
                'Signals should either be given as a `dict` or callables. '
                '{0} was given.'
                ''.format(type(signal).__name__)
            )

        if 'receiver' not in kwargs:
            raise ValueError(
                'Missing signal receiver callable. '
                'Please either provide a "receiver" key in the signal dict '
                'or use a callable instead of a dict.'
            )

        # if signal to connect to was not provided explicitly
        # try to determine it from the callable name
        if 'signal' not in kwargs:
            for s in self.signal_pool:
                if s in kwargs['receiver'].__name__:
                    kwargs['signal'] = s
                    break

            # the callable name does not suggest which signal to use
            if 'signal' not in kwargs:
                raise ValueError(
                    'Signal to connect to was not provided.'
                )

        # get the signal callable
        if isinstance(kwargs['signal'], six.string_types):
            try:
                kwargs['signal'] = self.signal_pool[kwargs['signal']]
            except KeyError:
                raise ValueError(
                    'Invalid signal "{}" was provided. '
                    'Please either explicitly specify Django signal '
                    'or provide its name in the receiver callable name.'
                    ''.format(kwargs['signal'])
                )

        kwargs.pop('signal').connect(**kwargs)


file_field_auto_delete = FileFieldAutoDelete.as_decorator()
file_field_auto_change_delete = FileFieldAutoChangeDelete.as_decorator()
auto_signals = AutoSignals.as_decorator()
