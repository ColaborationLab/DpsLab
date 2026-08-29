# Desktop Framework Selection 0.1

## Decision

The recommended direction for the first local DpsLab desktop interface is
**PySide6 with Qt Widgets**. This is a direction for a later controlled
implementation, not an installed dependency or an approval to create an
interface.

Qt Widgets is preferred over Qt Quick for the first version because DpsLab's
initial screens are structured, read-first views: status panels, tables,
provenance, limitations, and non-actionable safety states. A later design may
evaluate Qt Quick independently if an interaction genuinely needs it.

## Candidate comparison

| Candidate | Fit | Reason not selected for first implementation |
| --- | --- | --- |
| PySide6 / Qt Widgets | Recommended | Adds a substantial native dependency, so version pinning, SBOM, license review, and Windows packaging need a separate supply-chain contract. |
| Tkinter / ttk | Viable fallback | It is part of Python and suitable for a small utility, but its appearance and layout flexibility are a weaker fit for the planned multi-panel, provenance-heavy application. Tkinter also bridges Python calls into a Tcl interpreter, so its event and threading model requires care. |
| Tauri / web frontend | Not selected | Introduces Rust, JavaScript/HTML, a WebView, frontend dependency management, and a larger web-facing security and build surface without improving the local Python domain boundary. |

## Why PySide6 fits DpsLab

- The application already has a Python core; PySide6 is Qt's official Python
  binding and avoids a second application language for the initial UI.
- Qt supplies native desktop controls and an established deployment path for
  Windows, while keeping the UI separate from domain validation.
- Widgets can render the required unavailable, stale, pending-review, and
  blocked states without embedding external web content.
- The selected direction is compatible with a future signed distribution
  pipeline, but does not solve updating or signing by itself.

Qt for Python is distributed under LGPLv3/GPLv3 or a commercial license.
Before adoption, DpsLab must perform a license-compliance review for the exact
chosen distribution and packaging method; this document makes no legal
conclusion. Qt's official deployment tooling can generate desktop artifacts,
but its documentation also notes that packaging tools do not provide an
application-update mechanism. That remains a separate signed-update decision.

## Security and operating constraints

1. Use an official Python.org interpreter and a project-local virtual
   environment; do not use the Microsoft Store interpreter for this path.
2. Add PySide6 only through a version- and hash-locked dependency update,
   SBOM regeneration, vulnerability audit, static scan, and CI verification.
3. Treat the UI as an untrusted presentation boundary: it receives typed view
   state and has no direct access to profiles, raw source documents, process
   runners, keys, network clients, or addon data.
4. Keep the first UI local-only: no WebView, remote resources, telemetry,
   update checks, or background communication.
5. Future packaging must be an isolated contract. It must assess executable
   provenance, installer behavior, rollback protection, Windows trust
   signaling, and update signature verification.

## Closed future implementation scope

A subsequent implementation proposal may be limited to these candidate paths,
subject to a separate dependency and license review:

- `desktop-app/pyproject.toml`;
- `desktop-app/requirements-ci-win-py313.lock`;
- `security/sbom-runtime-win-py313.spdx.json`;
- `security/dependency_vulnerability_policy_0_1.json`;
- `desktop-app/src/dpslab/desktop_view_state.py`;
- `desktop-app/src/dpslab/desktop_interface.py`;
- `desktop-app/tests/test_desktop_view_state.py`;
- `desktop-app/tests/test_desktop_interface.py`;
- `tools/tests/test_dependency_supply_chain.py`;
- `tools/tests/test_dependency_vulnerability_audit.py`;
- `docs/DESKTOP_INTERFACE_ARCHITECTURE.md`;
- `docs/DESKTOP_FRAMEWORK_SELECTION.md`;
- `docs/NEXT_TASK.md`.

That proposal must use synthetic typed view states only. It must not read real
profiles, execute SimulationCraft, create comparisons, contact the network,
or implement distribution.

## Official references consulted

- Qt for Python overview and licensing:
  <https://doc.qt.io/qtforpython-6/>
- Qt for Python deployment:
  <https://doc.qt.io/qtforpython-6/deployment/index.html>
- Python Tkinter documentation:
  <https://docs.python.org/3/library/tkinter.html>
- Tauri prerequisites:
  <https://v2.tauri.app/start/prerequisites/>
