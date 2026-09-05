# Advisor synthetic guidance package

This package is a non-actionable synthetic fixture. It demonstrates the closed
shape for generic statistic targets, gear-priority labels, and priority-display
labels for damage, tank, and healer. It has no real game data, event handling,
inventory access, persistence, network, or ability automation.

The desktop parser accepts only the canonical, byte-bounded JSON form following
the `DPSLAB-SYNTHETIC-ADVISOR-0.1` prefix. It rejects duplicate JSON keys,
non-finite numeric constants, unknown or missing fields, any non-synthetic or
current-content lifecycle marker, actionable safety state, incompatible role
safety ordering, and non-canonical serialization. The resulting role summary
is immutable. These controls validate a synthetic fixture only; they do not
establish a current catalog, personalized result, live recommendation, or
in-game automation capability.
