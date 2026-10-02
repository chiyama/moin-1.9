# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - MoinMoin.Page Tests

    @copyright: 2007 MoinMoin:ThomasWaldmann
    @license: GNU GPL, see COPYING for details.
"""

import py
import pytest

from MoinMoin.Page import Page

class TestPage:
    def testMeta(self):
        page = Page(self.request, u'FrontPage')
        meta = page.meta
        for k, v in meta:
            if k == u'format':
                assert v == u'wiki'
            elif k == u'language':
                assert v == u'en'

    def testBody(self):
        page = Page(self.request, u'FrontPage')
        body = page.body
        assert isinstance(body, str)
        assert 'MoinMoin' in body
        assert body.endswith('\n')
        assert '\r' not in body

    def testExists(self):
        assert Page(self.request, 'FrontPage').exists()
        assert not Page(self.request, 'ThisPageDoesNotExist').exists()
        assert not Page(self.request, '').exists()

    def testEditInfoSystemPage(self):
        # system pages have no edit-log (and only 1 revision),
        # thus edit_info will return None
        page = Page(self.request, u'RecentChanges')
        edit_info = page.edit_info()
        assert edit_info == {}

    def testSplitTitle(self):
        page = Page(self.request, u"FrontPage")
        assert page.split_title(force=True) == u'Front Page'

    def testGetRevList(self):
        page = Page(self.request, u"FrontPage")
        assert 1 in page.getRevList()

    def testGetPageLinks(self):
        page = Page(self.request, u"FrontPage")
        assert u'WikiSandBox' in page.getPageLinks(self.request)

    def testSendPage(self):
        page = Page(self.request, u"FrontPage")
        import io
        out = io.StringIO()
        self.request.redirect(out)
        page.send_page(msg=u'Done', emit_headers=False)
        result = out.getvalue()
        self.request.redirect()
        del out
        assert result.strip().endswith('</html>')
        assert result.strip().startswith('<!DOCTYPE HTML PUBLIC')

    def testLoadCacheRejectsOtherPythonBytecode(self):
        """ a cache written by another Python version is rebuilt, not executed

        Executing marshalled code from another Python version can crash the
        interpreter (seen: 3.10 cache executed by 3.14).
        """
        import marshal
        from MoinMoin import caching
        page = Page(self.request, u"FrontPage")
        page.send_page(content_only=1)  # make sure the cache exists
        cache = caching.CacheEntry(self.request, page, page.getFormatterName(), scope='item')
        assert page.loadCache(self.request) is not None
        # cache in the old format: marshal data without a version tag
        cache.update(marshal.dumps(compile('pass', 'x', 'exec')))
        with pytest.raises(Exception) as excinfo:
            page.loadCache(self.request)
        assert str(excinfo.value) == 'CacheNeedsUpdate'

class TestRootPage:
    def testPageList(self):
        rootpage = self.request.rootpage
        pagelist = rootpage.getPageList()
        assert len(pagelist) > 100
        assert u'FrontPage' in pagelist
        assert u'' not in pagelist


coverage_modules = ['MoinMoin.Page']

