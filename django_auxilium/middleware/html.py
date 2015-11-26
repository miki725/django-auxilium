from __future__ import print_function, unicode_literals

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

from django_auxilium.utils.html import simple_minify


class MinifyHTMLMiddleware(object):
    """
    Middleware for minifying HTML.

    Unlike some other minifyers, this minifyer is pretty
    simple and tried to do the bare minimum in an attempt
    of being super-lightweight.

    This middleware only works when ``settings.DEBUG``
    is disabled.

    See Also
    --------
    django_auxilium.utils.html.simple_minify
        What is used to actually minify HTML
    """

    def __init__(self):
        if settings.DEBUG:
            raise MiddlewareNotUsed

    def process_response(self, request, response):
        """
        Process the response by minifying HTML.

        HTML is minified only when the response content type
        is HTML (e.g. contains ``'text/html'``).
        """
        header = 'Content-Type'
        if response.has_header(header) and 'text/html' in response[header]:
            try:
                response.content = simple_minify(response.content.strip())
            except Exception:
                pass
        return response
