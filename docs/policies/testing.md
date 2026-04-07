# Testing Policy

## Framework
pytest 9.x

## Test File Location
`MoinMoin/<package>/_tests/test_*.py`

## Running Tests
```bash
# Single test file
python -m pytest MoinMoin/_tests/test_error.py -v

# Core tests (excluding known problematic files)
python -m pytest MoinMoin/_tests/ \
  --ignore=MoinMoin/_tests/test_wikiutil.py \
  --ignore=MoinMoin/_tests/test_wsgiapp.py -v
```

## Test Infrastructure
- `conftest.py`'s `pytest_runtest_setup` injects `self.request`
- Test classes access the wiki context via `self.request`

## Smoke Tests / Full Scan
```bash
# Smoke tests (routine): 7 known Py3 regression patterns, <3 seconds
python -m pytest MoinMoin/_tests/test_smoke.py::TestSmoke -v

# Full scan (at milestones): GET all pages, verify no 500 errors, ~70 seconds
python -m pytest MoinMoin/_tests/test_smoke.py --run-slow -v

# Crawler (pre-release): Follow links on a live server and inspect responses
python wikiserver.py &
python scripts/crawl-wiki.py --fail-on-500 --report crawl-report.json
```

## Known Constraints
- `test_wikiutil.py`, `test_wsgiapp.py` use yield-based tests (deprecated)
  - These need to be rewritten with `@pytest.mark.parametrize` (TODO)
- **Truth source**: The test files themselves and the output of `python -m pytest`
