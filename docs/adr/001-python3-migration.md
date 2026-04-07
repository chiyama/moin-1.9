# ADR-001: Python 2 to Python 3 Migration

## Status
Accepted (2024)

## Background
MoinMoin 1.9.11 was originally Python 2.7 only. With Python 2 reaching EOL (2020-01-01),
applying security patches and updating libraries had become increasingly difficult.

## Decision
Migrate MoinMoin 1.9.11 to Python 3.10+. Work is done on the `py3-migration` branch.

Migration strategy:
- 2to3 automatic conversion + manual fixes
- Bundled libraries (werkzeug, passlib, pygments) updated to Py3-compatible versions
- Py2-only dependencies (flup, xappy) removed
- Incremental verification: import → tests → manual testing

## Alternatives Considered
- Migrate to MoinMoin 2.0: A separate project with no data compatibility
- Replace with a new wiki engine: High migration cost for existing data and customizations

## Consequences
- The `str` = text, `bytes` = binary boundary must be clarified across all modules
- `codecs.open()` must be replaced with `open(encoding=)`
- Test suite modernization required (yield-based → parametrize)
- Detailed rules in [docs/policies/coding.md](../policies/coding.md)
