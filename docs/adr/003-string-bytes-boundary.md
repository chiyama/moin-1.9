# ADR-003: str/bytes Boundary Rules

## Status
Accepted

## Background
In Python 2, `str` and `unicode` were implicitly convertible. In Python 3,
`str` (text) and `bytes` (binary) are strictly distinguished.
MoinMoin handles diverse data formats — wiki text, file I/O, HTTP, cache (pickle) —
so clear boundaries are essential.

## Decision

| Data Type | Python Type |
|---|---|
| Wiki page content, page names, user input | `str` |
| Filesystem paths | `str` |
| HTTP response body | `bytes` |
| Cache data, pickle data | `bytes` |
| hashlib / hmac arguments | `bytes` (encode strings with `.encode()` before passing) |
| Log file I/O | `bytes` (decode line by line) |

Text file read/write:
- Use `open(path, encoding='utf-8')`
- Do not use `codecs.open()` (see ADR-001)
- For binary files: `open(path, 'rb')` / `open(path, 'wb')`

## Consequences
- All modules must follow the boundaries above
- Violations will surface as `str`/`bytes` `TypeError` at runtime
- Verification: Run `python -m pytest` and confirm no TypeError occurs
