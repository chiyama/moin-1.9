# MoinMoin 1.9 Architecture Guide

This document maps the entire MoinMoin module structure for developers working on
the Python 3 port. Each module includes its purpose, maturity level after migration,
key files, and what remains to be done.

## Maturity Levels

| Level | Meaning |
|-------|---------|
| **OK** | Imports and runs correctly on Python 3.10 |
| **PARTIAL** | Imports successfully but has known runtime str/bytes issues |
| **UNTESTED** | Imports successfully but not yet exercised at runtime |
| **OPTIONAL** | Requires external library not installed (ldap, openid, etc.) |

---

## Request Lifecycle

A request flows through these modules in order:

```
wikiserver.py
  -> MoinMoin/script/server/standalone.py  (werkzeug run_simple)
    -> MoinMoin/wsgiapp.py                 (WSGI Application.__call__)
      -> MoinMoin/web/contexts.py          (AllContext wraps Request)
      -> MoinMoin/config/multiconfig.py    (load wiki configuration)
      -> MoinMoin/auth/                    (authenticate user)
      -> MoinMoin/i18n/                    (setup language)
      -> MoinMoin/action/                  (dispatch to action handler)
        -> MoinMoin/Page.py                (load page from filesystem)
        -> MoinMoin/parser/                (parse wiki markup)
        -> MoinMoin/formatter/             (render to HTML)
        -> MoinMoin/theme/                 (wrap in page template)
      <- HTTP Response
```

---

## Core Modules (MoinMoin/)

### Page.py — Page Reading
- **What**: Read-only access to wiki pages. `Page` and `RootPage` classes.
- **Maturity**: OK
- **Key concerns**: `codecs.open()` for page body, filesystem encoding
- **Tests**: `_tests/test_Page.py`
- **TODO**: Replace `codecs.open()` with `open(encoding=)`

### PageEditor.py — Page Writing
- **What**: Page editing, saving, renaming, deleting. Extends Page with write ops.
- **Maturity**: UNTESTED (read works, write path not yet exercised)
- **Key concerns**: File locking, conflict resolution, `codecs.open()` for saves
- **Tests**: `_tests/test_PageEditor.py` (some pass, some fail on str/bytes)
- **TODO**: Fix save path str/bytes, test edit/save cycle

### user.py — User Management
- **What**: User profiles, password hashing, login/logout state.
- **Maturity**: PARTIAL
- **Key concerns**: `hashlib` encoding (fixed), password scheme migration, `codecs.open()` for profiles
- **Dependencies**: passlib (bundled)
- **Tests**: `_tests/test_user.py` (some fail)
- **TODO**: Fix profile read/write encoding, test password verification

### wikiutil.py — Wiki Utilities
- **What**: ~2500-line utility module. URL quoting, plugin loading, text processing, argument parsing.
- **Maturity**: OK (core paths work)
- **Key functions**: `quoteWikinameFS`, `unquoteWikiname`, `escape`, `getFrontPage`, plugin loading
- **Tests**: `_tests/test_wikiutil.py` (yield-based, needs rewrite)
- **TODO**: Rewrite yield-based tests to parametrize, audit remaining `unicode` refs in docstrings

### wsgiapp.py — WSGI Entry Point
- **What**: Main `Application` class. `init()` -> `run()` -> `dispatch()` -> `handle_action()`.
- **Maturity**: OK
- **Tests**: `_tests/test_wsgiapp.py` (yield-based, needs rewrite)

### caching.py — Disk Cache
- **What**: Page and item caching with pickle support.
- **Maturity**: PARTIAL
- **Key concerns**: Pickle protocol, binary vs text mode, cache invalidation
- **Tests**: `_tests/test_caching.py` (some fail on str/bytes)
- **TODO**: Audit open() modes, verify pickle read/write

### error.py — Error Classes
- **What**: Base `Error`, `CompositeError`, `FatalError`, `ConfigurationError`.
- **Maturity**: OK
- **Tests**: `_tests/test_error.py` (4/4 pass)

### log.py — Logging Setup
- **What**: Configures Python logging. Loads `wikiserverlogging.conf`.
- **Maturity**: OK (fixed `_levelNames` -> `_levelToName`)

