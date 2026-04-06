# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - HTML Parser

    @copyright: 2006 MoinMoin:AlexanderSchremmer
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.support.htmlmarkup import Markup

# HTMLParseError was removed from html.parser in Python 3.5+
class HTMLParseError(Exception):
    def __init__(self, msg='', position=(None, None)):
        super().__init__(msg)
        self.msg = msg
        self.lineno = position[0]
        self.offset = position[1]

Dependencies = []

class Parser:
    """
        Sends HTML code after filtering it.
    """

    extensions = ['.htm', '.html']
    Dependencies = Dependencies

    def __init__(self, raw, request, **kw):
        self.raw = raw
        self.request = request

    def format(self, formatter, **kw):
        """ Send the text. """
        try:
            self.request.write(formatter.rawHTML(Markup(self.raw).sanitize()))
        except HTMLParseError as e:
            self.request.write(formatter.sysmsg(1) +
                formatter.text(u'HTML parsing error: %s in "%s"' % (e.msg,
                                  self.raw.splitlines()[e.lineno - 1].strip())) +
                formatter.sysmsg(0))
