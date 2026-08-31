"""Explicit sanitized coordinator for one supported local addon observation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .addon_observation_acquisition import (
    AddonObservationAcquisitionError,
    AddonObservationAcquisition,
    acquire_addon_observation_from_installation,
)
from .addon_character_identity_transport import CharacterIdentitySnapshot
from .addon_specialization_registry_transport import ClassSpecializationRegistrySnapshot
from .addon_observation_transport import SyntheticAddonObservation
from .retail_installation import RetailInstallationError
from .retail_installation_store import (
    RetailInstallationStoreError,
    load_retail_installation,
)


@dataclass(frozen=True)
class AddonObservationImportResult:
    state: str
    reason: str | None
    byte_count: int
    source_sha256: str | None
    observation: (
        SyntheticAddonObservation
        | CharacterIdentitySnapshot
        | ClassSpecializationRegistrySnapshot
        | None
    )
    observation_type: str | None = None


def _rejected(reason: str) -> AddonObservationImportResult:
    return AddonObservationImportResult("rejected", reason, 0, None, None)


def _observation_type_matches(acquired: AddonObservationAcquisition) -> bool:
    return (
        acquired.observation_type == "synthetic_observation"
        and isinstance(acquired.observation, SyntheticAddonObservation)
    ) or (
        acquired.observation_type == "character_identity_snapshot"
        and isinstance(acquired.observation, CharacterIdentitySnapshot)
    ) or (
        acquired.observation_type == "class_specialization_registry_snapshot"
        and isinstance(acquired.observation, ClassSpecializationRegistrySnapshot)
    )


def _public_result(
    acquired: AddonObservationAcquisition,
) -> AddonObservationImportResult:
    if acquired.state == "absent":
        if acquired != AddonObservationAcquisition("absent", 0, None, None):
            raise RuntimeError("addon_observation_import_state_invalid")
        return AddonObservationImportResult("absent", None, 0, None, None)
    if acquired.state == "cleared":
        if (
            acquired.byte_count < 1
            or acquired.source_sha256 is None
            or len(acquired.source_sha256) != 64
            or acquired.observation is not None
            or acquired.observation_type is not None
        ):
            raise RuntimeError("addon_observation_import_state_invalid")
        return AddonObservationImportResult(
            "cleared", None, acquired.byte_count, acquired.source_sha256, None
        )
    if acquired.state == "available":
        if (
            acquired.byte_count < 1
            or acquired.source_sha256 is None
            or len(acquired.source_sha256) != 64
            or acquired.observation is None
            or acquired.observation_type
            not in {
                "synthetic_observation",
                "character_identity_snapshot",
                "class_specialization_registry_snapshot",
            }
            or not _observation_type_matches(acquired)
        ):
            raise RuntimeError("addon_observation_import_state_invalid")
        return AddonObservationImportResult(
            "available",
            None,
            acquired.byte_count,
            acquired.source_sha256,
            acquired.observation,
            acquired.observation_type,
        )
    raise RuntimeError("addon_observation_import_state_invalid")


def import_addon_observation(config_root: Path) -> AddonObservationImportResult:
    """Import once through the existing store, process gate, and strict decoder."""
    try:
        stored = load_retail_installation(config_root)
    except RetailInstallationStoreError:
        return _rejected("configuration_invalid")
    if stored.state == "absent":
        return AddonObservationImportResult("not_configured", None, 0, None, None)
    if stored.state != "selected" or stored.selection is None:
        raise RuntimeError("addon_observation_import_configuration_state_invalid")
    try:
        acquired = acquire_addon_observation_from_installation(stored.selection)
    except AddonObservationAcquisitionError as exc:
        if str(exc) == "addon_observation_acquisition_wow_not_stopped":
            return _rejected("wow_not_stopped")
        return _rejected("source_invalid")
    except RetailInstallationError:
        return _rejected("source_invalid")
    return _public_result(acquired)


def import_synthetic_addon_observation(
    config_root: Path,
) -> AddonObservationImportResult:
    """Compatibility entry for the original synthetic-only coordinator."""
    return import_addon_observation(config_root)