### packages.py — Extension Packages
- **What**: Install/uninstall page packages (ZIP bundles of wiki pages).
- **Maturity**: UNTESTED
- **Tests**: `_tests/test_packages.py` (fails on str/bytes)

### wikisync.py — Wiki Synchronization
- **What**: Sync pages between wikis via XMLRPC.
- **Maturity**: UNTESTED
- **Tests**: `_tests/test_wikisync.py`

---

## Web Layer (MoinMoin/web/)

| File | Purpose | Maturity |
|------|---------|----------|
| `request.py` | Request/Response (werkzeug wrappers) | OK |
| `contexts.py` | AllContext, HTTPContext, ScriptContext | OK |
| `session.py` | Session management (secure_cookie) | UNTESTED |
| `serving.py` | Standalone server logging | OK |
| `utils.py` | Surge protection, forbidden check, UniqueIDGenerator | UNTESTED |
| `exceptions.py` | Forbidden, SurgeProtection HTTP exceptions | OK |
| `static/` | Static files (CSS, JS, images, applets) | OK |

**Dependencies**: werkzeug 1.0.1 (bundled in support/)

**TODO**: Test session persistence, surge protection

---

## Configuration (MoinMoin/config/)

| File | Purpose | Maturity |
|------|---------|----------|
| `__init__.py` | Character type definitions (upper/lower/digit) | OK |
| `multiconfig.py` | Wiki farm config loading, DefaultConfig | OK |

**Key changes made**: `_decode()` is now a no-op (str is already unicode in Py3), `hashlib` calls encode to bytes, `imp` module still used (deprecated warning).

**TODO**: Migrate `imp` -> `importlib`

---

## Actions (MoinMoin/action/) — 52 files

User-triggered operations dispatched from `wsgiapp.handle_action()`.

| Action | File | Purpose | Maturity |
|--------|------|---------|----------|
| show | `__init__.py` | Display page (default) | OK |
| edit | `edit.py` | Edit page | UNTESTED |
| AttachFile | `AttachFile.py` | File attachments | UNTESTED |
| diff | `diff.py` | Show page differences | UNTESTED |
| info | `info.py` | Page info/history | UNTESTED |
| search | `fullsearch.py` | Full-text search | UNTESTED |
| DeletePage | `DeletePage.py` | Delete a page | UNTESTED |
| RenamePage | `RenamePage.py` | Rename a page | UNTESTED |
| CopyPage | `CopyPage.py` | Copy a page | UNTESTED |
| SpellCheck | `SpellCheck.py` | Spell checking | UNTESTED |
| rss_rc | `rss_rc.py` | RSS feed | UNTESTED |
| login | `login.py` | Login form | UNTESTED |
| newaccount | `newaccount.py` | Account creation | UNTESTED |

**Tests**: `_tests/test_attachfile.py`, `_tests/test_cache.py`

**TODO**: Exercise each action through the web interface and fix str/bytes issues as they appear

---

## Authentication (MoinMoin/auth/) — 13 files

| File | Purpose | Maturity |
|------|---------|----------|
| `__init__.py` | BaseAuth, MoinAuth, GivenAuth | PARTIAL |
| `ldap_login.py` | LDAP authentication | OPTIONAL (needs python-ldap) |
| `openidrp.py` | OpenID Relying Party | OPTIONAL (needs openid) |
| `cas.py` | CAS authentication | UNTESTED |
| `php_session.py` | PHP session integration | UNTESTED |
| `mysql_group.py` | MySQL group backend | OPTIONAL (needs MySQLdb) |

**Tests**: `_tests/test_auth.py`, `_tests/test_ldap_login.py`

---

## Parsers (MoinMoin/parser/) — 18 files

Transform wiki markup into formatter calls.

| Parser | File | Purpose | Maturity |
|--------|------|---------|----------|
| MoinMoin wiki | `text_moin_wiki.py` | Main wiki markup | OK (page rendering works) |
| Creole | `_creole.py` | Creole wiki syntax | UNTESTED |
| reStructuredText | `text_rst.py` | RST markup | UNTESTED (needs docutils) |
| HTML | `text_html.py` | HTML passthrough | PARTIAL |
| Syntax highlight | `highlight.py` | Pygments integration | UNTESTED |
| Python | `text_python.py` | Python code highlight | UNTESTED |
| CSV | `text_csv.py` | Table from CSV | UNTESTED |
| DocBook | `text_docbook.py` | DocBook/XSLT | OPTIONAL (needs 4suite) |

