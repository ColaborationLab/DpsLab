# PySide6 Supply-Chain Review 0.1

## Status

`design_only`. This review records a licensing direction but does not approve a
package, version, download, installation, lock update, UI implementation, or
distribution.

## Observed package facts

On 2026-08-29, the official PyPI release history showed PySide6 `6.11.2` as
the current release observation. It is a discovery datum only: the future
integration must re-query official metadata and select an exact version then.

PyPI describes `PySide6` as an official Qt for Python package and states that
the umbrella wheel is an alias for `PySide6_Essentials` and
`PySide6_Addons`. The first implementation should evaluate the minimum exact
Qt module package set necessary for typed Qt Widgets views, rather than take
the umbrella package by default. It must demonstrate the required Widgets API
is available in that exact, hash-verified artifact set.

## Selected license direction

The selected direction for a future production distribution of the proprietary
DpsLab desktop application is a **Qt commercial license**. This keeps the
desktop application's proprietary licensing path clear and avoids asserting
LGPL compliance before its detailed distribution obligations are reviewed.

This is a product and distribution decision, not a purchase authorization. No
Qt license may be purchased, commercial wheel obtained, or Qt package installed
until a separate, costed acquisition and dependency-integration authorization.

Qt for Python documents community LGPLv3/GPL licensing and a commercial option.
Before adoption, the following evidence remains mandatory:

1. Confirm the intended proprietary distribution model and the exact commercial
   Qt for Python entitlement and package channel.
2. Confirm the notices, attribution, and third-party license inventory needed
   by the chosen distribution method.
3. Record the acquired license evidence and its supported Windows package set.

This is a compliance boundary, not an engineering inference. DpsLab must not
claim either commercial entitlement or LGPL compliance without corresponding
evidence and, where needed, legal review.

## Required acquisition evidence

Before installation, a dedicated implementation contract must require all of:

- current PyPI JSON metadata obtained from `pypi.org` over HTTPS;
- exact distribution name, version, Python ABI tag, Windows architecture,
  upload identity, and SHA-256 per selected wheel;
- an explicit and complete transitive dependency inventory, including
  `shiboken6` where required by the selected Qt package set;
- acquisition only into a disposable environment after hashes are fixed;
- a negative test that rejects a mismatched wheel, a source distribution, an
  unsupported architecture, an unlisted transitive package, or a missing
  hash;
- a record of the source URL and the identity evidence without storing package
  bytes in the repository.

## Required repository changes in a future implementation

A separate, closed implementation contract may modify only the dependency and
synthetic-UI boundary. It must include, at minimum:

- Python dependency declaration and the Windows CPython 3.13 hash lock;
- SBOM regeneration and dependency-vulnerability policy/audit coverage;
- CI validation of the exact lock;
- typed synthetic desktop view-state fixtures and tests;
- documentation of license notices and the local-only UI boundary.

The final exact route list must be reviewed after the package inventory is
known. This prevents a new Qt dependency from being adopted through an
unbounded lock rewrite.

## Deployment constraint

Qt documents desktop deployment tooling, but it does not constitute secure
auto-update functionality. Packaging, installer behavior, signed metadata,
rollback protection, revocation, and Windows trust signaling remain distinct
release-security contracts.

## Official sources consulted

- PyPI PySide6 metadata: <https://pypi.org/pypi/PySide6/json>
- PyPI PySide6 release history: <https://pypi.org/project/PySide6/>
- Qt for Python overview and license options:
  <https://doc.qt.io/qtforpython-6/>
- Qt for Python license inventory:
  <https://doc.qt.io/qtforpython-6/licenses.html>
- Qt for Python deployment:
  <https://doc.qt.io/qtforpython-6/deployment/index.html>
