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

## Attended production ceremony

The ceremony is a single attended transaction with four checkpoints. Passing a
checkpoint does not authorize the next one.

### 1. Readiness checkpoint

- The repository and `origin/main` are clean, synchronized, and CI-green.
- The ceremony tool and protected signing adapter match their audited commits.
- Daniel confirms that the Windows account is his controlled operator account.
- A user-selected local container directory outside every repository and cloud
  synchronization root is available.
- Two user-selected removable media are present: one for the encrypted recovery
  copy and one for the non-secret recovery record. Their exact paths are shown
  before any write.
- No screen sharing, terminal recording, clipboard manager, or automatic backup
  application is active.

Failure of any item aborts before key generation.

### 2. Generation checkpoint

Daniel must provide an explicit, time-bounded confirmation that names the key
identifier and the three resolved destinations. Only then may one Ed25519 key
be generated in memory, protected immediately with current-user DPAPI, and
written atomically to the local container path. Plaintext private bytes must
never be printed, copied to the clipboard, serialized, or written to disk.

The initial proposed identity is `dpslab.release.ed25519.001`. Its proposed
validity is one year from the ceremony time. These values remain proposals
until the attended confirmation.

### 3. Recovery checkpoint

The recovery copy must be encrypted independently of DPAPI so it remains usable
after loss of the Windows profile or computer. Its passphrase is chosen and
retained by Daniel outside the repository, chat, logs, environment variables,
and the non-secret recovery record.

Verification must decrypt the recovery copy only in memory, derive its public
key, compare the SHA-256 fingerprint with the local protected container, then
discard the recovered private bytes. The check records only success, algorithm,
key identifier, fingerprint, UTC time, and artifact SHA-256. A failed or
different fingerprint aborts and quarantines both artifacts; it never replaces
the public registry automatically.

### 4. Registry checkpoint

Only after recovery verification may a candidate public registry entry be
prepared. It contains the public key, fingerprint, validity window, status
`trusted`, and no private material. Human review and repository publication of
that entry are separate transactions. The new key cannot sign a production
release until the public registry is independently reviewed and published.

## Abort conditions

Abort immediately on an unexpected path, existing destination file, missing or
rewritable media, DPAPI error, recovery mismatch, CI drift, dirty repository,
operator-account mismatch, key-identifier collision, clock ambiguity, or any
attempt to continue without a checkpoint confirmation. An abort may remove
only incomplete temporary files created by that ceremony; it must preserve
completed evidence and never retry automatically.

## Non-secret evidence record

The ceremony record may contain only:

- ceremony identifier and UTC timestamps;
- operator attestation identifier;
- audited tool commit and repository commit;
- key identifier, algorithm, public key and SHA-256 fingerprint;
- validity window;
- hashes and resolved paths of the protected container and encrypted recovery
  artifact, with removable-media volume identifiers;
- checkpoint outcomes and explicit abort reason when applicable.

It must not contain private bytes, recovery ciphertext, passphrases, DPAPI
blobs, optional entropy, environment values, or filesystem contents.

## Synthetic dry run

`release_key_ceremony` evaluates the ceremony contract without effects. It
accepts only synthetic identifiers and `synthetic://` destinations, requires
all seven readiness observations and four ordered confirmations, and returns a
content-hashed non-secret evidence record. Production mode is structurally
unavailable. The evaluator performs no filesystem, media, DPAPI, key,
registry, signing, network, publication, or activation operation.

## Native-session requirement

The first production ceremony must run under Daniel's normal interactive
Windows identity. It must refuse Codex sandbox, service, CI, elevated helper,
or other surrogate identities because current-user DPAPI would bind the key to
the wrong account. The ceremony must show the effective Windows identity and
wait for Daniel to confirm it before checking destinations.

The current Codex execution identity was observed as
`DANIELPC\CodexSandboxOffline`; therefore it is explicitly ineligible for the
production ceremony. Removable-volume enumeration was also denied in that
context. These are expected fail-closed results, not errors to bypass.

A later unrestricted read-only preflight confirmed `DANIELPC\dpcs9` as the
native identity and found `F:` (`Black 3Tb`) healthy and available. Daniel
attests that it is external and controlled by him. A second external medium
must be connected and identified before the production ceremony can advance.
