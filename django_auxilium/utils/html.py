import re
from django.utils.html import strip_spaces_between_tags
from HTMLParser import HTMLParser
import htmlentitydefs


EXCLUDE_TAGS = ('textarea', 'pre', 'code', 'script',)
RE_WHITESPACE = re.compile(r'\s{2,}|\n')
RE_EXCLUDE_TAGS = re.compile(
    """(               # group for results to be included in re.split
          <(?:{0})     # match beginning of one of exclude tags
                       #   e.g. <pre or <textarea
          .*?          # non-greedy match anything inside the tag
                       # until the next group is matched
          </(?:{0})>   # match the closing tag   e.g. </pre>
    )""".format('|'.join(EXCLUDE_TAGS)),
    re.DOTALL | re.VERBOSE)


def simple_minify(html):
    """
    Minify HTML with very simple algorithm.

    This function tries to minify HTML by stripping all spaces between all html tags
    (e.g. ``</div>    <div>`` -> ``</div><div>``). This step is accomplished by using
    Django's ``strip_spaces_between_tags`` method. In addition to that, this function
    replaces all whitespace (more then two consecutive whitespace characters or new line)
    with a space character except inside excluded tags such as ``pre`` or ``textarea``.

    *Though process*

    To minify everything except content of excluded tags in one step requires very
    complex regular expression. The disadvantage is the regular expression will involve
    look-behinds and look-aheads. Those operations make regex much more resource-hungry
    which eats precious server memory. In addition, complex regex are hard to understand
    and can be hard to maintain. That is why this function splits the task into multiple
    sections. The first step is it executes Django's ``strip_spaces_between_tags``.
    After that, it uses regex expression which matches all exclude tags within the html
    to split the whole html string. However since the regex expression is wrapped inside
    a group, the content of the exclude tags is also included inside the resulting split
    list. Due to that it is guaranteed that every odd element (if there are any) will be
    the excluded tags. That means that all the whitespace within the even elements can
    be removed using the whitespace regex and ``re.sub`` method.
    """
    html = strip_spaces_between_tags(html)
    components = RE_EXCLUDE_TAGS.split(html)
    html = ''
    print len(components)
    for i, component in enumerate(components):
        if i % 2 == 0:
            component = RE_WHITESPACE.sub(' ', component)
        html += component
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