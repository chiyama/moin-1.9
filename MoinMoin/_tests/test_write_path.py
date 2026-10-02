# -*- coding: utf-8 -*-
"""
    MoinMoin - write path behind a reverse proxy (Py3 port)

    Setup under test: the proxy authenticates and passes the user name in a
    Remote-User header (WSGI: HTTP_REMOTE_USER), GivenAuth turns it into a
    wiki user, XML-RPC v2 is enabled, and the ACL lets only named users write.

    @license: GNU GPL, see COPYING for details.
"""
import re
import shutil
import xmlrpc.client

import pytest

from MoinMoin import wikiutil
from MoinMoin.auth import GivenAuth
from MoinMoin.config import multiconfig
from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from MoinMoin.user import User
from MoinMoin._tests import wikiconfig

AGENT = u'claude-agent'
PAGENAME = u'AutoCreatedWritePathTestPage'


def test_clean_input_str():
    """vulnerabilities.md P-2: str input must not be decoded again."""
    assert wikiutil.clean_input(u'a\tb\nc') == u'a b c'
    assert wikiutil.clean_input(u'') == u''


@pytest.mark.parametrize("environ_value, expected", [
    ('claude-agent', u'claude-agent'),
    # PEP 3333: environ values are latin-1 decoded bytes; the proxy sent UTF-8
    (u'山田'.encode('utf-8').decode('iso-8859-1'), u'山田'),
])
def test_given_auth_decode_username(environ_value, expected):
    """vulnerabilities.md P-4: no str.decode(); recover UTF-8 names from WSGI environ."""
    assert GivenAuth(coding='utf-8').decode_username(environ_value) == expected
    assert GivenAuth().decode_username(environ_value) == expected


class TestWritePath:
    class Config(wikiconfig.Config):
        auth = [GivenAuth(env_var='HTTP_REMOTE_USER', autocreate=True)]
        actions_excluded = [a for a in multiconfig.DefaultConfig.actions_excluded if a != 'xmlrpc']
        acl_rights_default = u"%s,EditorUser:read,write,delete,revert All:read" % AGENT
        # keep the GivenAuth user for XML-RPC (default True replaces it with an
        # invalid user, so that only getAuthToken/applyAuthToken can log in)
        xmlrpc_overwrite_user = False

    def teardown_method(self, method):
        # nuke_page() would be denied by this ACL; remove the page directory instead
        path = Page(self.request, PAGENAME).getPagePath(use_underlay=0, check_create=0)
        shutil.rmtree(path, ignore_errors=True)

    def _rpc(self, method, params, remote_user=None):
        headers = {'Content-Type': 'text/xml'}
        if remote_user:
            headers['Remote-User'] = remote_user
        appiter, status, _ = self.client.post('/?action=xmlrpc2', headers=headers,
                                              data=xmlrpc.client.dumps(params, method))
        body = b''.join(appiter)
        assert status[:3] == '200', body[:500]
        return xmlrpc.client.loads(body)[0][0]

    def test_xmlrpc_put_get_as_given_user(self):
        """vulnerabilities.md P-5: xmlrpc2 putPage/getPage work for the proxy-authenticated user."""
        text = u'= Test =\n日本語の本文\n'
        assert self._rpc('putPage', (PAGENAME, text), remote_user=AGENT) is True
        assert self._rpc('getPage', (PAGENAME, ), remote_user=AGENT) == text
        assert self._rpc('getPage', (PAGENAME, )) == text  # anonymous may read
        info = self._rpc('getPageInfo', (PAGENAME, ))
        assert info['author'] == u'Self:' + AGENT

    def test_xmlrpc_whoami(self):
        """WhoAmI returns the user name as text, not as a bytes repr."""
        assert self._rpc('WhoAmI', (), remote_user=AGENT) == u'You are %s. valid=1.' % AGENT

    def test_xmlrpc_put_anonymous_rejected(self):
        with pytest.raises(xmlrpc.client.Fault):
            self._rpc('putPage', (PAGENAME, u'spam\n'))
        assert not Page(self.request, PAGENAME).exists()

    def test_xmlrpc_put_unlisted_user_rejected(self):
        with pytest.raises(xmlrpc.client.Fault):
            self._rpc('putPage', (PAGENAME, u'spam\n'), remote_user=u'SomeoneElse')
        assert not Page(self.request, PAGENAME).exists()

    def test_editor_shown_only_to_given_user(self):
        appiter, status, _ = self.client.get('/%s?action=edit&editor=text' % PAGENAME,
                                             headers={'Remote-User': 'EditorUser'})
        assert status[:3] == '200'
        assert 'name="savetext"' in b''.join(appiter).decode('utf-8')
        appiter, status, _ = self.client.get('/%s?action=edit&editor=text' % PAGENAME)
        assert 'name="savetext"' not in b''.join(appiter).decode('utf-8')

    def test_web_save_as_given_user_and_anonymous(self):
        """Edit form POST: saves for the named user, rejected for anonymous."""
        def post(remote_user, text):
            headers = {'Remote-User': remote_user} if remote_user else {}
            # like a browser: view a page first, then keep the session cookie.
            # The ticket is bound to the session id, and createTicket() treats
            # a still-empty session as no session (same as upstream 1.9.11).
            appiter, status, resp_headers = self.client.get('/FrontPage', headers=headers)
            b''.join(appiter)
            cookie = resp_headers.get('Set-Cookie')
            if cookie:
                headers['Cookie'] = cookie.split(';')[0]
            appiter, status, _ = self.client.get('/%s?action=edit&editor=text' % PAGENAME, headers=headers)
            form = b''.join(appiter).decode('utf-8')
            fields = {'action': 'edit', 'editor': 'text', 'button_save': 'Save Changes',
                      'savetext': text, 'comment': u'コメント\tあり', 'category': ''}
            for name in ('ticket', 'rev'):
                m = re.search(r'name="%s" value="([^"]*)"' % name, form)
                if m:
                    fields[name] = m.group(1)
            appiter, status, _ = self.client.post('/%s' % PAGENAME, headers=headers, data=fields)
            return status, b''.join(appiter).decode('utf-8')

        status, body = post(None, u'spam\n')
        assert status[:3] != '500'
        assert not Page(self.request, PAGENAME).exists()

        status, body = post('EditorUser', u'hello\n')
        assert status[:3] in ('200', '302'), body[:500]
        page = Page(self.request, PAGENAME)
        assert page.exists()
        assert page.get_raw_body() == u'hello\n'

    def test_page_editor_anonymous_rejected(self):
        request = self.request
        saved_user = request.user
        request.user = User(request)  # anonymous
        try:
            with pytest.raises(PageEditor.AccessDenied):
                PageEditor(request, PAGENAME).saveText(u'spam\n', 0)
        finally:
            request.user = saved_user
