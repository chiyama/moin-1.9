#!/usr/bin/env python
"""
crawl-wiki.py — Full-site crawl for MoinMoin wiki (Python 3)

Starts from a running wiki server, follows every <a href> link, and
reports pages that return HTTP 500.  Designed as a release-gate check
to catch Python 3 migration regressions that unit tests miss.

Usage::

    # 1. Start the wiki server
    python wikiserver.py &

    # 2. Run the crawl
    python scripts/crawl-wiki.py [OPTIONS]

Options::

    --base-url URL     Base URL of the wiki (default: http://localhost:8080)
    --max-pages N      Stop after N pages (default: 0 = unlimited)
    --timeout SEC      Per-request timeout in seconds (default: 10)
    --workers N        Number of concurrent fetch threads (default: 8)
    --report FILE      Write JSON report to FILE (default: stdout summary only)
    --fail-on-500      Exit with code 1 if any 500 errors are found

Exit codes::

    0   No 500 errors found (or --fail-on-500 not set)
    1   500 errors found (only with --fail-on-500)

Example CI usage::

    python wikiserver.py &
    sleep 3
    python scripts/crawl-wiki.py --fail-on-500 --report crawl-report.json

Design notes
------------
- Uses stdlib only (no external dependencies).
- Follows only same-origin links; skips static files, destructive actions,
  and logout/attachment-download URLs.
- Deduplicates by normalized path (fragment-stripped).
- Classifies errors into patterns for easier triage.
- The crawler is BFS (breadth-first), so high-traffic pages are tested first.
- Concurrent fetching via ThreadPoolExecutor (I/O-bound, GIL-safe).
"""

import argparse
import json
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser


# ── Link extraction ──────────────────────────────────────────────────

class _LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, val in attrs:
                if name == 'href' and val:
                    self.links.append(val)


# ── URL filtering ────────────────────────────────────────────────────

# Actions that modify data — never crawl these.
_DESTRUCTIVE_ACTIONS = frozenset([
    'DeletePage', 'RenamePage', 'revert', 'copy',
    'logout', 'Save', 'save',
])

# File extensions that are static resources, not wiki pages.
_STATIC_EXTENSIONS = frozenset([
    '.png', '.gif', '.jpg', '.jpeg', '.svg', '.ico',
    '.css', '.js', '.woff', '.woff2', '.ttf', '.eot',
    '.zip', '.tar', '.gz', '.pdf',
])


def _normalize(url, base):
    """Strip fragment, make path-only, return None if off-site."""
    url = url.split('#')[0]
    if not url:
        return None
    if url.startswith(base):
        url = url[len(base):]
    if url.startswith(('http://', 'https://', 'javascript:', 'mailto:')):
        return None
    if not url.startswith('/'):
        return None
    return url


def _should_visit(path):
    """Return True if this path is worth crawling."""
    lower = path.lower()

    # Static resources
    if '/moin_static' in lower:
        return False
    for ext in _STATIC_EXTENSIONS:
        if lower.endswith(ext):
            return False

    # Destructive or side-effectful actions
    parsed = urllib.parse.urlparse(path)
    params = urllib.parse.parse_qs(parsed.query)
    action = params.get('action', [''])[0]
    if action in _DESTRUCTIVE_ACTIONS:
        return False

    # Attachment downloads (binary files)
    if 'action=AttachFile' in path and 'do=get' in path:
        return False

    return True


# ── Error classification ─────────────────────────────────────────────

def _classify_error(code, path):
    """Return a short category string for grouping."""
    if code == 404:
        return '404_not_found'
    if code == 500:
        parsed = urllib.parse.urlparse(path)
        params = urllib.parse.parse_qs(parsed.query)
        action = params.get('action', ['view'])[0]
        return f'500_{action}'
    if code == 0:
        return 'timeout_or_connection_error'
    return f'http_{code}'


# ── Single-page fetch ────────────────────────────────────────────────

def _fetch_one(base_url, norm, timeout):
    """Fetch a single page. Returns (norm, status, body_or_none, error_msg)."""
    url = base_url + norm
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=timeout)
        status = resp.getcode()
        body = resp.read().decode('utf-8', errors='replace')
        return (norm, status, body, None)
    except urllib.error.HTTPError as e:
        return (norm, e.code, None, str(e))
    except Exception as e:
        return (norm, 0, None, str(e))


# ── Crawler ──────────────────────────────────────────────────────────

