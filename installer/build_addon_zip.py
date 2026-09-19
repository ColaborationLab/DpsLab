"""Create the public, installable DpsLab addon ZIP without local player data."""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ADDON_FILES = (
    "DpsLab.toc", "Localization.lua", "CharacterIdentityObservation.lua",
    "CharacterSpecializationRegistryObservation.lua", "CharacterEquipmentObservation.lua",
    "DpsLabRealRecommendation.lua", "DpsLab.lua", "DefaultItemScoreProfiles.lua",
    "ItemScoreProfiles.lua",
)
EXCLUDED_TOC_FILES = {
    "SyntheticGuidance.lua", "SyntheticExchange.lua", "SyntheticObservation.lua",
    "TrainingDummySession.lua", "AdvisorSyntheticGuidance.lua",
}


def build(source: Path, output: Path) -> Path:
    """Write a deterministic addon-root ZIP after validating the public manifest."""
    source = source.resolve()
    if not source.is_dir() or any(not (source / name).is_file() for name in ADDON_FILES):
        raise ValueError("addon_source_invalid")
    toc = (source / "DpsLab.toc").read_text(encoding="utf-8")
    if "## Version: 0.2.0" not in toc or any(name not in toc for name in ADDON_FILES[1:]):
        raise ValueError("addon_manifest_invalid")
    public_toc = "\n".join(line for line in toc.splitlines() if line not in EXCLUDED_TOC_FILES) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("DpsLab/DpsLab.toc", public_toc)
        for name in ADDON_FILES[1:]:
            archive.write(source / name, f"DpsLab/{name}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a public DpsLab addon ZIP")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "addon" / "DpsLab")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
