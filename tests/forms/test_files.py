from __future__ import print_function, unicode_literals

import mock
import pytest
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import EMPTY_VALUES

from django_auxilium.forms import files
from django_auxilium.forms.files import TypedFileField


class TestTypedFileField(object):
    """
    Test the behaviour of the TypedFileField form field. Make sure that
    """
    good_extensions = ['txt', 'csv']
    bad_extensions = ['jpg', 'jpeg', 'png']
    good_types = ['text/plain', 'text/csv']
    bad_types = ['image/jpg', 'image/png']

    def test_empty_file(self):
        """
        Test that if empty file is given, None is returned.
        """
        field = TypedFileField(required=False)
        for v in EMPTY_VALUES:
            assert field.clean(v) is None

    def test_extensions(self):
        """
        Test that the extension validation is working properly
        """
        field = TypedFileField(required=False, ext_whitelist=self.good_extensions)

        for ext in self.good_extensions:
            name = 'somefooname.%s' % ext
            file = UploadedFile(name=name, size=1)
            assert field.clean(file) is file

        for ext in self.bad_extensions:
            name = 'somefooname.%s' % ext
            file = UploadedFile(name=name, size=1)
            with pytest.raises(forms.ValidationError):
                field.clean(file)

    def test_mimetypes(self):
        """
        Test that the mimetypes are validate correctly
        """
        field = TypedFileField(required=False, type_whitelist=self.good_types, use_magic=False)

        for t in self.good_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            assert field.clean(file) is file

        for t in self.bad_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            with pytest.raises(forms.ValidationError):
                field.clean(file)

    @mock.patch.object(files, 'get_content_type')
    def test_mimetypes_magic(self, mock_get_content_type):
        """
        Test that the mimetypes are validate correctly
        """

        def get_content_type(value):
            return value.content_type

        mock_get_content_type.side_effect = get_content_type

        field = TypedFileField(required=False, type_whitelist=self.good_types, use_magic=True)

        for t in self.good_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            assert field.clean(file) is file

        for t in self.bad_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            with pytest.raises(forms.ValidationError):
                field.clean(file)

    def test_no_mimetype(self):
        """
        Make sure ``ValidationError`` is raised if uploaded file has no mimetype
        """
        field = TypedFileField(required=False, type_whitelist=self.good_types, use_magic=False)

        for t in self.good_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            del file.content_type
            with pytest.raises(forms.ValidationError):
                field.clean(file)

    @mock.patch.object(files, 'get_content_type')
    def test_no_mimetype_magic(self, mock_get_content_type):
        """
        Make sure ``ValidationError`` is raised if uploaded file has no mimetype
        """
        mock_get_content_type.side_effect = ValueError

        field = TypedFileField(required=False, type_whitelist=self.good_types)

        for t in self.good_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            with pytest.raises(forms.ValidationError):
                field.clean(file)

    def test_both(self):
        """
        Test that both extensions and mimetypes are validated correctly both
        at the same time
        """
        field = TypedFileField(required=False,
                               ext_whitelist=self.good_extensions,
                               type_whitelist=self.good_types,
                               use_magic=False)

        for ext in self.good_extensions:
            name = 'somefooname.%s' % ext

            for t in self.good_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                assert field.clean(file) is file

            for t in self.bad_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                with pytest.raises(forms.ValidationError):
                    field.clean(file)

        for ext in self.bad_extensions:
            name = 'somefooname.%s' % ext

            for t in self.good_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                with pytest.raises(forms.ValidationError):
                    field.clean(file)

            for t in self.bad_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                with pytest.raises(forms.ValidationError):
                    field.clean(file)