**Tests**: `_tests/test_unicode.py`

---

## Formatters (MoinMoin/formatter/) — 11 files

Render parsed content into output formats.

| Formatter | File | Purpose | Maturity |
|-----------|------|---------|----------|
| HTML | `text_html.py` | HTML output (primary) | OK |
| Plain text | `text_plain.py` | Plain text output | UNTESTED |
| DOM XML | `dom_xml.py` | XML DOM output | UNTESTED |
| Page links | `pagelinks.py` | Extract page links | UNTESTED |

---

## Themes (MoinMoin/theme/) — 6 files

| File | Purpose | Maturity |
|------|---------|----------|
| `__init__.py` | ThemeBase class (~2000 lines) | OK |
| `modernized.py` | Default "modernized" theme | OK |
| `classic.py` | Classic MoinMoin theme | UNTESTED |
| `rightsidebar.py` | Right sidebar variant | UNTESTED |

---

## Macros (MoinMoin/macro/) — 41 files

Dynamic content via `<<MacroName>>` syntax.

| Macro | File | Purpose | Maturity |
|-------|------|---------|----------|
| (builtins) | `__init__.py` | TitleIndex, WordIndex, etc. | PARTIAL |
| Include | `Include.py` | Include other pages | UNTESTED |
| TableOfContents | `TableOfContents.py` | Auto TOC | UNTESTED |
| FootNote | `FootNote.py` | Footnotes | UNTESTED |
| EmbedObject | `EmbedObject.py` | Embed media | OK (sort() fixed) |
| RecentChanges | `RecentChanges.py` | Recent changes list | UNTESTED |
| AdvancedSearch | `AdvancedSearch.py` | Search form | UNTESTED |

---

## Data Structures (MoinMoin/datastruct/) 

Wiki-managed groups and dictionaries for ACL and variable substitution.

| Backend | Files | Maturity |
|---------|-------|----------|
| Wiki dicts | `backends/wiki_dicts.py` | OK |
| Wiki groups | `backends/wiki_groups.py` | OK |
| Config dicts | `backends/config_dicts.py` | UNTESTED |
| Config groups | `backends/config_groups.py` | UNTESTED |
| Composite | `backends/composite_*.py` | UNTESTED |

**Key change**: `UserDict.DictMixin` -> `collections.abc.MutableMapping`

---

## Internationalization (MoinMoin/i18n/)

| File | Purpose | Maturity |
|------|---------|----------|
| `__init__.py` | Translation loading, getText() | OK |
| `msgfmt.py` | PO -> MO compiler | OK (fixed for bytes) |
| `tools/` | Translation maintenance scripts | UNTESTED |

30+ languages supported via `.po` files in this directory.

---

## Search (MoinMoin/search/)

| Component | Files | Maturity |
|-----------|-------|----------|
| Built-in search | `builtin.py` | UNTESTED |
| Query parser | `queryparser/` | UNTESTED |
| Xapian search | `Xapian/` | OPTIONAL (needs xapian) |

---

## Logging (MoinMoin/logfile/)

| File | Purpose | Maturity |
|------|---------|----------|
| `__init__.py` | LogFile base class (binary I/O) | OK (fixed b'' write) |
| `editlog.py` | Edit log entries | PARTIAL |
| `eventlog.py` | Event log entries | UNTESTED |

**Key concern**: Log files use binary mode (`rb`/`ab`). Line parsing decodes to str.

---

## Security (MoinMoin/security/)

| File | Purpose | Maturity |
|------|---------|----------|
| `__init__.py` | ACL parsing and evaluation | UNTESTED |
| `antispam.py` | Anti-spam (BadContent page) | UNTESTED |
| `textcha.py` | Text CAPTCHA | UNTESTED |

**Tests**: `_tests/test_security.py`

---

## Utility (MoinMoin/util/) — 21 files

