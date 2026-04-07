# Coding Policy

Rules to follow in this project. Links to the relevant ADRs are included.

## File Encoding
- All text files must be UTF-8
- Legacy `# -*- coding: iso-8859-1 -*-` headers may be removed
- Text read/write: `open(path, encoding='utf-8')`
- Binary read/write: `open(path, 'rb')` / `open(path, 'wb')`
- Do not use `codecs.open()` — see [ADR-003](../adr/003-string-bytes-boundary.md)

## str/bytes Boundary
Follow [ADR-003](../adr/003-string-bytes-boundary.md)

## Import Style
- Import vendored libraries directly: `import werkzeug`
  - Do not use `from MoinMoin.support import ...` — see [ADR-002](../adr/002-vendored-libs.md)
- Guard optional dependencies with try/except ImportError:
  `ldap`, `openid`, `xapian`, `MySQLdb`, `gdchart`

## Deprecated Python 2 APIs
Reference list for fixes. **Truth source is the code**. Issues not listed here may also exist.

| Old | New | Notes |
|---|---|---|
| `time.clock()` | `time.perf_counter()` | |
| `array.tostring()` | `array.tobytes()` | |
| `except T, v:` | `except T as v:` | |
| `string.maketrans` | `str.maketrans` | |
| `dircache` | `os.listdir()` | Module removed |
| `UserDict.DictMixin` | `collections.abc.MutableMapping` | |
| `HTMLParseError` | (removed) | Removed in Py 3.5 |
| `imp` | `importlib` | Migration TODO exists |
| `ImportError` message | `'foo' in str(err)` | Py3 includes quotes |
