import os
from django import forms
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _


class FileFieldExt(forms.FileField):
    """
    Extension of FileField which allows to make sure the uploaded file has
    the appropriate extension and/or mimetype.

    This field accepts all the parameters as FileField, however in addition
    it accepts ``ext_whitelist`` and/or ``type_whitelist`` parameters which
    are lists defining allowed extensions and/or mime types::

        FileFieldExt(ext_whitelist=['jpg', 'jpeg'],
                     type_whitelist=['image/jpeg'])
    """

    default_error_messages = {
        "extension": _(u"File extension is not supported."),
        "mimetype": _(u"File mimetype is not supported.")
    }

    def __init__(self, *args, **kwargs):
        """
        Init methods extends the default FileField init however adds
        support for extra parameters
        """
        ext_whitelist = []
        type_whitelist = []

        if 'ext_whitelist' in kwargs:
            ext_whitelist = kwargs.pop("ext_whitelist")
        if 'type_whitelist' in kwargs:
            type_whitelist = kwargs.pop("type_whitelist")

        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.type_whitelist = [i.lower() for i in type_whitelist]

        super(self.__class__, self).__init__(*args, **kwargs)

    def to_python(self, data, *args, **kwargs):
        """
        Uses FileField's ``to_python`` method to convert data to python,
        however in addition makes sure that the file is of allowed extension
        and/or mimetype if they are specified. If not, raises standard Django
        ``ValidationError`` for both extension and/or mimetype.
        """
        data = super(self.__class__, self).to_python(data, *args, **kwargs)
        if data in EMPTY_VALUES:
            return None

        # make sure the extension is correct
        ext = os.path.splitext(data.name)[1][1:]
        if not ext in self.ext_whitelist and self.ext_whitelist:
            raise forms.ValidationError(self.error_messages['extension'])

        # get the mimetype from the UploadedFile
        try:
            mimetype = data.content_type
        except AttributeError:
            raise forms.ValidationError(self.error_messages['invalid'])

        # make sure the mimetype is correct
        if mimetype not in self.type_whitelist and self.type_whitelist:
            raise forms.ValidationError(self.error_messages['mimetype'])

        return data
