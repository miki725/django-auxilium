from __future__ import absolute_import, print_function, unicode_literals
import os
import uuid

import mock

from django_auxilium.models.fields.files import (
    OriginalFilenameRandomFileField,
    RandomFileField,
    original_random_filename_upload_to,
    random_filename_upload_to,
)


@mock.patch.object(uuid, 'uuid4')
@mock.patch.object(os.path, 'join')
def test_random_filename_upload_to(mock_join, mock_uuid4):
    mock_uuid4.return_value.hex = 'hex'

    upload_to = random_filename_upload_to('foo')
    result = upload_to(None, 'foo.jpg')

    assert result == mock_join.return_value
    mock_join.assert_called_once_with('foo', 'hex.jpg')


@mock.patch.object(uuid, 'uuid4')
@mock.patch.object(os.path, 'join')
def test_original_random_filename_upload_to(mock_join, mock_uuid4):
    mock_uuid4.return_value.hex = 'hex'
    instance = mock.Mock()

    upload_to = original_random_filename_upload_to('foo', 'filename')
    result = upload_to(instance, 'foo.jpg')

    assert result == mock_join.return_value
    assert instance.filename == 'foo.jpg'
    mock_join.assert_called_once_with('foo', 'hex.jpg')


class TestRandomFileField(object):
    def setup_method(self, method):
        self.field = RandomFileField(upload_to='foo')

    def test_init(self):
        assert self.field.upload_to_path == 'foo'
        assert callable(self.field.upload_to)


class TestOriginalFilenameRandomFileField(object):
    def setup_method(self, method):
        self.field = OriginalFilenameRandomFileField(upload_to='foo', filename_field='foo_filename')

    def test_init(self):
        assert self.field.upload_to_path == 'foo'
        assert self.field.filename_field == 'foo_filename'
        assert callable(self.field.upload_to)

    def test_deconstruct(self):
        actual = self.field.deconstruct()

        assert 'upload_to' in actual[3]
        assert actual[3]['upload_to'] == 'foo'
        assert 'filename_field' in actual[3]
        assert actual[3]['filename_field'] == 'foo_filename'
