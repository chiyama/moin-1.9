# Vulnerability Inventory

Known vulnerabilities and security-relevant defects of this port, with their status.
Policy: [ADR-004](../adr/004-scope-and-security-policy.md). Update this file in the
same change that fixes an item.

- **Last full audit**: 2026-10-02 (code read against branch `master` = upstream 1.9.11,
  plus scratch tests; external facts from NVD, OSV, GitHub advisories, devguide.python.org)
- **Truth source**: the code. File:line references are for the working tree at audit time
  and will drift; search by function name if a line no longer matches.

## Status legend

| Status | Meaning |
|---|---|
| open | Affects this port and is not fixed |
| fixed | Fix is present in the code (evidence given) |
| mitigated | Not fixed, but disabled by default or not reachable in default setup |
| n/a | Does not apply to this port |
| unverified | Could not be confirmed either way; see notes |

## Priority order

Ranked by reachability and impact. Work these first, one per session.

| # | Item | Why first |
|---|---|---|
| 1 | [R-1](#r-runtime) Python 3.10 end of life | No security fixes for the interpreter at all; blocks nothing else but affects everything |
| 2 | [V-1](#v-vendored-libraries) werkzeug 1.0.1 multipart DoS | Reachable by anonymous users with any POST |
| 3 | [V-5](#v-vendored-libraries) pygments 2.5.2 ReDoS / infinite loop | Reachable by anyone who can edit a page |
| 4 | [P-1](#p-weaknesses-and-defects-introduced-by-the-port), P-3 port defects in security code | Fail closed today, but each fix must avoid reintroducing upstream weaknesses (see U-3). P-2, P-4 (GivenAuth), P-5 are fixed |
| 5 | [T-1](#t-test-coverage-of-security-code) security tests not running | Without them, fixes above cannot be pinned |

## R. Runtime

| ID | Summary | Status | Evidence / notes | Next action |
|---|---|---|---|---|
| R-1 | Python 3.10 reached end of life in 2026-10 (3.10.22 is the final release). The `.venv` runs 3.10.11, 11 security releases behind (e.g. CVE-2023-24329, CVE-2023-40217, CVE-2024-4030). | open | https://devguide.python.org/versions/ ; https://www.python.org/downloads/release/python-31022/ | Move to Python 3.12+ (EOL 2028-10) or 3.14 (EOL 2030-10). Blockers below. |
| R-2 | `import imp` (removed in 3.12) in plugin loading: on 3.12+ every request returns 500. With `imp` replaced, 20 sampled URLs returned 200 on 3.14.4. | open | `MoinMoin/config/multiconfig.py:587` (`_loadPluginModule`) | Replace with `importlib`. |
| R-3 | Invalid escape sequences (SyntaxWarning on 3.12+, planned SyntaxError) in modules imported at startup | open | `util/timefuncs.py:29`, `packages.py:203`, `action/__init__.py:239`; scripts: `script/account/check.py:124`, `script/migration/text_moin158_wiki.py:51,946`, `script/old/repair_language.py:70` | Use raw strings. |
| R-4 | `return` inside `finally` (SyntaxWarning on 3.14, PEP 765) | open | `util/lock.py:241` | Restructure. |
| R-5 | `crypt` removed in 3.13: legacy `{DES}` password hashes stop verifying (fails closed; already the case on Windows) | open (low) | `user.py:30,741` (guarded import) | Verify `{DES}` via passlib, or document as unsupported. |

## V. Vendored libraries

Versions read from the code under `MoinMoin/support/`. `MoinMoin/__init__.py` puts
`support/` first on `sys.path`, so these copies win over anything installed in the venv.
Advisory data: OSV (https://osv.dev/vulnerability/<ID>).

| ID | Library | Advisory | Summary | Fixed in | Reachable in MoinMoin | Status |
|---|---|---|---|---|---|---|
| V-1 | werkzeug 1.0.1 | CVE-2023-25577 / GHSA-xg9f-g7g7-2323 | Unlimited multipart parts → CPU/memory exhaustion | 2.2.3 | Yes, unauthenticated: any POST parses the form (`wsgiapp.py:216`); no `max_content_length` / `max_form_memory_size` set anywhere | open |
| V-2 | werkzeug 1.0.1 | CVE-2024-49766 / GHSA-f9vj-2wh5-fj8j; CVE-2025-66221, CVE-2026-21860, CVE-2026-27199 | `safe_join` lets Windows UNC paths / device names through | 3.0.6 / 3.1.4–3.1.6 | Only on Windows when moin serves static files itself (`web/static/__init__.py:79`, standalone server default `docs=True`). Not traced end to end. | open (conditional) |
| V-3 | werkzeug 1.0.1 | CVE-2023-23934 / GHSA-px8h-6qxv-m22q | Nameless cookie can shadow `__Host-` cookies | 2.2.3 | Parsed, but moin uses no `__Host-` cookies | mitigated |
| V-4 | werkzeug 1.0.1 | CVE-2024-34069 (debugger RCE); CVE-2022-29361 (dev server smuggling, disputed) | — | 3.0.3 / 2.1.1 | Only with `debug='web'` (default `'off'`) / only when `wikiserver.py` serves traffic | mitigated |
| V-4a | werkzeug 1.0.1 | CVE-2023-46136 / PYSEC-2023-221 | Multipart boundary search DoS | 2.3.8 | OSV range includes 1.0.1, but the bug is in the parser introduced in 2.2; 1.0.1 parses differently | unverified |
| V-5 | pygments 2.5.2 | CVE-2021-20270, CVE-2021-27291, CVE-2026-4539 | Infinite loop (SMLLexer), ReDoS (several lexers, AdlLexer) | 2.7.4 / 2.20.0 | Yes: `{{{#!highlight <lexer>` by any editor (`parser/highlight.py:173`), and lexer by attachment filename (`:167`) | open |
| V-5a | pygments 2.5.2 | CVE-2022-40896 | ReDoS in SmithyLexer | 2.15.0 | No: lexer not present in 2.5.2 | n/a |
| V-6 | passlib 1.7.2 | none known | Upstream unmaintained since 2020 (latest 1.7.4); fork `libpass` is active | — | — | watch |
| V-7 | secure_cookie 0.1.0 | none known | Unmaintained; depends on werkzeug APIs removed in 2.x/3.x, so it must be replaced or adapted with V-1 | — | Session id validated against `^[a-f0-9]{40}$` before file access | watch |
| V-8 | parsedatetime 2.6 | none known | Dormant upstream | — | — | watch |

**werkzeug upgrade size** (V-1, V-2): moin code uses APIs removed in 2.x/3.x:
`werkzeug.urls.*` (via `wikiutil.py:95-185`, ~75 uses), `urls.Href`, `security.safe_str_cmp`
(~10 uses; replace with `hmac.compare_digest`), `posixemulation.rename`, `http.cookie_date`,
`BaseResponse` and response mixins (`web/request.py`), `serving.BaseRequestHandler`,
and `test.Client` now returning a response object (affects tests).

## U. Upstream MoinMoin 1.9

All publicly listed fixes for 1.9.x are present in the port. Checked by comparing each
fix commit's added lines with the working tree, and by reading diffs vs `master`.
No CVE/GHSA for MoinMoin 1.9 has been published after 1.9.11 (checked NVD, GitHub
advisories, OpenCVE, http://moinmo.in/SecurityFixes on 2026-10-02).

| ID | Summary | Status | Evidence (port) |
|---|---|---|---|
| CVE-2020-25074 | cache action directory traversal → RCE | fixed | `action/cache.py` `valid_key`, `execute` |
| CVE-2020-15275 | stored XSS via SVG attachment | fixed | `config/multiconfig.py` `mimetypes_xss_protect` includes `image/svg+xml`; served as `attachment` |
| CVE-2017-5934, CVE-2016-9119 | XSS in GUI editor link dialog | fixed as upstream (see U-1) | `action/fckdialog.py` `link_dialog`, `page_list` |
| CVE-2016-7146 | XSS in GUI editor attachment dialog | fixed | `action/fckdialog.py` `attachment_dialog` |
| CVE-2016-7148 | XSS in AttachFile view (multifile) | fixed | `action/AttachFile.py` `_build_filelist` |
| (1.9.8, no CVE) | XSS in useragents stats | fixed | `stats/useragents.py` |
| CVE-2012-6080 | AttachFile path traversal | fixed | `action/AttachFile.py` `_do_attachment_move`, `taintfilename` calls |
| CVE-2012-6081, CVE-2012-6495 | twikidraw/anywikidraw upload → RCE / traversal | fixed | `action/twikidraw.py`, `action/anywikidraw.py` (`taintfilename` on target) |
| (1.9.6, no CVE) | stronger `taintfilename` | fixed | `wikiutil.taintfilename` |
| CVE-2012-6082 | XSS via page name in RSS link | fixed | `theme/__init__.py` `rsslink` |
| (1.9.6, no CVE) | escape user CSS URL; constant-time comparisons | fixed | `theme/__init__.py` `stylesheetLink`; `safe_str_cmp` in `wikiutil.checkTicket`, `user.py`, `textcha.py` |
| CVE-2012-4404 | virtual group ACL bug | fixed | `security/__init__.py` `AccessControlList.may` |
| CVE-2011-1058 | `javascript:` URL in rst parser | fixed as upstream | `parser/text_rst.py` `visit_reference` (case-sensitive check; docutils not installed, not exercised) |
| CVE-2010-2487, CVE-2010-2969, CVE-2010-2970 | XSS in messages and several actions | fixed (SlideShow part unverified) | `PageEditor.py`, `action/LikePages.py`, `action/language_setup.py` |
| CVE-2010-0828 | XSS in Despam | fixed | `action/Despam.py` |
| CVE-2010-0668, CVE-2010-0669, CVE-2010-0717 | superuser/xmlrpc/ticket issues; profile input sanitizing; package actions | fixed (known parts) | tickets in `wikiutil.py`; `clean_input` in `userprefs/prefs.py`; `packages.py` |
| CVE-2009-4762 | hierarchical ACL evaluation | fixed | `security/__init__.py` `_check` |
| CVE-2010-0667 | `sys.argv` not cleared under CGI | n/a | CGI front end (`web/flup_frontend.py`) was removed; `wiki/server/moin.cgi` still imports it and cannot start |
| (1.9.3 advisory) | XSLT file read/write | mitigated | `allow_xslt = False` by default |

Open items inherited from upstream:

| ID | Summary | Status | Evidence / notes |
|---|---|---|---|
| U-1 | `fckdialog` wrote request values (the `pagename` parameter, and the page name taken from the URL path) into `value="..."` escaped without `quote=True`, so `"` ended the attribute: reflected XSS by anonymous GET. Same in upstream 1.9.11. Confirmed by test before the fix. | fixed | `action/fckdialog.py` `link_dialog`, `attachment_dialog`: `wikiutil.escape(..., quote=True)`. Test: `_tests/test_smoke.py` `test_fckdialog_escapes_quotes_in_attributes` |
| U-5 | The `refresh` action took `arena` and `key` from the request and removed the file `os.path.join(<page cache dir>, key)`, with no check on `key` (`../`, absolute paths) and no read ACL check. An anonymous GET could remove files writable by the wiki process. Found by code reading; same in upstream 1.9.11 (`do_refresh` in `master:MoinMoin/action/__init__.py`). Not exercised at runtime. | fixed | `action/__init__.py` `do_refresh`: only `arena=Page.py`; `key` must match `[A-Za-z0-9_][A-Za-z0-9_.-]*` (`valid_refresh_key`); the user must be able to read the page. Test: `action/_tests/test_refresh.py` |
| U-2 | XML types outside `mimetypes_xss_protect` (e.g. `text/xml`) are served inline. Same as upstream; mapping depends on the host's `mimetypes` data. | unverified | `config/multiconfig.py` `mimetypes_xss_protect` |
| U-3 | Password recovery token can be forged for a user who never requested a reset: `recoverpass_key` is `""`, so the HMAC key is empty. Upstream weakness; currently unreachable because of P-3. | mitigated by P-3 (must not be reintroduced) | `user.py:1261-1281` |
| U-4 | `htmlmarkup.py` (2006 Trac sanitizer) CSS filter does not decode CSS escapes/comments (matters only for legacy IE); attribute without value may raise `TypeError`. 23 sanitizer payloads tested OK. | unverified | `support/htmlmarkup.py:244-257` |

## P. Weaknesses and defects introduced by the port

No case was found where the port lets an attacker through a check. The defects below
make security-related features crash (HTTP 500) or reject (fail closed).

| ID | Summary | Severity | Evidence | Fix note |
|---|---|---|---|---|
| P-1 | `{SHA}`/`{SSHA}` password verification calls `base64.decodestring`/`encodestring` (removed in 3.9): login of such users returns 500; hash upgrade never happens | medium (availability) | `user.py:716-726`; `{SSHA}` encoding also double-encodes at `user.py:283-291` | Use `base64.b64decode`/`b64encode` with bytes; this is the cause of `test_user.py` baseline failures |
| P-2 | `clean_input` called `.decode()` on `str`: any non-empty input returned 500 (attachment upload over HTTP, edit/rename/delete comments, recoverpass, newaccount email, userprefs) | fixed | `wikiutil.clean_input` decodes only `bytes`. Test: `_tests/test_write_path.py` `test_clean_input_str` | — |
| P-3 | `hmac.new` gets a `str` key: password recovery tokens (500), TextCha (form 500, every answer rejected), cache keys (500) | low (fail closed) | `user.py:1263,1281`; `security/textcha.py:87`; `action/cache.py:102` | Encode keys; for recovery tokens, also reject an empty `recoverpass_key` (U-3) |
| P-4 | `.decode()` on `str` in HTTP/SSL-cert/Given auth with `coding` set: login with credentials returns 500 | GivenAuth fixed; HTTP and SSL-cert auth open (low, fail closed) | `GivenAuth.decode_username` re-encodes the WSGI (latin-1) str to bytes, then decodes with `coding` or as UTF-8. Test: `_tests/test_write_path.py`. Still open: `auth/http.py:84-85`, `auth/sslclientcert.py:47,51` | Same treatment as GivenAuth |
| P-5 | XML-RPC: module name `xmlrpc` shadowed by a function, every request 500; v2 also returned page text as base64 `Binary` (bytes) instead of a string | fixed | `xmlrpc/__init__.py` imports `xmlrpc.client as xmlrpclib`; `XmlRpc2._outstr` returns `str`. Test: `_tests/test_write_path.py` (putPage/getPage with GivenAuth and ACL) | — |
| P-6 | Other Py3 breakage seen during the audit (not security): `unichr`; macros TitleIndex (Hangul page names), PageSize, AdvancedSearch, PageList; `AttachFile do=box` returned 500 for a missing container member or a non-tar target | fixed | `wikiutil.getUnicodeIndexGroup`, `formatter/text_docbook.py`, `macro/PageSize.py`, `macro/AdvancedSearch.py`, `search/results.py` sort keys, `AttachFile._do_box` (404). Tests: `_tests/test_smoke.py` | — |

Checks confirmed intact (scratch tests, 2026-10-02): ticket create/check rejects forged,
expired, wrong-action and empty tickets with constant-time comparison; `{PASSLIB}`,
`{MD5}`, `{APR1}` verify correctly and reject wrong passwords; ACL evaluation
(`-All:write`, modifiers, Default, groups, `acl_hierarchic`) and 403 on read-protected
pages for show/raw/print/info/diff/AttachFile; `actions_excluded`/`actions_superuser`;
`taintfilename` blocks traversal; `.html`/`.svg`/`.swf` attachments served as `attachment`;
HTML sanitizer strips script, event handlers, `javascript:`/`data:`; surge protection;
`LocalBadContent`; session id validation.

## C. Configuration behaviour relevant to security

Not defects. These describe what an option does, so that a site can be configured
knowingly (ADR-004: operating decisions are made elsewhere).

| ID | Behaviour | Evidence |
|---|---|---|
| C-1 | `GivenAuth(env_var='HTTP_REMOTE_USER')` trusts a `Remote-User` request header from any client that reaches the wiki process. Whatever sits in front must set or clear that header on every request. | `auth/__init__.py` `GivenAuth.request`; `_tests/test_write_path.py` sends the header directly |
| C-2 | `xmlrpc_overwrite_user = True` (default) replaces the user authenticated by GivenAuth with an invalid user at the start of every XML-RPC call; only `getAuthToken`/`applyAuthToken` log in then. With `False`, XML-RPC runs as the GivenAuth user. | `xmlrpc/__init__.py` `XmlRpcBase.process` |
| C-3 | Surge protection exempts `REMOTE_ADDR` starting with `127.`. Behind a reverse proxy on the same host nothing is rate limited, unless the WSGI app is built with `make_application(trusted_proxies=[...])`, which takes the client address from `X-Forwarded-For`. | `web/utils.py` `check_surge_protect`; `web/serving.py` `ProxyTrust` |
| C-4 | `show_hosts = True` (default) shows editors' host names / IP addresses in `info` and RecentChanges to everyone who can read the page. | `config/multiconfig.py` `show_hosts` |
| C-5 | `createTicket` uses the session id only when the session is non-empty, so a form fetched as the first request of a new session carries a ticket that fails once the session has content. Same in upstream 1.9.11. Browsers that view a page before editing are not affected. | `wikiutil.createTicket` (`if request.session:`) |

## T. Test coverage of security code

| ID | Summary | Status | Evidence |
|---|---|---|---|
| T-1 | ACL and auth regression suites are never collected: `security/_tests/test_security.py` uses yield tests; `auth/_tests/test_auth.py`, `test_ldap_login.py` skip at module level | open | pytest collection |
| T-2 | Known baseline failures: 18 in `MoinMoin/_tests` (incl. `test_user.py`, see P-1), 6 in `action/_tests/test_cache.py` (see P-3) | open | pytest run |
