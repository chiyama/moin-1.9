# CLAUDE.md - MoinMoin 1.9 Development Guide

## Project Overview

MoinMoin 1.9.11 wiki engine, ported from Python 2.7 to Python 3.10.
Branch `py3-migration` contains the active Python 3 port.

## Quick Start

```bash
# Activate the virtual environment
source .venv/Scripts/activate    # Windows (Git Bash)
# .venv/Scripts/activate.bat     # Windows (CMD)
# source .venv/bin/activate      # Linux/Mac

# Start the wiki server
python wikiserver.py
# Open http://localhost:8080/

# Run tests
python -m pytest MoinMoin/_tests/test_error.py -v
python -m pytest MoinMoin/_tests/ --ignore=MoinMoin/_tests/test_wikiutil.py --ignore=MoinMoin/_tests/test_wsgiapp.py -v
```

## Architecture & Work Plan

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — module structure, maturity levels, request lifecycle
- [docs/MODERNIZE.md](docs/MODERNIZE.md) — session-by-session modernization plan with verification steps

## Key Conventions

### File Encoding
- All text files should use UTF-8. Old `# -*- coding: iso-8859-1 -*-` headers can be removed.
- Use `open(path, encoding='utf-8')` for text files, `open(path, 'rb')` for binary.
- Do NOT use `codecs.open()` — use the built-in `open()` with `encoding=` parameter.

### String/Bytes Rules (Python 3)
- `str` = text (Unicode). `bytes` = binary data. No implicit conversion.
- Wiki page content, page names, user input: always `str`.
- File system paths: always `str`.
- HTTP response bodies, cache data, pickle data: `bytes`.
- `hashlib`, `hmac`: require `bytes` arguments — encode strings first.

### Import Style
- Vendored libraries live in `MoinMoin/support/` and are added to `sys.path` via `MoinMoin/__init__.py`.
- Use `import werkzeug` (not `from MoinMoin.support import werkzeug`).
- Optional dependencies (`ldap`, `openid`, `xapian`, `MySQLdb`, `gdchart`) should be guarded with try/except ImportError.

### Testing
- Framework: pytest (9.x)
- Test files: `MoinMoin/<package>/_tests/test_*.py`
- Test classes use `self.request` injected by `conftest.py`'s `pytest_runtest_setup`
- Run specific tests: `python -m pytest MoinMoin/_tests/test_error.py -v`
- Known limitation: `test_wikiutil.py` and `test_wsgiapp.py` use yield-based tests (deprecated in modern pytest, need rewrite to `@pytest.mark.parametrize`)

### Common Pitfalls
- `time.clock()` was removed — use `time.perf_counter()`
- `array.tostring()` was removed — use `array.tobytes()`
- `except ExType, var:` is invalid — use `except ExType as var:`
- Python 3 `ImportError` messages are quoted: `No module named 'foo'` — use `'foo' in str(err)` not `str(err).endswith('foo')`
- `string.maketrans` was removed — use `str.maketrans` or `bytes.maketrans`
- `dircache` module was removed — use `os.listdir()` directly
- `UserDict.DictMixin` moved to `collections.abc.MutableMapping`
- `HTMLParseError` removed from `html.parser` in Python 3.5
- `imp` module is deprecated — should migrate to `importlib`

## Migration Status

### What Works
- Wiki server starts and serves pages (`python wikiserver.py`)
- 387/402 modules import successfully
- Core test suite: 22 tests pass
- Page viewing, FrontPage rendering

### Known Remaining Issues
- Some `codecs.open()` calls need migration to `open(encoding=...)`
- `imp` module usage in multiconfig.py (deprecated, works but warns)
- yield-based tests need rewrite to parametrize
- Untested: page editing, user registration, attachments, email, XMLRPC
- Optional auth backends (LDAP, OpenID) untested

## Build & Deploy

```bash
# Install for development
pip install -e .

# Package
python setup.py sdist

# The standalone server (wikiserver.py) is for development only.
# For production, use a WSGI server (gunicorn, uwsgi) with wsgiapp.application
```
