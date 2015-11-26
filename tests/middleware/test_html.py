from __future__ import absolute_import, print_function, unicode_literals

import mock
import pytest
from django.core.exceptions import MiddlewareNotUsed
from django.http.response import HttpResponse

from django_auxilium.middleware import html
from django_auxilium.middleware.html import MinifyHTMLMiddleware


class TestMinifyHTMLMiddleware(object):
    def test_init(self, settings):
        settings.DEBUG = False

        assert isinstance(MinifyHTMLMiddleware(), MinifyHTMLMiddleware)

        settings.DEBUG = True
        with pytest.raises(MiddlewareNotUsed):
            MinifyHTMLMiddleware()

    @mock.patch.object(html, 'simple_minify')
    def test_process_response_html(self, mock_simple_minify, settings):
        settings.DEBUG = False
        response = HttpResponse('foo  ')
        response['Content-Type'] = 'text/html'
        mock_simple_minify.return_value = 'hello there'

        middleware = MinifyHTMLMiddleware()

        assert middleware.process_response(None, response) is response
        assert response.content == b'hello there'
        mock_simple_minify.assert_called_once_with(b'foo')

    @mock.patch.object(html, 'simple_minify')
    def test_process_response_error(self, mock_simple_minify, settings):
        settings.DEBUG = False
        response = HttpResponse('foo  ')
        response['Content-Type'] = 'text/html'
        mock_simple_minify.side_effect = ValueError

        middleware = MinifyHTMLMiddleware()

        assert middleware.process_response(None, response) is response
        assert response.content == b'foo  '
        mock_simple_minify.assert_called_once_with(b'foo')
