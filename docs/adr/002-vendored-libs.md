# ADR-002: Third-Party Library Vendoring

## Status
Accepted (inherited from upstream MoinMoin)

## Background
MoinMoin has historically bundled third-party libraries under `MoinMoin/support/`.
This allows the application to run without additional pip installs.

## Decision
Continue vendoring. Libraries are placed in `MoinMoin/support/` and added to
`sys.path` in `MoinMoin/__init__.py`.

Currently bundled libraries:
- werkzeug 1.0.1
- passlib 1.7.2
- pygments 2.5.2
- parsedatetime 2.6
- secure_cookie 0.1.0
- htmlmarkup.py (custom, ported from Trac)
- md5crypt.py (custom)
- BasicAuthTransport.py (custom)

**Truth source**: The actual files inside the `MoinMoin/support/` directory.
Check each library's `__init__.py` or `_version` for version information.

## Alternatives Considered
- Switch to pip dependencies: Loses ease of deployment
- Partial vendoring: Increases management complexity

## Consequences
- Import libraries directly: `import werkzeug` (do not use `from MoinMoin.support import ...`)
- When updating a library, replace the entire package under `MoinMoin/support/`
