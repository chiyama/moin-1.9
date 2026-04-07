# MoinMoin Modernization Work Guide

This document is a session-based work plan for bringing MoinMoin to a production-ready
state after the Python 3 migration. Each session can be executed independently;
dependencies on prior sessions are noted where applicable.

Track progress by updating the Status of each item.

## Status Legend

- `[ ]` Not started
- `[~]` In progress / partially complete
- `[x]` Complete / verified

---

## Session 1: Page Editing (PageEditor)

**Target modules**: `PageEditor.py`, `action/edit.py`, `action/Save.py`, `caching.py`

**Goal**: Wiki page creation, editing, and saving work correctly

**Background**: Page viewing (Page.py) currently works, but the edit/save path is unverified.
str/bytes boundary issues are highly likely.

### Work Items

- [ ] `action/edit.py` — Verify edit form rendering
- [ ] `PageEditor.py` — Fix `saveText()` file write path
  - `codecs.open()` → `open(encoding='utf-8')`
  - Verify file locking behavior
- [ ] `caching.py` — Fix cache read/write
  - Confirm pickle read/write operates on bytes
  - Audit `open()` modes (binary vs text)
- [ ] `action/Save.py` — Verify save action

### Verification

```bash
# 1. Start server
python wikiserver.py

# 2. In browser:
# - Navigate to http://localhost:8080/TestPage?action=edit
# - Enter text and save
# - Confirm the saved page renders correctly

# 3. Programmatic verification
python -c "
from MoinMoin.web.request import Client
from MoinMoin.wsgiapp import Application
client = Client(Application())
# Get edit form
resp = client.get('/TestPage?action=edit')
print('Edit form:', resp[1])
"
```

### Done Criteria

- New pages can be created
- Existing pages can be edited and saved
- Saved pages render correctly

---

## Session 2: User Management (user, auth)

**Target modules**: `user.py`, `auth/__init__.py`, `action/login.py`, `action/newaccount.py`, `action/recoverpass.py`

**Goal**: User registration, login, and logout work correctly

**Background**: `user.py` reads/writes profiles with `codecs.open()`, and passwords are
hashed via passlib (bundled). The `hashlib` encoding issue has been fixed, but the
profile read/write path is unverified.

### Work Items

- [ ] `user.py` — User profile read/write
  - `codecs.open()` → `open(encoding='utf-8')`
  - Verify str/bytes in `save()` and `load()`
- [ ] `auth/__init__.py` — Verify MoinAuth (built-in auth) flow
- [ ] `action/newaccount.py` — Account creation
- [ ] `action/login.py` — Login form
- [ ] `action/recoverpass.py` — Password reset
- [ ] Password hash verification (passlib integration)

### Verification

```bash
# In browser:
# 1. Create account at http://localhost:8080/?action=newaccount
# 2. Log out, then log back in
# 3. Access user preferences page
```

### Done Criteria

- New users can be created
- Login and logout work
- User profiles are persisted

---

## Session 3: Attachments (AttachFile)

**Target modules**: `action/AttachFile.py`, `action/Load.py`

**Goal**: File upload, download, and listing work correctly

**Background**: Attachments are binary data, so `open('rb')`/`open('wb')` is likely
already correct. However, filename encoding and form processing may have issues.

### Work Items

- [ ] `action/AttachFile.py` — Upload handling (`_do_upload`)
  - Multipart form data processing
  - Filename str/bytes
- [ ] `action/AttachFile.py` — Download handling (`_do_get`)
  - Content-Type, Content-Disposition headers
- [ ] `action/AttachFile.py` — File listing
- [ ] `action/Load.py` — Page content upload

### Verification

```bash
# 1. Create a test page (requires Session 1)
# 2. Upload an attachment
# 3. Verify attachment listing
# 4. Download the attachment
# 5. Test with non-ASCII filenames
```

### Done Criteria

- Both text and binary files can be uploaded
- Uploaded files can be downloaded
- Attachment listing renders correctly

---

## Session 4: Log Files and History (logfile, diff, info)

**Target modules**: `logfile/__init__.py`, `logfile/editlog.py`, `action/diff.py`, `action/info.py`

**Goal**: Page edit history and diff views work correctly

**Background**: Log files are opened in binary mode (`rb`/`ab`) and decoded line by line.
The basic read path has been fixed, but edit log parsing and diff display are unverified.

### Work Items

- [ ] `logfile/editlog.py` — EditLog entry parsing
  - Tab-delimited line parsing
  - Timestamp, username, page name decoding
- [ ] `action/info.py` — Page info / history view
- [ ] `action/diff.py` — Revision diff display
- [ ] `util/diff_html.py` — HTML diff rendering

### Verification

```bash
# 1. Edit a page at least twice (requires Session 1)
# 2. View history at http://localhost:8080/TestPage?action=info
# 3. Display diff between two revisions
```

### Done Criteria

- Page edit history displays correctly
- Diffs between revisions are shown

---

## Session 5: Search

**Target modules**: `search/__init__.py`, `search/builtin.py`, `search/queryparser/`, `action/fullsearch.py`

**Goal**: Built-in search (no Xapian required) works correctly

### Work Items

- [ ] `search/builtin.py` — Verify MoinSearch operation
- [ ] `search/queryparser/` — Query parser str handling
- [ ] `action/fullsearch.py` — Search results page rendering

### Verification

```bash
# 1. Search at http://localhost:8080/?action=fullsearch&value=MoinMoin
# 2. Test with non-ASCII keywords
```

### Done Criteria

- Page title search works
- Full-text search works
- Search results link correctly

---

## Session 6: Security (ACL)

**Target modules**: `security/__init__.py`, `security/textcha.py`, `security/antispam.py`

**Goal**: ACL (Access Control Lists) work correctly

