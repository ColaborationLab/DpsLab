# Desktop Interface Architecture 0.1

## Purpose and boundary

The future desktop interface is a local, read-first presentation layer for
DpsLab. It helps a player understand already validated profiles, templates,
comparison records, provenance, limitations, and security state. It is not a
simulation engine, an optimizer, an addon replacement, or a data-acquisition
agent.

The interface consumes typed application view models. It must never interpret
raw profile text, HTML, scanner output, SavedVariables, or network responses
directly. A missing, invalid, expired, incompatible, or pending-review input
is represented as unavailable; it is never rendered as a recommendation.

## Local-only responsibilities

1. Explain the current subject, specialization, content context, evidence
   provenance, and freshness of a validated template or result.
2. Present comparison scope, frozen inputs, result status, uncertainty, and
   stated limitations without generalizing one result to another character or
   scenario.
3. Show non-actionable states plainly: `unavailable`, `pending_review`,
   `incompatible`, `expired`, `invalid`, and `blocked`.
4. Allow a user to inspect locally stored, already approved records and to
   copy non-sensitive summaries deliberately.
5. Make consent and destructive boundaries visible before any future action
   that would create a run, contact a source, import addon data, or publish an
   artifact.

## Explicit non-responsibilities

- No network requests, telemetry, account linking, or automatic game-data
  retrieval.
- No SimulationCraft invocation, comparison creation, profile transformation,
  catalog mutation, or recommendation generation.
- No addon communication, SavedVariables parsing, release download, update
  installation, signing-key access, or release publication.
- No attempt to repair malformed data, infer approval, or hide security
  warnings.

## Information model

The interface receives only a closed `DesktopViewState` equivalent from a
future adapter. That state separates:

| Area | Required display data | Fail-closed rule |
| --- | --- | --- |
| Subject | class, specialization, role, supported build/interface range | no identity means no subject-specific view |
| Template | identifier, version, provenance, freshness, applicability, review status | anything other than approved and applicable is non-actionable |
| Comparison | frozen scope, status, uncertainty, result classification, limitations | incomplete or mismatched evidence has no winner display |
| Safety | local data state, integrity status, known limitations, blocked actions | an unknown security state blocks associated actions |
| Provenance | source identifiers, revision, timestamp, and hashes where available | absent provenance is displayed as unavailable, not trusted |

The adapter owns validation and conversion. Presentation components only use
the closed view state and cannot receive arbitrary dictionaries or executable
callbacks from stored data.

## Screen structure

### Home / readiness

The opening screen answers: “what can safely be viewed now?” It shows the
selected local subject only when there is one, plus a compact list of data
states. It does not offer a generic “optimize” control.

### Template detail

This view presents template purpose, supported role and context, parameter
families, provenance, freshness, and limitations. For tanks and healers, the
view must state that DPS guidance is subordinate to the role-specific safety
context; it may not imply that damage is the sole objective.

### Comparison detail

This view makes the comparison contract visible before any interpretation:
which inputs were frozen, the exact scenario, result status, statistical
uncertainty, and the limits on reuse. It does not expose a winner if the
record is invalid, partial, stale, or outside its declared applicability.

### Evidence and safety detail

This view lets the user inspect provenance and current security posture using
non-sensitive identifiers and status only. It explains blocked or
pending-review conditions in plain language and offers no bypass control.

## Interaction and privacy requirements

- Local data remains local by default. Copy actions require an explicit user
  gesture and copy only the selected visible summary.
- No invisible background work. A future long operation must expose its
  purpose, inputs, current state, cancellation boundary, and result location.
- Keyboard navigation, visible focus, semantic labels, scalable text, and
  non-color-only status indicators are mandatory.
- Errors use stable, non-sensitive descriptions. Paths, process output,
  credentials, raw source documents, and scanner logs are not displayed by
  default.

## Future implementation boundary

An implementation proposal may introduce only these new layers after a
separate authorization:

1. typed desktop view-state models and an adapter from existing validated
   records;
2. a framework-neutral presentation contract and deterministic fixtures;
3. local, accessible screens for readiness, template detail, comparison
   detail, and evidence/safety detail;
4. tests demonstrating that unavailable and pending-review inputs have no
   actionable recommendation or execution control.

Framework selection, persistent UI preferences, real-data import, addon
exchange, network operations, simulation execution, and packaging remain
separate decisions. No graphical interface is implemented by this document.
