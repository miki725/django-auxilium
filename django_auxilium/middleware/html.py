from __future__ import unicode_literals, print_function
from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django_auxilium.utils.html import simple_minify


class MinifyHTMLMiddleware(object):
    def __init__(self):
        if settings.DEBUG:
            raise MiddlewareNotUsed

    def process_response(self, request, response):
        header = 'Content-Type'
        if response.has_header(header) and 'text/html' in response[header]:
            try:
                response.content = simple_minify(response.content.strip())
            except:
                pass
        return response
