# CLAUDE.md — Agent Work Entry Point

## Read First
1. This document (workflow and prohibitions)
2. [docs/policies/coding.md](docs/policies/coding.md) — Coding rules
3. [docs/policies/testing.md](docs/policies/testing.md) — Testing conventions
4. [docs/adr/](docs/adr/) — Accepted design decisions

## Environment Setup
```bash
source .venv/Scripts/activate    # Windows (Git Bash)
# source .venv/bin/activate      # Linux/Mac
```

## Verification Commands
```bash
# Start server
python wikiserver.py

# Run tests
python -m pytest MoinMoin/_tests/test_error.py -v
python -m pytest MoinMoin/_tests/ \
  --ignore=MoinMoin/_tests/test_wikiutil.py \
  --ignore=MoinMoin/_tests/test_wsgiapp.py -v
```

## Workflow
1. Present the plan first
2. Make small changes
3. Verify with tests after each change
4. Current work plan: [docs/runbooks/modernize.md](docs/runbooks/modernize.md)

## Prohibitions
- Do not use `codecs.open()` — use `open(encoding='utf-8')` instead
- Do not use `from MoinMoin.support import ...` — use direct imports like `import werkzeug`
- Do not make definitive claims in documentation without verifying in code
- Do not edit vendored code under `MoinMoin/support/`

## Truth Source Priority
Code > Tests > Config files > ADR > Policy > Documentation prose
