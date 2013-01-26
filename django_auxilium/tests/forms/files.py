from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import EMPTY_VALUES
from django import forms
from django_auxilium.forms.files import FileFieldExt


class FileFieldExt_Test(TestCase):
    """
    Test the behaviour of the FileFieldExt form field. Make sure that
    """

    @classmethod
    def setUpClass(cls):
        cls.good_extensions = ['txt', 'csv']
        cls.bad_extensions = ['jpg', 'jpeg', 'png']
        cls.good_types = ['text/plain', 'text/csv']
        cls.bad_types = ['image/jpg', 'image/png']

    def test_empty_file(self):
        """
        Test that if empty file is given, None is returned.
        """
        form = FileFieldExt(required=False)
        for v in EMPTY_VALUES:
            self.assertEqual(form.clean(v), None)

    def test_extensions(self):
        """
        Test that the extension validation is working properly
        """
        form = FileFieldExt(required=False, ext_whitelist=self.good_extensions)

        for ext in self.good_extensions:
            name = 'somefooname.%s' % ext
            file = UploadedFile(name=name, size=1)
            self.assertEqual(form.clean(file), file)

        for ext in self.bad_extensions:
            name = 'somefooname.%s' % ext
            file = UploadedFile(name=name, size=1)
            self.assertRaises(forms.ValidationError)

    def test_mimetypes(self):
        """
        Test that the mimetypes are validate correctly
        """
        form = FileFieldExt(required=False, type_whitelist=self.good_types)

        for t in self.good_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            self.assertEqual(form.clean(file), file)

        for t in self.bad_types:
            name = 'somefooname'
            file = UploadedFile(name=name, size=1, content_type=t)
            with self.assertRaises(forms.ValidationError):
                form.clean(file)

    def test_both(self):
        """
        Test that both extensions and mimetypes are validated correctly both
        at the same time
        """
        form = FileFieldExt(required=False,
                            ext_whitelist=self.good_extensions,
                            type_whitelist=self.good_types)

        for ext in self.good_extensions:
            name = 'somefooname.%s' % ext

            for t in self.good_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                self.assertEqual(form.clean(file), file)

            for t in self.bad_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                with self.assertRaises(forms.ValidationError):
                    form.clean(file)

        for ext in self.bad_extensions:
            name = 'somefooname.%s' % ext

            for t in self.good_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                with self.assertRaises(forms.ValidationError):
                    form.clean(file)

            for t in self.bad_types:
                file = UploadedFile(name=name, size=1, content_type=t)
                with self.assertRaises(forms.ValidationError):
                    form.clean(file)
