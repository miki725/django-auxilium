from __future__ import absolute_import, print_function, unicode_literals

import magic
import mock

from django_auxilium.utils import content_type
from django_auxilium.utils.content_type import (
    get_content_type,
    get_content_type_from_binary,
    get_content_type_from_file,
)


@mock.patch.object(magic, 'from_buffer')
def test_get_content_type_from_binary(mock_from_buffer):
    mock_from_buffer.return_value = b'plain/text'

    actual = get_content_type_from_binary(b'foo')

    assert actual == 'plain/text'
    mock_from_buffer.assert_called_once_with(b'foo', mime=True)


@mock.patch.object(content_type, 'get_content_type_from_binary')
def test_get_content_type_from_file(mock_get_content_type_from_binary):
    f = mock.Mock()

    actual = get_content_type_from_file(f)

    assert actual == mock_get_content_type_from_binary.return_value
    assert f.mock_calls == [
        mock.call.seek(0),
        mock.call.read(1024),
        mock.call.seek(0),
    ]
    mock_get_content_type_from_binary.assert_called_once_with(f.read.return_value)


@mock.patch.object(content_type, 'get_content_type_from_file')
@mock.patch.object(content_type, 'get_content_type_from_binary')
def test_get_content_type_binary(mock_get_content_type_from_binary, mock_get_content_type_from_file):
    actual = get_content_type(b'foo')

    assert actual == mock_get_content_type_from_binary.return_value
    mock_get_content_type_from_binary.assert_called_once_with(b'foo')
    assert not mock_get_content_type_from_file.called


@mock.patch.object(content_type, 'get_content_type_from_file')
@mock.patch.object(content_type, 'get_content_type_from_binary')
def test_get_content_type_file(mock_get_content_type_from_binary, mock_get_content_type_from_file):
    actual = get_content_type(mock.sentinel.file)

    assert actual == mock_get_content_type_from_file.return_value
    mock_get_content_type_from_file.assert_called_once_with(mock.sentinel.file)
    assert not mock_get_content_type_from_binary.called
