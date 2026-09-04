# Live manual analysis export 0.1

`/dpslab export analysis` renders current equipped observations in a selectable
addon text box. `/dpslab export analysis <0-4>` additionally describes one
chosen bag. The player copies the text and pastes it into the desktop parser.
The addon does not print the payload, use the clipboard, write SavedVariables,
or send data over the network. A parsed desktop snapshot is not an analysis,
recommendation, simulation, or durable record.

The desktop parser accepts only the canonical `DPSLAB-LIVE-ANALYSIS-0.1`
envelope and computes an intake SHA-256 receipt. Compatibility and expansion
eligibility remain separate future controls.
