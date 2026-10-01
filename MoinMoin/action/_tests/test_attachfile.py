# -*- coding: utf-8 -*-
"""
    MoinMoin - tests of AttachFile action

    @copyright: 2007 by Karol Nowak <grywacz@gmail.com>
                2007-2008 MoinMoin:ReimarBauer
    @license: GNU GPL, see COPYING for details.
"""
import os, io
from MoinMoin import wikiutil
from MoinMoin.Page import Page
from MoinMoin.action import AttachFile
from MoinMoin.PageEditor import PageEditor
from MoinMoin._tests import become_trusted, create_page, nuke_page

class TestAttachFile:
    """ testing action AttachFile"""
    pagename = u"AutoCreatedSillyPageToTestAttachments"

    def test_add_attachment(self):
        """Test if add_attachment() works"""

        become_trusted(self.request)
        filename = "AutoCreatedSillyAttachment"

        create_page(self.request, self.pagename, u"Foo!")

        AttachFile.add_attachment(self.request, self.pagename, filename, "Test content", True)
        exists = AttachFile.exists(self.request, self.pagename, filename)

        nuke_page(self.request, self.pagename)

        assert exists

    def test_add_attachment_for_file_object(self):
        """Test if add_attachment() works with file like object"""

        become_trusted(self.request)

        filename = "AutoCreatedSillyAttachment.png"

        create_page(self.request, self.pagename, u"FooBar!")
        data = "Test content"

        filecontent = io.StringIO(data)

        AttachFile.add_attachment(self.request, self.pagename, filename, filecontent, True)
        exists = AttachFile.exists(self.request, self.pagename, filename)
        path = AttachFile.getAttachDir(self.request, self.pagename)
        imagef = os.path.join(path, filename)
        file_size = os.path.getsize(imagef)

        nuke_page(self.request, self.pagename)

        assert exists and file_size == len(data)

    def test_get_attachment_path_created_on_getFilename(self):
        """
        Tests if AttachFile.getFilename creates the attachment dir on self.requesting
        """
        become_trusted(self.request)

        filename = ""

        file_exists = os.path.exists(AttachFile.getFilename(self.request, self.pagename, filename))

        nuke_page(self.request, self.pagename)

        assert file_exists


class TestAttachFilePy3:
    """ str/bytes boundary of attachment storage and embedding (Py3 port) """
    pagename = u"AutoCreatedSillyPageToTestAttachmentsPy3"
    # PNG signature: contains \r\n and \x1a, so any text-mode handling corrupts it
    data = b"\x89PNG\r\n\x1a\n" + bytes(range(256))

    def setup_method(self, method):
        become_trusted(self.request)
        create_page(self.request, self.pagename, u"Foo!")

    def teardown_method(self, method):
        nuke_page(self.request, self.pagename)

    def _read(self, filename):
        fpath = AttachFile.getFilename(self.request, self.pagename, filename)
        with open(fpath, 'rb') as f:
            return f.read()

    def test_add_attachment_bytes(self):
        target, size = AttachFile.add_attachment(self.request, self.pagename, u"pic.png", self.data)
        assert (target, size) == (u"pic.png", len(self.data))
        assert self._read(u"pic.png") == self.data

    def test_add_attachment_binary_file_object(self):
        AttachFile.add_attachment(self.request, self.pagename, u"pic.png", io.BytesIO(self.data))
        assert self._read(u"pic.png") == self.data

    def test_non_ascii_filename_add_move_copy(self):
        name = u"写真.png"
        AttachFile.add_attachment(self.request, self.pagename, name, self.data)
        assert AttachFile._get_files(self.request, self.pagename) == [name]
        AttachFile.copy_attachment(self.request, self.pagename, self.pagename, name, u"コピー.png")
        AttachFile.move_attachment(self.request, self.pagename, self.pagename, name, u"移動.png")
        assert AttachFile._get_files(self.request, self.pagename) == sorted([u"コピー.png", u"移動.png"])
        assert self._read(u"移動.png") == self.data

    def test_container_put_get_bytes(self):
        ci = AttachFile.ContainerItem(self.request, self.pagename, u"drawing.tdraw")
        ci.truncate()
        ci.put('drawing.png', self.data)
        ci.put('drawing.map', u'<map name="%MAPNAME%"></map>')
        assert ci.get('drawing.png').read() == self.data
        assert ci.get('drawing.map').read() == b'<map name="%MAPNAME%"></map>'

    def test_content_disposition(self):
        assert AttachFile._content_disposition('inline', u'pic.png') == 'inline; filename="pic.png"'
        value = AttachFile._content_disposition('attachment', u'写真.png')
        value.encode('latin-1')  # WSGI header values must be latin-1
        assert value == "attachment; filename=\"??.png\"; filename*=UTF-8''%E5%86%99%E7%9C%9F.png"

    def test_embed_existing_attachment(self):
        create_page(self.request, self.pagename, u"{{attachment:pic.png}} [[attachment:pic.png]]")
        AttachFile.add_attachment(self.request, self.pagename, u"pic.png", self.data)
        page = Page(self.request, self.pagename)
        self.request.page = page
        html = self.request.redirectedOutput(page.send_page, content_only=1)
        assert 'do=get&amp;target=pic.png' in html
        assert 'nonexistent' not in html

    def test_dump_copies_attachment(self, tmp_path):
        from MoinMoin.script.export import dump
        AttachFile.add_attachment(self.request, self.pagename, u"写真.png", self.data)
        url = dump._attachment(self.request, self.pagename, u"写真.png", str(tmp_path))
        assert url == "attachments/%s/%%E5%%86%%99%%E7%%9C%%9F.png" % wikiutil.quoteWikinameFS(self.pagename)
        copied = tmp_path / "attachments" / wikiutil.quoteWikinameFS(self.pagename) / u"写真.png"
        assert copied.read_bytes() == self.data
        assert dump._attachment(self.request, self.pagename, u"missing.png", str(tmp_path)) == ""


coverage_modules = ['MoinMoin.action.AttachFile']
