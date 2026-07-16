"""Closed schema 0.1 for one controlled A/B comparison."""

from __future__ import annotations

import re
import json
import tomllib
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


class ComparisonSpecError(ValueError):
    """The comparison spec is missing, open-ended, or violates protocol 0.1."""


def _closed(table: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(table) - allowed
    if unknown:
        raise ComparisonSpecError(f"Campos desconocidos en {label}: {sorted(unknown)}")


def _table(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ComparisonSpecError(f"Falta la tabla [{key}]")
    return value


def _text(table: dict[str, Any], key: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value:
        raise ComparisonSpecError(f"{key} debe ser texto no vacio")
    return value


def _integer(table: dict[str, Any], key: str) -> int:
    value = table.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ComparisonSpecError(f"{key} debe ser entero")
    return value


@dataclass(frozen=True, slots=True)
class ComparisonArm:
    key: str
    label: str
    item_id: int
    item_level: int
    source: str
    slot: str
    bonus_ids: tuple[int, ...]
    gem_id: int
    expected_profile_line: str

    @property
    def canonical_bonus_ids(self) -> tuple[int, ...]:
        """Canonical comparison form; serialization keeps ``bonus_ids`` order."""
        return tuple(sorted(self.bonus_ids))


@dataclass(frozen=True, slots=True)
class ComparisonProtocol:
    blocks: int
    iterations_per_run: int
    threads: int
    within_pair_pause_seconds: float
    between_block_pause_seconds: float
    timeout_seconds: float
    max_pair_attempts: int
    seeds: tuple[int, ...]
    orders: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ComparisonAnalysis:
    confidence_level: float
    epsilon_percent: float
    primary_method: str
    sensitivity_method: str


@dataclass(frozen=True, slots=True)
class ComparisonSpec:
    source_file: Path
    source_sha256: str
    comparison_id: str
    status: str
    base_profile: Path
    base_profile_sha256: str
    scenario: Path
    scenario_sha256: str
    arm_a: ComparisonArm
    arm_b: ComparisonArm
    evidence_manifest: Path
    evidence_sha256: str
    protocol: ComparisonProtocol
    analysis: ComparisonAnalysis
    simc_version: str
    simc_revision: str


ROOT_KEYS = {"schema_version", "comparison_id", "description", "status", "created_at", "frozen_at", "scope", "inputs", "arms", "normalization", "precision", "protocol", "seeds", "analysis", "software_requirements"}

EXPECTED_COMPARISON_ID = "flasil_neck_50228_vs_249368_v1"
EXPECTED_PROFILE_SHA256 = "f733c73d8455aca4c3efc81ce69c71aec899d7fd95585e38e989e983a055d738"
EXPECTED_SCENARIO_SHA256 = "93187338a61d1cfc330f5262abb0b9183acb727d310099eca7917138207c09aa"
EXPECTED_EVIDENCE_SHA256 = "0472ee720a94e8bb46d446b671bedd5d15c95a72cce808de6f20f69dd374e8fe"
EXPECTED_SEEDS = (1367750201, 618936042, 288306750, 1083574406, 1600660097, 1339438866, 1945530490, 1927693846)
EXPECTED_ARMS = {
    "a": (50228, 276, "equipped", (13440, 6652, 13668, 12699, 12798), 240906,
          "neck=,id=50228,gem_id=240906,bonus_id=13440/6652/13668/12699/12798"),
    "b": (249368, 276, "bag", (6652, 13668, 13334, 12798), 240906,
          "neck=,id=249368,gem_id=240906,bonus_id=6652/13668/13334/12798"),
}


def _exact_keys(table: dict[str, Any], keys: set[str], label: str) -> None:
    _closed(table, keys, label)
    missing = keys - set(table)
    if missing:
        raise ComparisonSpecError(f"Campos obligatorios ausentes en {label}: {sorted(missing)}")


def _validate_evidence(path: Path, root: Path) -> None:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ComparisonSpecError(f"Manifest de evidencia invalido: {exc}") from exc
    root_keys = {"evidence_manifest_schema_version", "comparison_id", "recorded_at", "provenance", "images", "profile_correlation", "compatibility_conclusion", "limitations"}
    _exact_keys(document, root_keys, "evidence_manifest")
    if document["evidence_manifest_schema_version"] != "0.1" or document["comparison_id"] != EXPECTED_COMPARISON_ID:
        raise ComparisonSpecError("Identidad del manifest no admitida")
    expected = {
        "eternal_voidsong_chain_tooltip.png": ("9f6d2d9ffcc83d1b5716c9aed823c9f9f5d1778f47ae5018ad91a5b867ab74e8", 249368, 276),
        "barbed_ymirheim_choker_tooltip.png": ("eccab6e476b344198e1a13c69a818174f0d1c9711506682c7752d061a74600f8", 50228, 276),
        "flawless_quick_garnet_socket.png": ("ced373ca0b8c95c368714adb8709ebf04db318fa355c763e49e0d8fd6f9eb35c", None, None),
    }
    images = document["images"]
    if not isinstance(images, list) or len(images) != 3:
        raise ComparisonSpecError("El manifest debe contener exactamente tres imagenes")
    package = path.parent.resolve()
    seen: set[str] = set()
    for image in images:
        if not isinstance(image, dict) or not isinstance(image.get("file"), str):
            raise ComparisonSpecError("Entrada de imagen invalida")
        name = image["file"]
        if name not in expected or name in seen or Path(name).name != name:
            raise ComparisonSpecError("Ruta o identidad de imagen no admitida")
        image_path = (package / name).resolve()
        if image_path.parent != package or not image_path.is_file():
            raise ComparisonSpecError("Imagen de evidencia ausente o fuera del paquete")
        digest, item_id, item_level = expected[name]
        image_keys = {
            "eternal_voidsong_chain_tooltip.png": {"file", "sha256", "subject", "item_id", "item_level", "visible_stats", "visible_socket", "visible_effect"},
            "barbed_ymirheim_choker_tooltip.png": {"file", "sha256", "subject", "item_id", "item_level", "visible_stats", "visible_socketed_gem"},
            "flawless_quick_garnet_socket.png": {"file", "sha256", "subject", "gem_profile_id", "visible_gem_stats"},
        }[name]
        _exact_keys(image, image_keys, f"evidence image {name}")
        if sha256(image_path.read_bytes()).hexdigest() != digest or image.get("sha256") != digest:
            raise ComparisonSpecError("Hash individual de evidencia incorrecto")
        if item_id is not None and (image.get("item_id"), image.get("item_level")) != (item_id, item_level):
            raise ComparisonSpecError("Item de evidencia incorrecto")
        if name == "flawless_quick_garnet_socket.png" and image.get("gem_profile_id") != 240906:
            raise ComparisonSpecError("Identidad de gema incorrecta")
        seen.add(name)
    correlation = document["profile_correlation"]
    if correlation != {"equipped_item_id": 50228, "declared_gem_id": 240906, "gem_identity": "Flawless Quick Garnet"}:
        raise ComparisonSpecError("Identidad de gema no admitida")
    expected_conclusion = "Eternal Voidsong Chain muestra un Prismatic Socket y la interfaz permite insertar la misma Flawless Quick Garnet declarada como gem_id=240906 en el perfil."
    if document["compatibility_conclusion"] != expected_conclusion:
        raise ComparisonSpecError("Conclusion de compatibilidad no admitida")


def _arm(key: str, table: dict[str, Any]) -> ComparisonArm:
    _closed(table, {"label", "item_id", "item_level", "source", "slot", "declared_bonus_ids", "declared_gem_id", "expected_profile_line"}, f"arms.{key}")
    bonus = table.get("declared_bonus_ids")
    if not isinstance(bonus, list) or not bonus or any(isinstance(x, bool) or not isinstance(x, int) for x in bonus):
        raise ComparisonSpecError(f"arms.{key}.declared_bonus_ids no es valido")
    arm = ComparisonArm(key, _text(table, "label"), _integer(table, "item_id"), _integer(table, "item_level"), _text(table, "source"), _text(table, "slot"), tuple(bonus), _integer(table, "declared_gem_id"), _text(table, "expected_profile_line"))
    if arm.slot != "neck" or arm.item_level != 276:
        raise ComparisonSpecError(f"arms.{key} debe ser neck ilvl 276")
    if not re.fullmatch(r"neck=,id=\d+,gem_id=\d+,bonus_id=\d+(?:/\d+)*", arm.expected_profile_line):
        raise ComparisonSpecError(f"arms.{key}.expected_profile_line no es canonica")
    return arm


def _derived_seed(identifier: str, index: int) -> int:
    data = f"{identifier}|block={index}|seed-v1".encode()
    value = int.from_bytes(sha256(data).digest()[:4], "big") & 0x7FFFFFFF
    return value or 1


def load_comparison_spec(path: Path, *, root: Path) -> ComparisonSpec:
    data = path.read_bytes()
    try:
        doc = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ComparisonSpecError(f"Spec TOML invalido: {exc}") from exc
    _exact_keys(doc, ROOT_KEYS, "root")
    if doc.get("schema_version") != "0.1" or doc.get("status") != "frozen" or doc.get("comparison_id") != EXPECTED_COMPARISON_ID:
        raise ComparisonSpecError("Se requiere comparison_spec 0.1 congelado")
    scope, inputs, arms = _table(doc, "scope"), _table(doc, "inputs"), _table(doc, "arms")
    normalization, precision = _table(doc, "normalization"), _table(doc, "precision")
    protocol, seeds, analysis = _table(doc, "protocol"), _table(doc, "seeds"), _table(doc, "analysis")
    software = _table(doc, "software_requirements")
    _closed(scope, {"comparison_type", "slot", "character", "allowed_changed_slots", "baseline_role", "matrix_generation", "optimization"}, "scope")
    _closed(inputs, {"base_profile", "scenario"}, "inputs")
    _closed(arms, {"a", "b"}, "arms")
    _closed(normalization, {"policy", "status", "target_gem_id", "socket_type", "enchant", "copy_bonus_ids", "invent_sockets", "fallback_to_as_equipped", "evidence"}, "normalization")
    _closed(precision, {"precision_source", "precision_mode", "iterations_per_run"}, "precision")
    _closed(protocol, {"blocks", "threads", "within_pair_pause_seconds", "between_block_pause_seconds", "timeout_seconds", "max_pair_attempts", "retry_full_pair", "require_all_blocks_valid", "exclude_dps_outliers", "early_stopping"}, "protocol")
    _closed(seeds, {"seed_derivation", "derivation_identifier", "values", "orders"}, "seeds")
    _closed(analysis, {"primary_method", "sensitivity_method", "quantile_provider", "confidence_level", "epsilon_percent", "stochastic_analysis", "bootstrap", "monte_carlo"}, "analysis")
    _closed(software, {"python_minimum", "scipy", "simulationcraft_version", "simulationcraft_revision"}, "software_requirements")
    base, scenario = _table(inputs, "base_profile"), _table(inputs, "scenario")
    evidence = _table(normalization, "evidence")
    _closed(base, {"path", "sha256"}, "inputs.base_profile")
    _closed(scenario, {"path", "sha256", "scenario_id"}, "inputs.scenario")
    _closed(evidence, {"type", "reference", "sha256"}, "normalization.evidence")
    if scope != {"comparison_type": "equipment_ab", "slot": "neck", "character": "Flasil", "allowed_changed_slots": ["neck"], "baseline_role": "historical_reference_only", "matrix_generation": False, "optimization": False}:
        raise ComparisonSpecError("scope 0.1 no coincide con el contrato cerrado")
    if normalization.get("status") != "approved" or normalization.get("policy") != "normalized" or normalization.get("target_gem_id") != 240906:
        raise ComparisonSpecError("La normalizacion no esta aprobada")
    if evidence.get("type") != "wow_tooltip_bundle_v1":
        raise ComparisonSpecError("Tipo de evidencia no admitido")
    if precision != {"precision_source": "comparison_spec", "precision_mode": "fixed_iterations", "iterations_per_run": 5000}:
        raise ComparisonSpecError("La precision debe ser 5000 iteraciones fijas")
    values, orders = seeds.get("values"), seeds.get("orders")
    if not isinstance(values, list) or not isinstance(orders, list):
        raise ComparisonSpecError("Seeds y ordenes deben ser listas")
    identifier = _text(seeds, "derivation_identifier")
    expected = tuple(_derived_seed(identifier, i) for i in range(1, 9))
    if seeds.get("seed_derivation") != "sha256_first_u32_masked_31bit_v1" or identifier != EXPECTED_COMPARISON_ID or tuple(values) != expected or tuple(values) != EXPECTED_SEEDS or tuple(orders) != ("AB", "BA") * 4 or len(set(values)) != 8:
        raise ComparisonSpecError("Seeds u ordenes no coinciden con el contrato")
    booleans = {"retry_full_pair": True, "require_all_blocks_valid": True, "exclude_dps_outliers": False, "early_stopping": False}
    if any(protocol.get(k) is not v for k, v in booleans.items()):
        raise ComparisonSpecError("Politica operativa no coincide con el contrato")
    expected_protocol = {"blocks": 8, "threads": 2, "within_pair_pause_seconds": 30, "between_block_pause_seconds": 60, "timeout_seconds": 900, "max_pair_attempts": 2}
    if any(isinstance(protocol.get(k), bool) or protocol.get(k) != value for k, value in expected_protocol.items()):
        raise ComparisonSpecError("Parametros operativos congelados incorrectos")
    if (analysis.get("primary_method"), analysis.get("sensitivity_method"), analysis.get("quantile_provider"), analysis.get("confidence_level"), analysis.get("epsilon_percent")) != ("welch_delta_ratio_percent_v1", "paired_ratio_percent_t_v1", "scipy.stats.t.ppf", 0.95, 0.5) or any(analysis.get(k) is not False for k in ("stochastic_analysis", "bootstrap", "monte_carlo")):
        raise ComparisonSpecError("Analisis 0.1 debe ser analitico con SciPy")
    if software != {"python_minimum": "3.11", "scipy": ">=1.11.0,<2.0.0", "simulationcraft_version": "1205-01", "simulationcraft_revision": "a81c39d"}:
        raise ComparisonSpecError("Requisitos de software congelados incorrectos")
    root = root.resolve()
    base_path, scenario_path = root / _text(base, "path"), root / _text(scenario, "path")
    evidence_path = root / _text(evidence, "reference")
    for source, digest, label in ((base_path, _text(base, "sha256"), "perfil"), (scenario_path, _text(scenario, "sha256"), "escenario"), (evidence_path, _text(evidence, "sha256"), "evidencia")):
        if not source.is_file() or sha256(source.read_bytes()).hexdigest() != digest:
            raise ComparisonSpecError(f"Hash incorrecto para {label}")
    if (_text(base, "path"), _text(base, "sha256")) != ("profiles/flasil.simc", EXPECTED_PROFILE_SHA256) or (_text(scenario, "path"), _text(scenario, "sha256"), _text(scenario, "scenario_id")) != ("scenarios/st_lightmovement_300s_v1.toml", EXPECTED_SCENARIO_SHA256, "st_lightmovement_300s_v1") or (_text(evidence, "reference"), _text(evidence, "sha256")) != ("comparisons/evidence/flasil_neck_50228_vs_249368_v1/evidence_manifest.json", EXPECTED_EVIDENCE_SHA256):
        raise ComparisonSpecError("Entradas congeladas incorrectas")
    _validate_evidence(evidence_path, root)
    arm_a, arm_b = _arm("a", _table(arms, "a")), _arm("b", _table(arms, "b"))
    if any((arm.item_id, arm.item_level, arm.source, arm.bonus_ids, arm.gem_id, arm.expected_profile_line) != EXPECTED_ARMS[key] for key, arm in (("a", arm_a), ("b", arm_b))):
        raise ComparisonSpecError("Identidad de brazos no admitida")
    return ComparisonSpec(path.resolve(), sha256(data).hexdigest(), _text(doc, "comparison_id"), "frozen", base_path.resolve(), _text(base, "sha256"), scenario_path.resolve(), _text(scenario, "sha256"), arm_a, arm_b, evidence_path.resolve(), _text(evidence, "sha256"), ComparisonProtocol(_integer(protocol, "blocks"), 5000, _integer(protocol, "threads"), float(protocol["within_pair_pause_seconds"]), float(protocol["between_block_pause_seconds"]), float(protocol["timeout_seconds"]), _integer(protocol, "max_pair_attempts"), tuple(values), tuple(orders)), ComparisonAnalysis(float(analysis["confidence_level"]), float(analysis["epsilon_percent"]), _text(analysis, "primary_method"), _text(analysis, "sensitivity_method")), _text(software, "simulationcraft_version"), _text(software, "simulationcraft_revision"))
