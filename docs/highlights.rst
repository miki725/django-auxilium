Highlights
==========

As mentioned in :doc:`README <index>`, this library is a collection
of various utilities for working in Django.
This document highlights some of the most useful features.
To see all of them you can either browse the source code or
browse the API docs.

Models
------

Base models are available with common attributes:

* :py:class:`BaseModel <django_auxilium.models.base.BaseModel>` -
  contains ``created`` and ``modified`` attributes
* :py:class:`CreatedModel <django_auxilium.models.base.CreatedModel>` -
  contains ``created`` attribute
* :py:class:`ModifiedModel <django_auxilium.models.base.ModifiedModel>` -
  contains ``modified`` attribute
* :py:class:`UserModel <django_auxilium.models.base.UserModel>` -
  contains ``user`` attribute which is a foreign key to a Django user model
* :py:class:`TitleDescriptionModel <django_auxilium.models.base.TitleDescriptionModel>` -
  contains ``title`` and ``description`` attributes

Model fields
------------

Useful fields:

* :py:class:`RandomFileField <django_auxilium.models.fields.files.RandomFileField>` -
  file field which always generates unique filename when storing new files
* :py:class:`OriginalFilenameRandomFileField <django_auxilium.models.fields.files.OriginalFilenameRandomFileField>` -
  file field which always generates unique filename when storing new files
  however stores original filename on specified field
* :py:class:`RandomImageField <django_auxilium.models.fields.files.RandomImageField>` -
  image field which always generates unique filename when storing new files
* :py:class:`OriginalFilenameRandomImageField <django_auxilium.models.fields.files.OriginalFilenameRandomImageField>` -
  image field which always generates unique filename when storing new files
  however stores original filename on specified field

Form fields
-----------

* :py:class:`TypedFileField <django_auxilium.forms.files.TypedFileField>` -
  file field which enforces allowed file extensions and/or mimetypes
* :py:class:`MultipleValuesCharField <django_auxilium.forms.multiple_values.MultipleValuesCharField>` -
  character field which normalizes to multiple values via any delimiter including regex.
  Useful when in UI multiple inputs cannot be used but multiple values need
  to be collected.

Signals
-------

Model signal utility decorators:

* :py:func:`file_field_auto_delete <django_auxilium.models.signals.file_field_auto_delete>` -
  this decorator automatically attaches appropriate signal to remove file fields
  when model is removed::

    >>> @file_field_auto_delete
    ... class FooModel(models.Model):
    ...     file = models.FileField(upload_to='foo')

* :py:func:`file_field_auto_change_delete <django_auxilium.models.signals.file_field_auto_change_delete>` -
  this decorator automatically attaches appropriate signal to remove file fields
  when model is removed::

    >>> from dirtyfields import DirtyFieldsMixin
    >>> @file_field_auto_change_delete
    ... class FooModel(DirtyFieldsMixin, models.Model):
    ...     file = models.FileField(upload_to='foo')

* :py:func:`auto_signals <django_auxilium.models.signals.auto_signals>` -
  this decorator allows to define model signals within the model
  which are returned as part of ``get_signals()`` method::

    >>> @auto_signals
    ... class MyModel(models.Model):
    ...     @classmethod
    ...     def get_signals(cls):
    ...         def so_something_pre_save(sender, instance, *args, **kwargs):
    ...             print('doing something on pre_save')
    ...         return [
    ...             {
    ...                 'receiver': so_something,
    ...                 'weak': False,
    ...                 'dispatch_uid': 'my_signal_uuid',
    ...             },
    ...         ]

Middleware
----------

* :py:class:`MinifyHTMLMiddleware <django_auxilium.middleware.html.MinifyHTMLMiddleware>` -
  simple and speedy HTML minifying middleware

Decorators
----------

Utilities
+++++++++

* :py:class:`cache <django_auxilium.utils.functools.cache.cache>` -
  decorator for caching either stand-alone functions or class methods
  so that they are only executed once. Useful for expensive functions
  which do not accept any parameters::

    >>> @cache
    def my_expensive_function():
    ...     return list(zip(range(1000000), range(1000000)))

* :py:class:`memoize <django_auxilium.utils.functools.cache.memoize>` -
  decorator for caching either stand-alone functions or class methods
  which cache results per given parameters so that subsequent calls
  with same parameters are not executed. Useful for expensive functions
  which accept parameters::

    >>> @memoize
    ... def fib(n):
    ...     if n == 0:
    ...         return 0
    ...     elif n == 1:
    ...         return 1
    ...     else:
    ...         return fib(n - 1) + fib(n - 2)

* :py:class:`lazy <django_auxilium.utils.functools.lazy.lazy>` -
  decorator for making functions execute lazily. They only execute
  once any operation is executed on their result, including type checking::

    >>> @lazy(str)
    ... def foo(self):
    ...     print('executing foo')
    ...     return foo

    >>> f = foo()
    >>> isinstance(f, str)
    executing foo
    True
    >>> f == 'foo'
    True

Bases
+++++

These base decorator classes are available which can be used to create
class-based-decorators. They aim to provide to decorators what Django
did with class-based-views to regular views. Both have a place however
for more complex tasks separating logic within decorator might be more
useful. As a matter of fact, the above decorators are all implemented
on top of these base classes:

* :py:class:`Decorator <django_auxilium.utils.functools.decorators.Decorator>` -
  this is a base class for creating class-based-decorators::

    >>> class MyPartialDecorator(Decorator):
    ...     def __init__(self, *args, **kwargs):
    ...         self.args = args
    ...         self.kwargs = kwargs
    ...     def get_wrapped_object(self):
    ...         def wrapper(*args, **kwargs):
    ...             _args = self.args + args
    ...             _kwargs = self.kwargs.copy()
    ...             _kwargs.update(kwargs)
    ...             return self.to_wrap(*_args, **_kwargs)
    ...         return wrapper

    >>> my_partial = MyPartialDecorator.as_decorator()

* :py:class:`HybridDecorator <django_auxilium.utils.functools.decorators.HybridDecorator>` -
  this is a base class for creating class-based-decorators which can wrap both
  standalone functions and class methods::

    >>> class MyDecorator(Decorator):
    ...     def get_wrapped_object(self):
    ...         if self.in_class:
    ...             # class method
    ...         else:
    ...             # standalone function

    >>> my_decorator = MyDecorator.as_decorator()
