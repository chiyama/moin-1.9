# MoinMoin

Python 3 port of the MoinMoin wiki engine.
Forked from the original MoinMoin 1.9.11 (Python 2.7) and ported to run on **Python 3.10+**.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows

# First time only: extract underlay data
python -c "import tarfile; tarfile.open('wiki/underlay.tar').extractall('wiki/')"

# Start development server
python wikiserver.py
# → http://localhost:8080/
```

## Key Commands

| Command | Purpose |
|---|---|
| `python wikiserver.py` | Start development server |
| `python -m pytest MoinMoin/_tests/test_error.py -v` | Run tests (single file) |
| `pip install -e .` | Install in development mode |

## Documentation Map

| Path | Description |
|---|---|
| [CLAUDE.md](CLAUDE.md) | AI agent work entry point |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Module structure and maturity |
| [docs/adr/](docs/adr/) | Architecture Decision Records (ADR) |
| [docs/policies/](docs/policies/) | Coding and testing conventions |
| [docs/runbooks/modernize.md](docs/runbooks/modernize.md) | Modernization work plan |
| [docs/REQUIREMENTS](docs/REQUIREMENTS) | Dependencies |
| [docs/INSTALL.html](docs/INSTALL.html) | Installation guide (Py3 update TODO) |
| [docs/licenses/](docs/licenses/) | Licenses |

## License

GNU GPL v2 or later. See [LICENSE](LICENSE) for details.
