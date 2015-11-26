"""
Collection of Django custom model field which have something to do with files
"""

from __future__ import print_function, unicode_literals
import os
import uuid

from django.db import models


def random_filename_upload_to(path):
    """
    Get ``upload_to`` compliant method which will always return a random filename.

    This method can be used as Django's ``FileField`` ``upload_to`` parameter.
    It returns an ``upload_to`` callable which will make sure the filename will always
    be random. This method also accepts a ``path`` parameter which will define where
    relative to the media folder, the file will be stored.

    Parameters
    ----------
    path : str
        The path relative to ``media`` where the filename should be uploaded to

    Returns
    -------
    upload_to : function
        Django ``FileField``'s ``upload_to`` compliant function
    """

    def f(instance, filename):
        ext = filename.split('.')[-1]
        filename = '{0}.{1}'.format(uuid.uuid4().hex, ext)
        return os.path.join(path, filename)

    return f


def original_random_filename_upload_to(path, filename_field):
    """
    Get ``upload_to`` compliant method which will always return a random filename
    however will also store the original filename in the model.

    Parameters
    ----------
    path : str
        The path relative to ``media`` where the filaname should be uploaded to
    filename_field : str
        The name of the model attribute to which the original filename should be stored.

    Returns
    -------
    upload_to : function
        Django ``FileField``'s ``upload_to`` compliant function
    """
    g = random_filename_upload_to(path)

    def f(instance, filename):
        setattr(instance, filename_field, filename)
        return g(instance, filename)

    return f


class RandomFileFieldDeconstructMixin(object):
    """
    Mixin for random filename file mixins which implements
    Django's ``deconstruct`` to be Django-migrations compatible
    """

    def deconstruct(self):
        """
        Standard Django's ``deconstruct`` in order to enable migrations support
        """
        name, path, args, kwargs = super(RandomFileFieldDeconstructMixin, self).deconstruct()
        kwargs.update({
            'upload_to': self.upload_to_path,
        })
        if hasattr(self, 'filename_field') and self.filename_field != 'filename':
            kwargs.update({
                'filename_field': self.filename_field,
            })
        return name, path, args, kwargs


class RandomFileNameFileFieldMixin(RandomFileFieldDeconstructMixin):
    """
    Mixing for a custom ``FileField`` which generates random filename

    Parameters
    ----------
    upload_to : str
        String where uploaded files should be saved.
        Within that directory, random filename will always be selected.
    """

    def __init__(self, *args, **kwargs):
        assert kwargs.get('upload_to') is not None

        self.upload_to_path = kwargs['upload_to']
        kwargs['upload_to'] = random_filename_upload_to(kwargs['upload_to'])

        super(RandomFileNameFileFieldMixin, self).__init__(*args, **kwargs)


class RandomFileNameWithFilenameFileFieldMixin(RandomFileFieldDeconstructMixin):
    """
    Mixing for a custom ``FileField`` which generates random filename
    and also stores original filename

    Parameters
    ----------
    upload_to : str
        String where uploaded files should be saved.
        Within that directory, random filename will always be selected.
    filename_field : str
        Name of Django model field name where original filename
        should be stored
    """
    def __init__(self, *args, **kwargs):
        assert kwargs.get('upload_to') is not None

        self.filename_field = kwargs.pop('filename_field', 'filename')
        self.upload_to_path = kwargs['upload_to']
        kwargs['upload_to'] = original_random_filename_upload_to(
            kwargs['upload_to'],
            self.filename_field
        )

        super(RandomFileNameWithFilenameFileFieldMixin, self).__init__(*args, **kwargs)


RandomFileField = type(
    str('RandomFileField'),
    (RandomFileNameFileFieldMixin, models.FileField,),
    {}
)

OriginalFilenameRandomFileField = type(
    str('OriginalFilenameRandomFileField'),
    (RandomFileNameWithFilenameFileFieldMixin, models.FileField,),
    {}
)

RandomImageField = type(
    str('RandomImageField'),
    (RandomFileNameFileFieldMixin, models.ImageField,),
    {}
)

OriginalFilenameRandomImageField = type(
    str('OriginalFilenameRandomImageField'),
    (RandomFileNameWithFilenameFileFieldMixin, models.ImageField,),
    {}
)