def crawl(base_url, max_pages=0, timeout=10, workers=8):
    """
    Crawl the wiki starting from base_url.

    Uses a thread pool of ``workers`` threads to fetch pages concurrently.
    New links discovered from fetched pages are fed back into the queue.

    Returns (visited_count, errors, category_counts) where:
      - errors is a list of (path, status_code, message) tuples
      - category_counts is a dict of {category: count}
    """
    visited = set()
    queue = ['/']
    errors = []
    categories = {}
    count = 0
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        while queue:
            if max_pages and count >= max_pages:
                break

            # Drain up to `workers` items from the queue
            batch = []
            while queue and len(batch) < workers:
                if max_pages and count + len(batch) >= max_pages:
                    break
                path = queue.pop(0)
                norm = _normalize(path, base_url)
                if norm is None or norm in visited:
                    continue
                visited.add(norm)
                batch.append(norm)

            if not batch:
                break

            # Submit batch concurrently
            futures = {
                pool.submit(_fetch_one, base_url, norm, timeout): norm
                for norm in batch
            }

            for future in as_completed(futures):
                norm, status, body, error_msg = future.result()
                count += 1

                if count % 100 == 0:
                    print(f'  ... {count} pages visited, '
                          f'{len(queue)} queued, '
                          f'{len(errors)} errors',
                          file=sys.stderr)

                if status == 200 and body:
                    # Extract and enqueue links
                    parser = _LinkExtractor()
                    try:
                        parser.feed(body)
                    except Exception:
                        pass  # malformed HTML is OK
                    for link in parser.links:
                        ln = _normalize(link, base_url)
                        if ln and ln not in visited and _should_visit(link):
                            queue.append(ln)
                elif error_msg or status != 200:
                    msg = error_msg or f'HTTP {status}'
                    cat = _classify_error(status, norm)
                    categories[cat] = categories.get(cat, 0) + 1
                    errors.append((norm, status, msg))

    return count, errors, categories


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Crawl a MoinMoin wiki and report HTTP 500 errors.',
    )
    parser.add_argument(
        '--base-url', default='http://localhost:8080',
        help='Base URL of the wiki (default: http://localhost:8080)',
    )
    parser.add_argument(
        '--max-pages', type=int, default=0,
        help='Stop after N pages; 0 = unlimited (default: 0)',
    )
    parser.add_argument(
        '--timeout', type=int, default=10,
        help='Per-request timeout in seconds (default: 10)',
    )
    parser.add_argument(
        '--workers', type=int, default=8,
        help='Number of concurrent fetch threads (default: 8)',
    )
    parser.add_argument(
        '--report', metavar='FILE',
        help='Write detailed JSON report to FILE',
    )
    parser.add_argument(
        '--fail-on-500', action='store_true',
        help='Exit with code 1 if any HTTP 500 errors are found',
    )
    args = parser.parse_args()

    print(f'Crawling {args.base_url} (workers={args.workers}) ...',
          file=sys.stderr)
    t0 = time.time()
    count, errors, categories = crawl(
        args.base_url,
        max_pages=args.max_pages,
        timeout=args.timeout,
        workers=args.workers,
    )
    elapsed = time.time() - t0

    # Separate 500s from other errors
    errors_500 = [(p, c, m) for p, c, m in errors if c == 500]
    errors_other = [(p, c, m) for p, c, m in errors if c != 500]

    # Summary
    print(f'\n{"=" * 60}', file=sys.stderr)
    print(f'Crawl complete: {count} pages in {elapsed:.1f}s '
          f'({args.workers} workers)', file=sys.stderr)
    print(f'  500 errors: {len(errors_500)}', file=sys.stderr)
    print(f'  Other errors (404, timeout, etc.): {len(errors_other)}',
          file=sys.stderr)

    if categories:
        print(f'\nError categories:', file=sys.stderr)
        for cat, n in sorted(categories.items(),
                             key=lambda x: -x[1]):
            print(f'  {cat}: {n}', file=sys.stderr)

    if errors_500:
        print(f'\n500 errors:', file=sys.stderr)
        for path, code, msg in errors_500[:20]:
            decoded = urllib.parse.unquote(path)
            print(f'  {decoded}', file=sys.stderr)
        if len(errors_500) > 20:
            print(f'  ... and {len(errors_500) - 20} more',
                  file=sys.stderr)

    # JSON report
    if args.report:
        report = {
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'base_url': args.base_url,
            'pages_visited': count,
            'elapsed_seconds': round(elapsed, 1),
            'workers': args.workers,
            'error_counts': categories,
            'errors_500': [
                {'path': p, 'message': m} for p, c, m in errors_500
            ],
            'errors_other': [
                {'path': p, 'code': c, 'message': m}
                for p, c, m in errors_other
            ],
        }
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f'\nReport written to {args.report}', file=sys.stderr)

    if args.fail_on_500 and errors_500:
        sys.exit(1)


if __name__ == '__main__':
    main()