### Work Items

- [ ] `security/__init__.py` — ACL parsing and evaluation
- [ ] Verify read/write restrictions via ACL
- [ ] `security/textcha.py` — Text CAPTCHA
- [ ] `security/antispam.py` — Anti-spam measures

### Verification

```bash
# 1. Configure ACL in wikiconfig.py
# 2. Verify permission differences between anonymous and logged-in users
# 3. Test: python -m pytest MoinMoin/security/_tests/test_security.py -v
```

### Done Criteria

- Access control based on ACL settings works
- Test suite passes

---

## Session 7: Email Notifications (mail, events)

**Target modules**: `mail/sendmail.py`, `events/__init__.py`, `events/emailnotify.py`

**Goal**: Email notifications on page changes work correctly

### Work Items

- [ ] `mail/sendmail.py` — SMTP sending
  - Mail header str/bytes
  - MIME encoding
- [ ] `events/__init__.py` — Event dispatch
- [ ] `events/emailnotify.py` — Email notification handler

### Verification

```bash
# 1. Configure mail_from and mail_smarthost in wikiconfig.py
# 2. Subscribe to a page, then edit it as a different user
# 3. Confirm email is sent
```

---

## Session 8: XMLRPC API

**Target modules**: `xmlrpc/__init__.py`, `xmlrpc/*.py`

**Goal**: Page retrieval and updates via XMLRPC work correctly

### Work Items

- [ ] `xmlrpc/__init__.py` — Verify XmlRpcBase operation
- [ ] `xmlrpc.client` bytes/str handling
- [ ] Basic APIs: getPage, putPage, listPages

### Verification

```python
import xmlrpc.client
s = xmlrpc.client.ServerProxy('http://localhost:8080/?action=xmlrpc2')
print(s.getAllPages())
```

---

## Session 9: Parsers and Formatters

**Target modules**: `parser/`, `formatter/`

**Goal**: All markup parsing and output rendering work correctly

### Work Items

- [ ] `parser/text_moin_wiki.py` — Full feature test of the main parser
- [ ] `parser/highlight.py` — Pygments integration (code blocks)
- [ ] `parser/text_csv.py` — CSV tables
- [ ] `parser/text_rst.py` — reStructuredText (requires docutils)
- [ ] `formatter/text_html.py` — HTML output verification
- [ ] `formatter/text_plain.py` — Plain text output

### Verification

```bash
# Create test pages with various markup and verify rendering:
# - Headings, lists, tables, links, images
# - Code blocks ({{{#!python ... }}})
# - Macros (<<TableOfContents>>, <<Include(...)>>)
```

---

## Session 10: Test Suite Modernization

**Target modules**: `_tests/`, each package's `_tests/`

**Goal**: Significantly improve test suite pass rate

### Work Items

- [ ] `_tests/test_wikiutil.py` — Rewrite yield-based tests to `@pytest.mark.parametrize`
- [ ] `_tests/test_wsgiapp.py` — Same as above
- [ ] Check test pass status in each package's `_tests/`
- [ ] Improve `conftest.py` (as needed)
- [ ] `imp` → `importlib` migration (`config/multiconfig.py`)

### Verification

```bash
# Run all tests
python -m pytest MoinMoin/ -v --ignore=MoinMoin/support/ -k "not xapian and not ldap and not openid" --tb=short 2>&1 | tail -20
```

### Done Criteria

- Test pass rate above 80%
- All yield-based tests converted to parametrize

---

## Session 11: codecs.open Cleanup and Remaining Python 2 Code Removal

**Target**: All modules (cross-cutting)

**Goal**: Remove all remaining Python 2 patterns

### Work Items

- [ ] `codecs.open()` → `open(encoding=)` (17 files)
- [ ] `imp` module → `importlib` (multiconfig.py)
- [ ] Remove remaining `unicode` type references (including docstrings)
- [ ] Remove `# -*- coding: iso-8859-1 -*-` headers
- [ ] Replace remaining `has_key()` calls with `in`

### Verification

```bash
# Search for remaining patterns
grep -rn "codecs.open" MoinMoin/ --include="*.py" | grep -v /support/
grep -rn "import imp" MoinMoin/ --include="*.py" | grep -v /support/
grep -rn "has_key" MoinMoin/ --include="*.py" | grep -v /support/
```

---

## Dependency Graph

```
Session 1 (PageEditor)  ← Foundation. Prerequisite for many other sessions
    ↓
Session 2 (user/auth)   ← Prerequisite for Sessions 3, 6, 7
    ↓
Session 3 (AttachFile)
Session 4 (logfile/diff) ← Can start anytime after Session 1
Session 5 (search)       ← Can be executed independently
Session 6 (security)     ← After Session 2
Session 7 (mail)         ← After Session 2
Session 8 (XMLRPC)       ← Can be executed independently
Session 9 (parser)       ← Can be executed independently
Session 10 (tests)       ← Ideally after all sessions, but can start earlier
Session 11 (cleanup)     ← Execute last
```

---

## Session 12: Documentation Update for Python 3

**Target**: `docs/INSTALL.html`, `docs/UPDATE.html`, `docs/resetpw/`

**Goal**: Update legacy Python 2 documentation for Python 3

### Work Items

- [ ] `docs/INSTALL.html` — Rewrite installation instructions for Python 3.10+
  - Update all Python 2.7 references
  - Remove flup / CGI instructions, replace with WSGI server instructions
- [ ] `docs/UPDATE.html` — Rewrite update instructions for Python 3
- [ ] `docs/resetpw/` — Verify and update password reset instructions for Python 3
  - Verify moin CLI command operation
  - Check template character encoding

### Done Criteria

- No Python 2.7 references remain in any document
- All documented procedures actually work
