# MoinMoin

MoinMoin is a wiki engine - a software you can use to run your own wiki site.

MoinMoin is written in Python. **Python 3.10 or later is required.**

This is a fork of MoinMoin 1.9.11 that has been ported to Python 3.
The original MoinMoin 1.9.x only supported Python 2.7.

## Quick Start

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows

# Extract underlay data (first time only)
python -c "import tarfile; tarfile.open('wiki/underlay.tar').extractall('wiki/')"

# Start the development server
python wikiserver.py

# Open http://localhost:8080/ in your browser
```

## Documentation

Local:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Module structure and migration status
- [docs/MODERNIZE.md](docs/MODERNIZE.md) - Session-based modernization work plan
- [docs/CHANGES](docs/CHANGES) - Version history
- [docs/REQUIREMENTS](docs/REQUIREMENTS) - List of requirements
- [docs/INSTALL.html](docs/INSTALL.html) - Installation instructions
- [docs/README.migration](docs/README.migration) - Data conversion instructions
- [CLAUDE.md](CLAUDE.md) - Development guide and conventions

On the Web:

- [MoinMoin homepage](https://moinmo.in/)

## Migration Status

This port covers the following changes from the original Python 2.7 codebase:

- All `print` statements converted to `print()` functions
- All `except Type, var` converted to `except Type as var`
- `unicode` / `basestring` / `long` types replaced with `str` / `int`
- `dict.has_key()` replaced with `in` operator
- Standard library module renames (`StringIO`, `urllib2`, `xmlrpclib`, etc.)
- `file()` builtin replaced with `open()`
- Vendored libraries (werkzeug, passlib, pygments) verified for Python 3

The wiki server starts and serves pages. Some features (page editing, user
registration, attachments, email) need further testing and fixes. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for per-module status.

## License

GNU GPL v2 or later. See [LICENSE](LICENSE) for details.
