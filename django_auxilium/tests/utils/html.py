from __future__ import unicode_literals, print_function
from django.test import TestCase
from django_auxilium.utils.html import simple_minify


MINIFY_INPUT = """
<html>
<head>
    <title>Minify Test</title>
    <script>
        (function() {
            console.log('hello world');
        })();
    </script>
</head>
<body>
    <div>Content Here</div>
    <textarea>
Input
Here
  123
    </textarea>
    <code>Code
    Here</code>
    <pre>
    <span>Hello</span>
    <b>World</b>
    {
        "json": "here"
    }
    </pre>
    <script>
        (function() {
            console.log('inside body script');
        })();
    </script>
</body>
</html>
"""

MINIFY_EXPECTED = """<html><head><title>Minify Test</title><script>
        (function() {
            console.log('hello world');
        })();
    </script></head><body><div>Content Here</div><textarea>
Input
Here
  123
    </textarea> <code>Code
    Here</code> <pre>
    <span>Hello</span>
    <b>World</b>
    {
        "json": "here"
    }
    </pre><script>
        (function() {
            console.log('inside body script');
        })();
    </script></body></html>"""


class TestHTML(TestCase):
    def test_simple_minify(self):
        self.assertEqual(simple_minify(MINIFY_INPUT), MINIFY_EXPECTED)
