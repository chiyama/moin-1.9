# ADR-004: Project Scope and Security Policy

## Status
Accepted (2026-10-02)

## Background
This port is used by sites that are built and operated elsewhere (for example,
the `websites` repository). Decisions about how those sites are built and run
(static export vs. public server, hosting, access control in front of the site)
were starting to be discussed in this repository.

The port inherits all upstream MoinMoin 1.9 security fixes up to 1.9.11, but
upstream 1.9 is no longer maintained, and the vendored libraries and the Python
runtime have known vulnerabilities of their own.

## Decision

### Scope
- This repository maintains MoinMoin itself: correctness on Python 3, and security.
- Operational decisions for sites that use it are made outside this repository.
  Documents here may describe what a configuration option does, but do not
  recommend how a particular site should be operated.

### Security policy
- Aim to resolve every known vulnerability as far as possible. This covers:
  - upstream MoinMoin 1.9 vulnerabilities (keep their fixes intact through the port)
  - vulnerabilities in vendored libraries under `MoinMoin/support/`
  - vulnerabilities in, and end of support of, the Python runtime
  - weaknesses introduced by the Python 3 port itself
- The inventory and the status of each item live in
  [docs/security/vulnerabilities.md](../security/vulnerabilities.md).
  Update it in the same change that fixes an item.
- When choosing what to work on, known vulnerabilities come first.
- A fix should come with a test that fails without it, where practical.
- Vendored libraries are upgraded by replacing the whole package (ADR-002).
  Partial edits under `MoinMoin/support/` remain prohibited.
- If an item cannot be resolved, record why and what limits the exposure
  (for example, a configuration option that disables the affected feature).

## Consequences
- Each security fix updates the inventory, so the inventory always reflects the code.
- Upgrading vendored libraries (notably werkzeug) and the Python version may require
  changes across the codebase; these are planned as separate work sessions.
