from __future__ import print_function, unicode_literals
import pathlib

from django import forms
from django.utils.translation import ugettext_lazy as _

from django_auxilium.utils.content_type import get_content_type


class TypedFileField(forms.FileField):
    """
    Typed FileField which allows to make sure the uploaded file has
    the appropriate type.

    File type can be verified either by extension and/or mimetype.

    This field accepts all the parameters as FileField, however in addition
    it accepts some additional parameters as documented below.

    Examples
    --------

    ::

        TypedFileField(ext_whitelist=['jpg', 'jpeg'],
                       type_whitelist=['image/jpeg'])

    .. warning::
        If ``use_magic`` is used, please make sure that ``python-magic``
        is installed. This library does not require it by default.

    Parameters
    ----------
    ext_whitelist : list, optional
        List of allowed file extensions. Note that each extension
        should emit the first period. For example for filename
        ``'example.jpg'``, the allowed extension should be ``'jpg'``.
    type_whitelist : list, optional
        List of allowed file mimetypes.
    use_magic : bool, optional
        If ``type_whitelist`` is specified, this boolean determines
        whether to use ``python-magic`` (based of top of ``libmagic``)
        to determine the mimetypes of files instead of relying
        on Django's ``UploadedFile.content_type``.
        Django does not take any real care to determine any accurately
        the mimetype so it is recommended to leave this parameter
        as ``True`` which is the default value.
    """

    default_error_messages = {
        'extension': _('File extension is not supported.'),
        'mimetype': _('File mimetype is not supported.')
    }

    def __init__(self, *args, **kwargs):
        """
        Init methods extends the default FileField init however adds
        support for extra parameters
        """
        ext_whitelist = kwargs.pop('ext_whitelist', [])
        type_whitelist = kwargs.pop('type_whitelist', [])

        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.type_whitelist = [i.lower() for i in type_whitelist]
        self.use_magic = kwargs.pop('use_magic', True)

        super(TypedFileField, self).__init__(*args, **kwargs)

    def validate(self, value):
        """
        Validate that the file is of supported extension and/or type.
        """
        super(TypedFileField, self).validate(value)
        if value in self.empty_values:
            return None

        # make sure the extension is correct
        ext = pathlib.Path(value.name).name.split('.', 1)[-1]
        if self.ext_whitelist and ext not in self.ext_whitelist:
            raise forms.ValidationError(self.error_messages['extension'])

        # getting mimetype of a file could use some resources
        # so if we don't need to check mimetype, we can return faster
        if not self.type_whitelist:
            return value

        # get the mimetype from the UploadedFile
        if self.use_magic:
            try:
                mimetype = get_content_type(value)
            except Exception:
                raise forms.ValidationError(self.error_messages['invalid'])

        else:
            try:
                mimetype = value.content_type
            except AttributeError:
                raise forms.ValidationError(self.error_messages['invalid'])

        # make sure the mimetype is correct
        if mimetype not in self.type_whitelist:
            raise forms.ValidationError(self.error_messages['mimetype'])

        return value
