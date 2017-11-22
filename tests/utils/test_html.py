from __future__ import print_function, unicode_literals

from django_auxilium.utils.html import (
    TextExtractorHTMLParser,
    html_to_text,
    simple_minify,
)


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
    <strong>Hello</strong> <i>World</i>
    <strong>Hello</strong><i>Mars</i>
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

MINIFY_EXPECTED = """<html> <head> <title>Minify Test</title><script>
        (function() {
            console.log('hello world');
        })();
    </script></head> <body> <strong>Hello</strong> <i>World</i> <strong>Hello</strong><i>Mars</i> <div>Content Here</div><textarea>
Input
Here
  123
    </textarea><code>Code
    Here</code><pre>
    <span>Hello</span>
    <b>World</b>
    {
        "json": "here"
    }
    </pre><script>
        (function() {
            console.log('inside body script');
        })();
    </script></body> </html>"""


EXTRACT_INPUT = """
<html>
<head>
    <title>Minify Test</title>
</head>
<body>
    <div>Content Here</div>
    &gt;&#62;&#x3E;
</body>
</html>
"""

EXTRACT_EXPECTED = """Minify Test


    Content Here
    >>>"""


def test_simple_minify():
    assert simple_minify(MINIFY_INPUT) == MINIFY_EXPECTED


def test_html_to_text():
    assert html_to_text(EXTRACT_INPUT).strip() == EXTRACT_EXPECTED


def test_handle_charref():
    parser = TextExtractorHTMLParser()
    assert parser.handle_charref('62') == '>'


def test_handle_entityref():
    parser = TextExtractorHTMLParser()
    assert parser.handle_entityref('gt') == '>'
