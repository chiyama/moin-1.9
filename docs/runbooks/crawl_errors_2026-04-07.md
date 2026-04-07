# Crawl Investigation Results (2026-04-07)

Results from crawling links starting from the front page, looking for 500 errors.
300 pages crawled, 5 unique error types detected.

---

## Error 1: AttachFile._get_files — `str.decode()` (Impact: High)

- **Symptom**: All pages with attachments return 500
- **Scope**: WikiSandBox, HelpOnMoinWikiSyntax, language-specific FrontPages, etc. — over 100 pages
- **File**: `MoinMoin/action/AttachFile.py:601`
- **Error**: `AttributeError: 'str' object has no attribute 'decode'`
- **Cause**: Python 3's `os.listdir()` returns `str`, but `.decode()` is being called
- **Traceback**:
  ```
  theme/__init__.py:1755 send_title → AttachFile.send_link_rel()
  AttachFile.py:623 send_link_rel → _get_files()
  AttachFile.py:601 _get_files:
    files = [fn.decode(config.charset) for fn in os.listdir(attach_dir)]
  ```

---

## Error 2: PageEditor.sendEditor — `str.decode()` (Impact: High)

- **Symptom**: `?action=edit&editor=text` returns 500 on all pages
- **Scope**: All page edit operations
- **File**: `MoinMoin/PageEditor.py:350`
- **Error**: `AttributeError: 'str' object has no attribute 'decode'`
- **Cause**: `"hidden".decode(...)` — code assumes Python 2 bytes literals
- **Traceback**:
  ```
  action/edit.py:78 execute → pg.sendEditor()
  PageEditor.py:350:
    request.write(html.INPUT(type="hidden".decode(name="action", value="edit")))
  ```

---

## Error 3: action/info.py — SyntaxError (Impact: High)

- **Symptom**: `?action=info` returns 500 on all pages
- **Scope**: All page info/history views
- **File**: `MoinMoin/action/info.py:37`
- **Error**: `SyntaxError: invalid syntax`
- **Cause**: Past migration broke the syntax: `.encode('utf-8')` inserted in the wrong position
- **Code**:
  ```python
  digest = hashlib.new('sha1', page.get_raw_body(.encode('utf-8')).encode(config.charset)).hexdigest().upper()
  ```
  Should be `page.get_raw_body().encode(config.charset)`.

---

## Error 4: fullsearch — `str.decode()` (Impact: High)

- **Symptom**: Full-text search returns 500
- **Scope**: Entire search functionality
- **File**: `MoinMoin/search/queryparser/__init__.py:157`
- **Error**: `AttributeError: 'str' object has no attribute 'decode'`
- **Cause**: In Python 3 the query is already `str`, but `.decode()` is still being called
- **Traceback**:
  ```
  action/fullsearch.py:189 → queryparser/__init__.py:157:
    query = query.decode(config.charset)
  ```

---

## Error 5: formatter/__init__.py — `import formatter, htmllib` (Impact: Medium)

- **Symptom**: 500 on fallback rendering for table attribute errors
- **Scope**: Pages with table syntax, under specific conditions
- **File**: `MoinMoin/formatter/__init__.py:373`
- **Error**: `ModuleNotFoundError: No module named 'formatter'`
- **Cause**: `formatter` and `htmllib` were removed in Python 3
- **Traceback**:
  ```
  parser/text_moin_wiki.py:1537 format → _getTableAttrs()
  parser/text_moin_wiki.py:1143 → wikiutil.parseAttributes()
  wikiutil.py:2004 → table_extension() → formatter.rawHTML()
  formatter/__init__.py:373:
    import formatter, htmllib
  ```

---

## Error 6: SpellCheck — `sort()` with positional arg (Impact: Low)

- **Symptom**: `?action=SpellCheck` returns 500
- **Scope**: Spell check feature
- **File**: `MoinMoin/action/SpellCheck.py:168`
- **Error**: `TypeError: sort() takes no positional arguments`
- **Cause**: Python 3's `list.sort()` does not accept a comparison function as a positional argument (use `key=` instead)
- **Code**:
  ```python
  badwords.sort(lambda x, y: cmp(x.lower(), y.lower()))
  ```

