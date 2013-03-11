import re
from django.utils.html import strip_spaces_between_tags
from HTMLParser import HTMLParser
import htmlentitydefs


RE_MULTISPACE = re.compile(r"\s{2,}")
RE_NEWLINE = re.compile(r"\n")


def simple_minify(html):
    html = strip_spaces_between_tags(html.strip())
    html = RE_MULTISPACE.sub(' ', html)
    html = RE_NEWLINE.sub('', html)
    return html


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []

    def handle_data(self, d):
        self.result.append(d)

    def handle_charref(self, number):
        codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
        self.result.append(unichr(codepoint))

    def handle_entityref(self, name):
        codepoint = htmlentitydefs.name2codepoint[name]
        self.result.append(unichr(codepoint))

    def get_text(self):
        return u''.join(self.result)


def html_to_text(html):
    """
    Based from
    `http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python`_.
    """
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()