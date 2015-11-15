"""
Collection of Django custom model field which have something to do with files
"""

from __future__ import unicode_literals, print_function
import os
from uuid import uuid4
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
        The path relative to ``media`` where the filaname should be uploaded to

    Returns
    -------
    upload_to : function
        Django ``FileField``'s ``upload_to`` compliant function
    """

    def f(instance, filename):
        ext = filename.split('.')[-1]
        filename = '{0}.{1}'.format(uuid4().hex, ext)
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


class RandomFileFieldMeta(object):
    @staticmethod
    def random_init(self, *args, **kwargs):
        assert kwargs.get('upload_to') is not None

        self.upload_to_path = kwargs['upload_to']
        kwargs['upload_to'] = random_filename_upload_to(kwargs['upload_to'])

        super(self.__class__, self).__init__(*args, **kwargs)

    @staticmethod
    def original_random_init(self, *args, **kwargs):
        assert kwargs.get('upload_to') is not None

        self.filename_field = kwargs.pop('filename_field', 'filename')
        self.upload_to_path = kwargs['upload_to']
        kwargs['upload_to'] = original_random_filename_upload_to(kwargs['upload_to'],
                                                                 self.filename_field)

        super(self.__class__, self).__init__(*args, **kwargs)

    @staticmethod
    def deconstruct(self):
        name, path, args, kwargs = super(self.__class__, self).deconstruct()
        kwargs.update({
            'upload_to': self.upload_to_path,
        })
        if hasattr(self, 'filename_field') and self.filename_field != 'filename':
            kwargs.update({
                'filename_field': self.filename_field,
            })
        return name, path, args, kwargs


RandomFileField = \
    type(str('RandomFileField'),
         (models.FileField,),
         {'__init__': RandomFileFieldMeta.random_init,
          'deconstruct': RandomFileFieldMeta.deconstruct})

OriginalFilenameRandomFileField = \
    type(str('OriginalFilenameRandomFileField'),
         (models.FileField,),
         {'__init__': RandomFileFieldMeta.original_random_init,
          'deconstruct': RandomFileFieldMeta.deconstruct})

RandomImageField = \
    type(str('RandomImageField'),
         (models.ImageField,),
         {'__init__': RandomFileFieldMeta.random_init,
          'deconstruct': RandomFileFieldMeta.deconstruct})

OriginalFilenameRandomImageField = \
    type(str('OriginalFilenameRandomImageField'),
         (models.ImageField,),
         {'__init__': RandomFileFieldMeta.original_random_init,
          'deconstruct': RandomFileFieldMeta.deconstruct})
