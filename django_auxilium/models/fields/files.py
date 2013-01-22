"""
Collection of Django custom model field which have something to do with files
"""

import os
from functools import wraps
from uuid import uuid4
from django.db.models import FileField


class RandomFileField(FileField):
    """
    Class which implements custom behaviour for ``upload_to`` paramater
    for Django ``FileField`` model field. It makes sure that the uploaded file
    will be given a random filename when saved. This enhances security and tries
    to avoid any possible filename conflicts. This class inherits from Django
    standard ``FileField``.

    Parameters
    ----------
    upload_to : str
        Path where the uploaded file should be uploaded to
    """
    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = self.upload_to(kwargs['upload_to'])

        super(RandomFileField, self).__init__(*args, **kwargs)

    def upload_to(self, path):
        """
        Get the method which will be passed to ``upload_to`` argument to
        Django ``FileField``. This method will make sure the uploaded
        files will have a random filename.

        Parameters
        ----------
        path : str
            The path relative to ``media`` where the filaname should be uploaded to

        Returns
        -------
        upload_to : def
            Function following Django ``FileField`` ``upload_to`` parameter which
            will retun a random path where the file should be saved to.
        """
        @wraps(self.upload_to)
        def f(instance, filename):
            ext = filename.split('.')[-1]
            filename = '{}.{}'.format(uuid4().hex, ext)
            return os.path.join(path, filename)

        return f


class OriginalFilenameRandomFileField(RandomFileField):
    """
    Class which implements custom behaviour for ``upload_to`` paramater
    for Django ``FileField`` model field. It makes sure that the uploaded file
    will be given a random filename when saved. Unlike ``RandomFileField``, this
    class' implementation saves the original filename in the models field as
    specified in ``filename_field`` parameter. Having random filename enhances
    security and tries to avoid any possible filename conflicts.
    This class inherits from ``RandomFileField``.

    Parameters
    ----------
    upload_to : str
        Path where the uploaded file should be uploaded to
    filename_field : str, optional
        Field name of Django model where the original filename should be saved

        .. note:: The model field **must** be defined below the file field.
    """
    def __init__(self, *args, **kwargs):
        filename_field = kwargs.pop('filename_field', 'filename')
        kwargs['upload_to'] = self.upload_to(kwargs['upload_to'], filename_field)

        super(OriginalFilenameRandomFileField, self).__init__(*args, **kwargs)

    def upload_to(self, path, filename_field):
        """
        Get the method which will be passed to ``upload_to`` argument to
        Django ``FileField``. This method will make sure the uploaded
        files will have a random filename. Also it will save the original
        filename in the specified model field.

        Parameters
        ----------
        path : str
            The path relative to ``media`` where the filaname should be uploaded to

        Returns
        -------
        upload_to : def
            Function following Django ``FileField`` ``upload_to`` parameter which
            will retun a random path where the file should be saved to.
        """
        g = super(OriginalFilenameRandomFileField, self).upload_to(path)

        @wraps(self.upload_to)
        def f(instance, filename):
            setattr(instance, filename_field, filename)
            return g(instance, filename)

        return f
