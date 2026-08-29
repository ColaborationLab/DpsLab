# DpsLab Intellectual Property and Monetization Boundary 0.1

## Status and decision

`design_only`. This document records product direction; it creates no license,
EULA, trademark registration, Patreon page, public repository, paid offering,
or distribution channel.

The selected product direction is:

- the in-game DpsLab addon remains free of charge, source-visible, and fully
  functional for every user;
- the local desktop application remains a proprietary DpsLab product, with a
  future commercial Qt entitlement required before a production PySide6 build;
- voluntary support is external to World of Warcraft and never conditions
  access to an addon, an addon feature, a recommendation, a guide, an update,
  installation, or support service.

This is intentionally not an open-source declaration for the whole project.
It separates the visibility and free-distribution obligations of the addon from
the proprietary desktop product and from the DpsLab brand.

## Blizzard-compatible addon boundary

The published Blizzard UI Add-On Development Policy requires add-ons to be
free, code-visible, free of advertising, and without in-game donation requests.
Accordingly, a future DpsLab addon must:

- contain no paywall, premium build, paid data pack, paid recommendation,
  required donation, advertisement, or donor-only functional path;
- expose its addon source code without obfuscation and preserve required
  copyright and third-party notices;
- contain no Patreon, payment, donation, or commercial call-to-action in its
  UI, slash commands, strings, screenshots, or release package;
- use only APIs permitted by Blizzard and remain performance-conscious;
- treat unknown, stale, incompatible, or unauthenticated inputs as
  non-actionable rather than promising a result.

An external project website or distribution page may later offer voluntary
support only after a separate platform and legal review. It must state plainly
that donations are optional and provide no game functionality or service in
return.

## Ownership model

No ownership or registration is claimed by this document. Before public
distribution, Daniel must designate the legal rightsholder and retain evidence
of contributions. The future operating model is:

| Asset | Intended control | Required future evidence |
| --- | --- | --- |
| DpsLab desktop code and release tooling | Proprietary | rightsholder record, contributor terms, third-party notices, release signature provenance |
| DpsLab addon code | Source-visible and free to use with WoW | addon distribution terms reviewed for Blizzard compatibility, copyright notices, complete third-party notices |
| DpsLab name, logo, and visual identity | Brand asset; no registration claimed | availability search, jurisdictional trademark advice, registration decision, approved brand-use rules |
| Generated recommendations and current-source records | DpsLab data product subject to source constraints | provenance, freshness, applicability, and source-specific use review |

Until a registration is approved and recorded, use no `®` symbol and make no
claim that the name is registered. A future clearance should check the actual
markets of planned distribution before public launch; it is not a web-search
substitute.

## Voluntary support model

The recommended platform is Patreon, used as an off-game creator-support and
community channel. Patreon states that creators retain ownership of creations
posted there, subject to the platform license necessary to operate the service.

Permitted candidate benefits, subject to a later Patreon and legal review, are
non-functional creator updates, development diaries, optional external credit,
and community discussion. They must not grant access to DpsLab software,
features, game data, recommendations, downloads, updates, priority technical
support, installation assistance, or a service related to the addon.

The Patreon page must identify DpsLab as an independent community project and
must not imply Blizzard endorsement, affiliation, or ownership. It must not
publish Blizzard-owned artwork, text, game data, or other material without a
separate rights assessment.

## Practical protection controls

1. Keep desktop, signing material, release metadata, private test fixtures,
   and non-public research in private, access-controlled repositories.
2. Before any public addon repository, perform a repository split and secret
   scan; publish only the source-visible addon, its notices, reproducible build
   inputs, and safe documentation.
3. Establish contributor terms before accepting external code, designs, or
   assets. Contributions must state ownership and licensing rights clearly.
4. Preserve immutable release evidence: commit identity, reviewed artifact
   hashes, SBOM, dependency license inventory, signing verification, and
   revocation/update records.
5. Register or reserve domains and public account names only after name and
   trademark clearance. Do not spend funds, register marks, or create accounts
   under this design contract.
6. Maintain a public security-reporting path before broad release, with no
   secrets, recovery material, or private user information placed in public
   repositories or community posts.

## Required gates before external launch

No public addon, Patreon offering, desktop release, or trademark claim may
proceed until a separate authorization verifies all of:

1. the legal rightsholder and contributor chain;
2. a lawyer or qualified local adviser review of the planned notices, terms,
   trademark territory, and Qt commercial entitlement;
3. Blizzard-policy review of the actual addon contents and its external
   donation language;
4. a clean public-release repository split, secret scan, dependency/SBOM
   evidence, and reproducible signed release process;
5. platform terms, tax, privacy, and community-moderation requirements for the
   selected Patreon account.

## Explicit exclusions

This design does not authorize a license text, EULA, trademark filing, public
repository, Patreon account, payment handling, advertisement, paid content,
desktop packaging, updater, release, addon implementation, SimulationCraft,
or a real comparison.

## Sources consulted

- Blizzard UI Add-On Development Policy:
  <https://us.forums.blizzard.com/en/wow/t/ui-add-on-development-policy/24534/1>
- Qt licensing options:
  <https://doc.qt.io/qt-6/licensing.html>
- Qt for Python commercial use:
  <https://doc.qt.io/qtforpython-6.10/commercial/index.html>
- Patreon Terms of Use:
  <https://www.patreon.com/policy/legal>
- GitHub guidance on repository licensing and default copyright:
  <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository>