---

## Error 7: WantedPages / OrphanedPages — Timeout (Impact: Low)

- **Symptom**: `/WantedPages`, `/OrphanedPages` time out (>10 seconds)
- **Scope**: 2 pages only
- **Cause**: Not investigated. Possibly full-page scan is too heavy, or an infinite loop exists

---

## Additional Errors Found via Full Scan (pytest --run-slow)

### Error 8: Creole Parser — `unichr` is not defined (Impact: Medium)

- **Symptom**: Pages using Creole markup return 500
- **Scope**: 32 pages (SyntaxReference in various languages, etc.)
- **File**: `MoinMoin/parser/_creole.py:147-148`
- **Error**: `NameError: name 'unichr' is not defined`
- **Cause**: Python 3 renamed `unichr` → `chr`
- **Status**: Fixed — `unichr` → `chr`

### Error 9: RecentChanges — EditLogLine comparison (Impact: Low)

- **Symptom**: AbandonedPages display returns 500
- **File**: `MoinMoin/logfile/editlog.py:42-46`
- **Error**: `TypeError: '<' not supported between instances of 'EditLogLine' and 'EditLogLine'`
- **Cause**: Python 3 removed `__cmp__`; comparison methods like `__lt__` are required
- **Status**: Fixed — `__cmp__` → `__lt__`/`__eq__`/`__le__`/`__gt__`/`__ge__`

### Error 10: text_csv Parser — Unnecessary encode/decode (Impact: Medium)

- **Symptom**: Pages with CSV tables return 500
- **Scope**: 26 pages (SyntaxReference, HelpOnParsers in various languages, etc.)
- **File**: `MoinMoin/parser/text_csv.py:58, 83, 87, 98, 101, 103-104, 127, 133, 158`
- **Error**: `TypeError: a bytes-like object is required, not 'str'`
- **Cause**: Python 3's `csv.reader` accepts and returns `str`, but Py2-era encode/decode calls remain
- **Status**: Fixed — Removed all encode/decode calls

### Error 11: htmlmarkup.py — `html` module name collision (Impact: Very Low)

- **Symptom**: Russian help page `ПомощьПоДействиям/AttachFile` returns 500
- **Scope**: 1 page only (specific page with embedded HTML parser)
- **File**: `MoinMoin/support/htmlmarkup.py:84`
- **Error**: `AttributeError: 'Element' object has no attribute 'name2codepoint'`
- **Cause**: `html = Tags()` at end of module shadows `import html.entities`
- **Status**: Fixed — Renamed to `import html.entities as _html_entities`

---

## Crawl Statistics

- Pages crawled: 300 (1358 remaining in queue)
- Total errors: 107 (500: 82, 404: 23, timeout: 2)
- 404 errors are from uninstalled language pack pages — expected behavior

---

## Confirmed Working (200)

- `/` (front page)
- `/LanguageSetup` (page rendering)
- `?action=newaccount` (fixed)
- `?action=login`
- `?action=diff`
- `?action=recall`
- `?action=subscribe`
- `?action=userprefs`
- `?action=raw`
- `?action=print`
- `?action=sitemap`
- `?action=chart`
- `?action=bookmark`
- `?action=LikePages`
- `?action=LocalSiteMap`
- `?action=MyPages`
- `?action=DesktopEdition`
- `?action=thread_monitor`
- `?action=Load`
- `?action=Save`
- `?action=AttachFile`
- `?action=Despam`
- `?action=PackagePages`
- `?action=SyncPages`
- `?action=CopyPage`
- `?action=titleindex`
- `/TitleIndex`, `/WordIndex`, `/FindPage`, `/RecentChanges`
- `/FrontPage` (without attachments)
- `/HelpOnFormatting`
- `/SystemInfo`
