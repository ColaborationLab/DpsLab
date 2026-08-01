# Release key custody

DpsLab release signatures use Ed25519. The repository, addon, CI, logs, and
release artifacts must never contain a production private key.

The initial custody model is Windows current-user protection. Machine-wide
protection is forbidden. The protected container records only closed metadata,
a public-key fingerprint, and protected ciphertext. Signing returns only a
detached signature over exact canonical manifest bytes.

Production key generation, backup, recovery, rotation, revocation, signing,
publication, and activation are separate attended operations. The implemented
tests use deterministic synthetic keys and simulated protection; they do not
invoke Windows protection with real secret material.

Before a future production ceremony, Daniel must approve the storage location,
offline encrypted recovery media, recovery verification procedure, validity
window, and public registry entry. A valid signature grants release eligibility
only and never implies publication.
