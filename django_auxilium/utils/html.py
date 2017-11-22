from __future__ import print_function, unicode_literals
import re

import six
from six.moves.html_entities import name2codepoint
from six.moves.html_parser import HTMLParser

from .string import text_onion


EXCLUDE_TAGS = ('textarea', 'pre', 'code', 'script',)
RE_WHITESPACE = re.compile(r'\s{2,}|\n')
RE_SPACE_BETWEEN_TAGS = re.compile(r'>(?:\s{2,}|\n)<')
RE_EXCLUDE_TAGS = re.compile(
    """(               # group for results to be included in re.split
          <(?:{0})     # match beginning of one of exclude tags
                       #   e.g. <pre or <textarea
          .*?          # non-greedy match anything inside the tag
                       # until the next group is matched
          </(?:{0})>   # match the closing tag   e.g. </pre>
    )""".format('|'.join(EXCLUDE_TAGS)),
    re.DOTALL | re.VERBOSE)


@text_onion
def simple_minify(html):
    """
    Minify HTML with very simple algorithm.

    This function tries to minify HTML by stripping most spaces between all html tags
    (e.g. ``</div>    <div>`` -> ``</div> <div>``). Note that not all spaces are removed
    since sometimes that can adjust rendered HTML (e.g. ``<strong>Hello</strong> <i></i>``).
    In addition to that, this function replaces all whitespace
    (more then two consecutive whitespace characters or new line)
    with a space character except inside excluded tags such as ``pre`` or ``textarea``.

    **Though process**:

    To minify everything except content of excluded tags in one step requires very
    complex regular expression. The disadvantage is the regular expression will involve
    look-behinds and look-aheads. Those operations make regex much more resource-hungry
    which eats precious server resources. In addition, complex regex are hard to understand
    and can be hard to maintain. That is why this function splits the task into multiple
    sections.

    #. Regex expression which matches all exclude tags within the html is used
       to split the HTML split into components. Since the regex expression is
       wrapped inside a group, the content of the exclude tags is also included
       inside the resulting split list.
       Due to that it is guaranteed that every odd element (if there are any)
       will be the excluded tags.
    #. All the split components are looped and processed in order to construct
       final minified HTML.
    #. All odd indexed elements are not processed and are simply
       appended to final HTML since as explained above, they are guaranteed
       to be content of excluded tags hence do not require minification.
    #. All even indexed elements are minified by stripping whitespace between
       tags and redundant whitespace is stripped in general via simple regex.

    You can notice that the process does not involve parsing HTML since that
    usually adds some overhead (e.g. using beautiful soup). By using 2 regex
    passes this achieves very similar result which performs much better.
    """
    components = RE_EXCLUDE_TAGS.split(html)
    html = ''
    for i, component in enumerate(components):
        if i % 2 == 0:
            component = component.strip()
            component = RE_SPACE_BETWEEN_TAGS.sub('> <', component)
            component = RE_WHITESPACE.sub(' ', component)
            html += component
        else:
            html += component
    return html


class TextExtractorHTMLParser(HTMLParser):
    """
    Custom HTML parser which extracts only text while parsing HTML

    Once the parser parses the HTML, :py:meth:`.get_text`
    can be called which will return extracted text
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []

    def handle_data(self, d):
        """
        Handler for data/text in HTML

        This simply adds the data to the results list this class
        maintains of the extracted html
        """
        self.result.append(d)

    def handle_charref(self, number):
        """
        Handler for processing character references.

        This method handles both decimal (e.g. ``'&gt;' == '&#62;'``) and
        hexadecimal (e.g. ``'&gt;' == '&#x3E;'``) references.
        It does that by simply converting the reference number
        to an integer with appropriate base and then converts
        that number to a character.
        """
        codepoint = int(number[1:], 16) if number[0] in ('x', 'X') else int(number)
        text = six.unichr(codepoint)
        self.result.append(text)
        return text

    def handle_entityref(self, name):
        """
        Handler for processing character references.

        This method handles processing HTML entities (e.g. ``'&gt;'``).
        It first maps the entity name to a codepoint which is a
        unicode character number and then converts that number
        to a unicode character.
        """
        text = six.unichr(name2codepoint[name])
        self.result.append(text)
        return text

    def get_text(self):
        """
        Get extracted text after HTML is parsed.

        Returns
        -------
        str
            Extracted text from the HTML document
        """
        return ''.join(self.result)


def html_to_text(html):
    """
    Function to convert HTML text to plain text by stripping all HTML.

    Implementation is based from
    `<http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python>`_.
    """
    s = TextExtractorHTMLParser()
    s.feed(html)
    return s.get_text()