| File | Purpose | Maturity |
|------|---------|----------|
| `__init__.py` | pickle helpers, XML utilities | OK |
| `pysupport.py` | Dynamic module/plugin loading | OK (zip loader removed) |
| `filesys.py` | Filesystem utilities, rename, fuid | OK (dircache removed) |
| `lock.py` | File locking (ExclusiveLock, ReadLock) | UNTESTED |
| `clock.py` | Performance timing | OK |
| `web.py` | Web utilities (makeSelection, etc.) | UNTESTED |
| `SubProcess.py` | Subprocess wrapper | OK (fixed stdlib import) |
| `abuse.py` | Abuse logging | UNTESTED |
| `daemon.py` | Daemonize process | UNTESTED |
| `chartypes_create.py` | Generate Unicode char type tables | OK (unichr->chr) |
| `datasets.py` | TupleDataset, Column | UNTESTED |
| `diff3.py` | 3-way diff/merge | UNTESTED |
| `bdiff.py` | Binary diff | UNTESTED |
| `diff_html.py` | HTML diff rendering | UNTESTED |
| `mail.py` | Email address utilities | UNTESTED |
| `profile.py` | Profiling support | UNTESTED |
| `timefuncs.py` | Time formatting | UNTESTED |

---

## Other Modules

| Package | Files | Purpose | Maturity |
|---------|-------|---------|----------|
| `events/` | 5 | Page change notification system | UNTESTED |
| `filter/` | 22 | External doc filters (PDF, Word, etc.) | PARTIAL |
| `mail/` | 3 | SMTP email sending | UNTESTED |
| `stats/` | 6 | Wiki statistics/charts | OPTIONAL (gdchart) |
| `userform/` | 3 | Login forms, user browser UI | UNTESTED |
| `userprefs/` | 7 | User preference panels | UNTESTED |
| `widget/` | 5 | HTML widget generation | OK |
| `wikixml/` | 3 | XML marshalling | UNTESTED |
| `xmlrpc/` | 7 | XML-RPC API (v1 & v2) | UNTESTED |
| `converter/` | 2 | HTML-to-wiki conversion | UNTESTED |
| `script/` | 20+ | CLI tools (moin command) | PARTIAL |

---

## Vendored Libraries (MoinMoin/support/)

| Library | Version | Py3 Status | Notes |
|---------|---------|------------|-------|
| werkzeug | 1.0.1 | Works | Py2+Py3 dual support |
| passlib | 1.7.2 | Works | Password hashing |
| pygments | 2.5.2 | Works | Syntax highlighting |
| parsedatetime | 2.6 | Works | Date parsing |
| secure_cookie | 0.1.0 | Works | Session cookies |
| htmlmarkup.py | custom | Ported | HTML sanitization |
| md5crypt.py | custom | Ported | MD5 password hash |
| BasicAuthTransport.py | custom | Ported | XMLRPC basic auth |

**Removed**: flup (Py2 only), xappy (Py2 only), python_compatibility.py (obsolete)

---

## Priority Order for Further Work

### Tier 1 — Core Functionality (must work)
1. **PageEditor.py** — page saving, editing
2. **user.py** — login, registration, password
3. **caching.py** — disk cache read/write
4. **logfile/** — edit log, event log
5. **action/edit.py** — edit action
6. **action/AttachFile.py** — file attachments

### Tier 2 — Important Features
7. **search/builtin.py** — full-text search
8. **action/diff.py** — page diffs
9. **action/info.py** — page history
10. **mail/sendmail.py** — email notifications
11. **security/__init__.py** — ACL enforcement
12. **i18n/** — multi-language support

### Tier 3 — Nice to Have
13. **xmlrpc/** — remote API
14. **parser/text_rst.py** — reStructuredText
15. **parser/highlight.py** — syntax highlighting
16. **converter/** — HTML to wiki
17. **script/** — CLI tools

### Tier 4 — Low Priority
18. **stats/** — usage statistics (needs gdchart)
19. **auth/ldap_login.py** — LDAP (needs python-ldap)
20. **auth/openidrp.py** — OpenID (needs python-openid)
21. **wikisync.py** — wiki synchronization
