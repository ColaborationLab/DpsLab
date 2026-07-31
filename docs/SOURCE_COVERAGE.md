# Source Coverage and Historical Evidence 0.1

DpsLab separates active coverage from retained evidence. Current guidance may
use only compatible, complete, fresh, non-invalidated captures required by the
active manifest. Historical captures remain content-addressed for explicit
audit, comparison, regression testing, rollback, and recovery.

Historical evidence never fills a current coverage gap and never becomes a
recommendation implicitly. Every historical comparison names both capture IDs,
source revisions, and hashes and is marked `historical_only`.

The synthetic implementation is pure and offline. It validates closed JSON,
canonical UTF-8 bytes, SHA-256 projections, source identity, acquisition and
license policy, compatibility, freshness, invalidation, and role-specific
mandatory families. Complete coverage produces at most `pending_review`.

There is no source retrieval, URL handling, network client, database, real WoW
data, SimulationCraft, addon behavior, UI, signing, packaging, or distribution.
