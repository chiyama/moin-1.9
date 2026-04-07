# -*- coding: utf-8 -*-
"""
    MoinMoin - Smoke Tests & Full-Page Scan (Integration)

    Two layers of integration tests:

    1. Regression tests (TestSmoke)
       - One test per error pattern found during Py3 migration crawl (2026-04-07).
       - Fast (<1s), run on every commit.

    2. Full-page scan (TestAllPages)
       - GET every wiki page; assert no 500 errors.
       - Marked ``@pytest.mark.slow``; skip by default.
       - Run explicitly: ``pytest -m slow`` or ``pytest --run-slow``

    Background
    ----------
    During the Python 2 → 3 migration, a full-site crawl (300 pages) revealed
    6 distinct error patterns, all caused by str/bytes confusion, removed stdlib
    modules, or changed built-in semantics.  The regression tests pin each fix
    so it cannot silently regress.

    The full-page scan catches *new* breakage across the entire wiki (1898 pages)
    in ~70 seconds via the in-process werkzeug Client (no HTTP server needed).

    Errors found and fixed (2026-04-07)
    ------------------------------------
    1. AttachFile._get_files     — os.listdir returns str in Py3, not bytes
    2. AttachFile.getFilename    — filename must stay str for os.path.join
    3. PageEditor.sendEditor     — "hidden".decode(...) syntax, html.INPUT str()
    4. action/info.py:37         — SyntaxError from botched .encode() insertion
    5. queryparser.parse_query   — str has no .decode(); guard should be bytes
    6. formatter.rawHTML         — formatter/htmllib removed in Py3.x
    7. SpellCheck.checkSpelling  — sort(lambda) → sort(key=)
    8. wikiutil.createTicket     — time.time() returns float; %x needs int
    9. wikiutil.createTicket     — hmac.new needs bytes key and msg
    10. Page.getPageList          — list(filter(name)) → filter(name)

    @copyright: 2026 MoinMoin:py3-migration
    @license: GNU GPL, see COPYING for details.
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _WikiClient:
    """Mixin providing a ``_get`` helper for werkzeug Client."""

    def _get(self, path):
        """Issue GET via werkzeug Client, return (status_str, body_str)."""
        appiter, status, headers = self.client.get(path)
        body = b''.join(appiter).decode('utf-8', errors='replace')
        return status, body

    def _assert_no_500(self, path):
        """Assert the path does not return HTTP 500."""
        try:
            status, body = self._get(path)
        except Exception as exc:
            pytest.fail(f"GET {path} raised {type(exc).__name__}: {exc}")
        assert status[:3] != '500', (
            f"GET {path} returned 500"
        )
        return status, body


# ---------------------------------------------------------------------------
# 1. Regression tests — one per known error pattern
# ---------------------------------------------------------------------------

class TestSmoke(_WikiClient):
    """Smoke tests: one request per error pattern found in crawl 2026-04-07."""

    def test_page_view_basic(self):
        """Basic page rendering (no attachments)."""
        status, body = self._get('/LanguageSetup')
        assert status[:3] == '200'

    def test_page_view_with_attachments(self):
        """Page with attachment dir: AttachFile._get_files / getFilename."""
        status, body = self._get('/WikiSandBox')
        assert status[:3] == '200'

    def test_action_edit(self):
        """Text editor: PageEditor.sendEditor (html.INPUT, makeSelection)."""
        status, body = self._get('/FrontPage?action=edit&editor=text')
        # 200 whether permitted or denied; must not be 500
        assert status[:3] == '200'

    def test_action_info(self):
        """Page info/history: action/info.py SHA digest computation."""
        status, body = self._get('/FrontPage?action=info')
        assert status[:3] == '200'

    def test_action_fullsearch(self):
        """Full-text search: queryparser.parse_query, Page.getPageList filter."""
        status, body = self._get('/LanguageSetup?action=fullsearch&value=wiki')
        assert status[:3] == '200'

    def test_action_newaccount(self):
        """New account form: wikiutil.createTicket (hmac, time.time int cast)."""
        status, body = self._get('/LanguageSetup?action=newaccount')
        assert status[:3] == '200'

    def test_action_format_plaintext(self):
        """Plain-text formatter: formatter.rawHTML (replaced formatter/htmllib)."""
        status, body = self._get('/LanguageSetup?action=format&mimetype=text/plain')
        assert status[:3] == '200'


# ---------------------------------------------------------------------------
# 2. Full-page scan — every page, no 500
# ---------------------------------------------------------------------------

def _get_all_pagenames():
    """Return sorted list of all page names from the test wiki."""
    from MoinMoin._tests import wikiconfig, maketestwiki
    from MoinMoin.web.request import TestRequest
    from MoinMoin.wsgiapp import init

    maketestwiki.run(True)
    req = TestRequest()
    req.given_config = wikiconfig.Config
    req = init(req)
    pages = req.rootpage.getPageList(include_underlay=True)
    return sorted(pages)


# Build page list once at import time (fast, no HTTP)
_ALL_PAGES = _get_all_pagenames()


@pytest.mark.slow
class TestAllPages(_WikiClient):
    """GET every wiki page and assert no 500 Internal Server Error.

    Run with::

        python -m pytest MoinMoin/_tests/test_smoke.py -m slow --run-slow -v

    Pages that return 200, 302, 404, or 403 are acceptable — only 500
    (server crash) constitutes a failure.
    """

    @pytest.mark.parametrize("pagename", _ALL_PAGES)
    def test_page_no_500(self, pagename):
        self._assert_no_500('/' + pagename)
