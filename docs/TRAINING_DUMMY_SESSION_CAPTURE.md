# Training dummy session capture

`training_dummy_session_capture_0_1` provides only synthetic, injected inputs.
It has no real WoW API calls, event registration, persistence, network,
recommendations, or simulation. A later separately authorized block may replace
the injected boundary with a reviewed, player-invoked real observation route.

The transport is canonical JSON prefixed with `DPSLAB-SYNTHETIC-TRAINING-0.1`.
It carries a bounded aggregate only: terminal session state, duration, target
classification, three bounded metrics, and an explicit synthetic safety marker.
