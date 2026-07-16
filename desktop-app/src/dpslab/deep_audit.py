"""Deep, read-only comparison of an HTML report and a completed DpsLab run."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

AVAILABILITY = {"present", "not_exposed", "not_applicable", "parse_failed"}
RELEVANCE = {"potentially_material", "likely_irrelevant", "unknown"}


@dataclass(frozen=True, slots=True)
class Comparison:
    field: str
    manual_value: Any
    formal_value: Any
    manual_source: str
    formal_source: str
    manual_locator: str
    formal_locator: str
    comparison_status: str
    manual_availability: str
    formal_availability: str
    relevance: str
    justification: str

    def __post_init__(self) -> None:
        if self.comparison_status not in {"identical", "different", "unavailable"}:
            raise ValueError("comparison_status inválido")
        if self.manual_availability not in AVAILABILITY or self.formal_availability not in AVAILABILITY:
            raise ValueError("availability inválida")
        if self.relevance not in RELEVANCE:
            raise ValueError("relevance inválida")


@dataclass(frozen=True, slots=True)
class JsonCandidate:
    offset: int
    raw: str
    value: Any | None
    error: str | None


@dataclass(frozen=True, slots=True)
class AplExtraction:
    completeness: str
    source: str
    lists: dict[str, list[str]]
    action_count: int
    order: list[str]
    duplicates: list[str]
    precombat: list[str]
    normalized_sha256: str | None


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _balanced_object(text: str, start: int) -> str | None:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def extract_json_candidates(text: str) -> list[JsonCandidate]:
    """Extract likely data objects without evaluating JavaScript."""
    starts = {match.start() for match in re.finditer(r"\{\s*\"target\"\s*:", text)}
    starts.update(match.start() for match in re.finditer(r"\{\s*target\s*:", text))
    candidates: list[JsonCandidate] = []
    for start in sorted(starts):
        raw = _balanced_object(text, start)
        if raw is None:
            candidates.append(JsonCandidate(start, text[start : start + 200], None, "unbalanced"))
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            candidates.append(JsonCandidate(start, raw, None, str(exc)))
        else:
            candidates.append(JsonCandidate(start, raw, value, None))
    return candidates


def extract_embedded_profile(text: str, character: str = "Flasil") -> list[str]:
    pattern = rf"<p>\s*warlock=&quot;{re.escape(character)}&quot;|<p>\s*warlock=\"{re.escape(character)}\""
    match = re.search(pattern, text, re.IGNORECASE)
    if match is None:
        return []
    end = text.find("</p>", match.start())
    if end < 0:
        return []
    block = text[match.start() + 3 : end]
    block = re.sub(r"<br\s*/?>", "\n", block, flags=re.IGNORECASE)
    block = re.sub(r"<[^>]+>", "", block)
    return html.unescape(block).replace("\r\n", "\n").replace("\r", "\n").split("\n")


def classify_profile_lines(lines: Sequence[str]) -> dict[str, Any]:
    active: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    blanks: list[int] = []
    keys: dict[str, list[int]] = {}
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            blanks.append(number)
        elif stripped.startswith("#"):
            comments.append({"line": number, "text": line})
        elif "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            active.append({"line": number, "text": line, "key": key, "value": value})
            keys.setdefault(key, []).append(number)
        else:
            active.append({"line": number, "text": line, "key": None, "value": None})
    return {
        "active_assignments": active,
        "comments": comments,
        "blank_lines": blanks,
        "duplicate_keys": {key: values for key, values in keys.items() if len(values) > 1},
    }


def compare_profiles(manual_lines: Sequence[str], formal_lines: Sequence[str]) -> dict[str, Any]:
    manual = classify_profile_lines(manual_lines)
    formal = classify_profile_lines(formal_lines)
    manual_active = [item["text"] for item in manual["active_assignments"]]
    formal_active = [item["text"] for item in formal["active_assignments"]]
    manual_counts: dict[str, int] = {}
    formal_counts: dict[str, int] = {}
    for line in manual_active:
        manual_counts[line] = manual_counts.get(line, 0) + 1
    for line in formal_active:
        formal_counts[line] = formal_counts.get(line, 0) + 1
    manual_only = [line for line, count in manual_counts.items() for _ in range(max(0, count - formal_counts.get(line, 0)))]
    formal_only = [line for line, count in formal_counts.items() for _ in range(max(0, count - manual_counts.get(line, 0)))]
    by_key_manual = {item["key"]: item["value"] for item in manual["active_assignments"] if item["key"]}
    by_key_formal = {item["key"]: item["value"] for item in formal["active_assignments"] if item["key"]}
    differing = [
        {"field": f"profile.assignment.{key}", "key": key,
         "manual_value": by_key_manual[key], "formal_value": by_key_formal[key],
         "manual_source": "flasil.simc.html", "formal_source": "profiles/flasil.simc",
         "manual_locator": f"manual_report_embedded_profile/{key}",
         "formal_locator": f"active_assignment/{key}", "comparison_status": "different",
         "manual_availability": "present", "formal_availability": "present",
         "relevance": "unknown",
         "justification": "El perfil del HTML es reconstruido por SimC; una diferencia textual no demuestra una diferencia efectiva."}
        for key in sorted(by_key_manual.keys() & by_key_formal.keys())
        if by_key_manual[key] != by_key_formal[key]
    ]
    return {
        "audit_schema_version": "0.1",
        "manual_profile_role": "manual_report_embedded_profile",
        "active_assignments": {"manual": manual["active_assignments"], "formal": formal["active_assignments"]},
        "comments": {"manual": manual["comments"], "formal": formal["comments"]},
        "blank_lines": {"manual": manual["blank_lines"], "formal": formal["blank_lines"]},
        "duplicate_keys": {"manual": manual["duplicate_keys"], "formal": formal["duplicate_keys"]},
        "manual_only_lines": manual_only,
        "formal_only_lines": formal_only,
        "differing_assignments": differing,
        "exact_active_sequence_equal": manual_active == formal_active,
    }


def extract_apl(lines: Sequence[str], source: str, *, completeness: str) -> AplExtraction:
    lists: dict[str, list[str]] = {}
    order: list[str] = []
    for line in lines:
        stripped = line.strip()
        match = re.match(r"actions(?:\.([A-Za-z0-9_]+))?(\+?=)(.*)$", stripped)
        if match is None:
            continue
        name = match.group(1) or "default"
        action = match.group(3).strip()
        lists.setdefault(name, []).append(action)
        order.append(f"{name}:{action}")
    duplicates = sorted({item for item in order if order.count(item) > 1})
    normalized = "\n".join(item.strip() for item in order).encode("utf-8")
    digest = hashlib.sha256(normalized).hexdigest() if completeness == "complete" else None
    return AplExtraction(completeness, source, lists, len(order), order, duplicates, lists.get("precombat", []), digest)


def canonical_damage_key(entry: dict[str, Any]) -> tuple[str | None, str]:
    ids = (entry.get("owner_id"), entry.get("pet_id"), entry.get("action_id"))
    if all(value is not None for value in ids):
        return "/".join(str(value) for value in ids), "high"
    names = (entry.get("owner_name"), entry.get("pet_name"), entry.get("action_name"))
    if all(value for value in names):
        return "/".join(re.sub(r"\W+", "_", str(value).lower()).strip("_") for value in names), "fallback"
    return None, "unmappable"


def _comparison(field: str, manual: Any, formal: Any, *, manual_source: str, formal_source: str,
                manual_locator: str, formal_locator: str, relevance: str = "unknown",
                manual_availability: str = "present", formal_availability: str = "present",
                justification: str = "Comparación directa de valores expuestos.") -> Comparison:
    available = manual_availability == formal_availability == "present"
    status = "identical" if available and manual == formal else "different" if available else "unavailable"
    return Comparison(field, manual, formal, manual_source, formal_source, manual_locator,
                      formal_locator, status, manual_availability, formal_availability,
                      relevance, justification)


def _atomic_json(path: Path, value: Any) -> None:
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary:
            Path(temporary).unlink(missing_ok=True)


def _atomic_text(path: Path, value: str) -> None:
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary:
            Path(temporary).unlink(missing_ok=True)


def run_audit(manual_html: Path, profile: Path, run: Path, output: Path) -> dict[str, Any]:
    inputs = [manual_html, profile, run / "metadata.json", run / "simc.json", run / "stdout.txt",
              run / "stderr.txt", run / "run_summary.json"]
    root = profile.resolve().parents[1]
    scenario = root / "scenarios" / "st_lightmovement_300s_v1.toml"
    variant = root / "variants" / "flasil_soul_shards_0_v1.toml"
    inputs.extend(path for path in (scenario, variant) if path.exists())
    before = {path.resolve().as_posix(): sha256_file(path) for path in inputs}
    html_text = manual_html.read_text(encoding="utf-8", errors="strict")
    candidates = extract_json_candidates(html_text)
    valid = [candidate for candidate in candidates if candidate.error is None]
    failed = [candidate for candidate in candidates if candidate.error is not None]
    embedded_lines = extract_embedded_profile(html_text)
    formal_lines = profile.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    profile_diff = compare_profiles(embedded_lines, formal_lines)
    simc = json.loads((run / "simc.json").read_text(encoding="utf-8"))
    metadata = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
    summary = json.loads((run / "run_summary.json").read_text(encoding="utf-8"))
    stdout = (run / "stdout.txt").read_text(encoding="utf-8")
    options = simc.get("sim", {}).get("options", {})
    tables = {html.unescape(label).strip(): html.unescape(re.sub("<[^>]+>", "", value)).strip()
              for label, value in re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", html_text, re.I | re.S)}
    def table_number(label: str, *, scale: float = 1.0) -> float | int | None:
        match = re.search(r"[0-9]+(?:\.[0-9]+)?", tables.get(label, ""))
        if match is None:
            return None
        value = float(match.group()) * scale
        return int(value) if value.is_integer() else value
    fight_style_match = re.search(r"<b>Fight Style:</b>\s*([^<]+)", html_text, re.I)
    max_time_match = re.search(r"Fight Length:\s*([0-9.]+)<br\s*/?>", html_text, re.I)
    vary_match = re.search(r"Vary Combat Length:\s*([0-9.]+)", html_text, re.I)
    option_manual = {
        "iterations": table_number("Iterations:"), "threads": table_number("Threads:"),
        "world_lag": table_number("World Lag:", scale=0.001),
        "queue_lag": table_number("Queue Lag:", scale=0.001),
        "fight_style": html.unescape(fight_style_match.group(1)).strip() if fight_style_match else None,
        "max_time": float(max_time_match.group(1)) if max_time_match else None,
        "vary_combat_length": float(vary_match.group(1)) if vary_match else None,
    }
    runtime_keys = {"threads"}
    derived_keys = {"expected_iteration_time"}
    option_groups: dict[str, list[dict[str, Any]]] = {"input_configuration": [], "runtime_configuration": [], "derived_results": []}
    comparisons: list[Comparison] = []
    comparisons.append(_comparison("profile.active_assignment_sequence",
        [item["text"] for item in profile_diff["active_assignments"]["manual"]],
        [item["text"] for item in profile_diff["active_assignments"]["formal"]],
        manual_source="flasil.simc.html", formal_source="profiles/flasil.simc",
        manual_locator="manual_report_embedded_profile/active_assignments",
        formal_locator="active_assignments", relevance="unknown",
        justification="Se compara el perfil reconstruido por el informe, no se presume que sea la entrada manual original."))
    for key, formal_value in sorted(options.items()):
        group = "runtime_configuration" if key in runtime_keys else "derived_results" if key in derived_keys else "input_configuration"
        manual_value = option_manual.get(key)
        availability = "present" if manual_value is not None else "not_exposed"
        relevance = "likely_irrelevant" if key in {"threads", "seed", "expected_iteration_time"} else "unknown"
        item = _comparison(f"sim.options.{key}", manual_value, formal_value,
            manual_source="flasil.simc.html", formal_source="simc.json",
            manual_locator=f"HTML table/{key}", formal_locator=f"/sim/options/{key}",
            relevance=relevance, manual_availability=availability,
            justification="La ausencia en el HTML se marca unavailable; no se infiere un valor predeterminado.")
        option_groups[group].append(asdict(item)); comparisons.append(item)
    raid_events = simc.get("sim", {}).get("raid_events", [])
    comparisons.append(_comparison("raid_events.expanded_configuration", None, raid_events,
        manual_source="flasil.simc.html", formal_source="simc.json",
        manual_locator="visible/Fight Style=LightMovement", formal_locator="/sim/raid_events",
        manual_availability="not_exposed", relevance="unknown",
        justification="El HTML expone LightMovement, pero no su configuración expandida; no se infiere desde el nombre."))
    manual_apl = extract_apl(embedded_lines, "manual_report_embedded_profile", completeness="complete" if embedded_lines else "unavailable")
    formal_apl = extract_apl(stdout.splitlines(), "stdout.txt", completeness="partial")
    apl_status = "identical" if manual_apl.completeness == formal_apl.completeness == "complete" and manual_apl.normalized_sha256 == formal_apl.normalized_sha256 else "unavailable"
    comparisons.append(Comparison("apl.effective", asdict(manual_apl), asdict(formal_apl),
        "manual_report_embedded_profile", "stdout.txt", "embedded profile/actions*", "stdout/Core Engine Priority Lists",
        apl_status, "present" if embedded_lines else "not_exposed", "present" if formal_apl.action_count else "not_exposed",
        "unknown", "Los hashes solo se comparan cuando ambas APL son completas."))
    player = simc["sim"]["players"][0]
    damage_formal: list[dict[str, Any]] = []
    for stat in player.get("stats", []):
        if stat.get("portion_amount"):
            damage_formal.append({"owner_name": player.get("name"), "pet_name": player.get("name"), "action_name": stat.get("name"), "action_id": stat.get("id"), "percentage": stat.get("portion_amount", 0) * 100, "source": "/sim/players/0/stats"})
    raw_pets = player.get("stats_pets", [])
    pet_groups = raw_pets.items() if isinstance(raw_pets, dict) else ((pet.get("name"), pet.get("stats", [])) for pet in raw_pets)
    for pet_name, pet_stats in pet_groups:
        for stat in pet_stats:
            if stat.get("portion_amount"):
                damage_formal.append({"owner_name": player.get("name"), "pet_name": pet_name, "pet_id": stat.get("pet_id"), "action_name": stat.get("name"), "action_id": stat.get("id"), "percentage": stat.get("portion_amount", 0) * 100, "source": f"/sim/players/0/stats_pets/{pet_name}"})
    for entry in damage_formal:
        key, confidence = canonical_damage_key(entry); entry.update(canonical_key=key, mapping_confidence=confidence)
    damage_charts = [candidate.value for candidate in valid if isinstance(candidate.value, dict) and candidate.value.get("target") == "actor1dps_sources"]
    soul = {
        "combat_start_resource": {"value": None, "availability": "not_exposed"},
        "combat_end_resource": {"value": None, "availability": "not_exposed"},
        "first_action": {"value": None, "availability": "not_exposed"},
        "first_gain": {"value": None, "availability": "not_exposed"},
        "first_spend": {"value": None, "availability": "not_exposed"},
        "total_gains": {"value": None, "availability": "not_exposed"},
        "total_spends": {"value": None, "availability": "not_exposed"},
        "waste_or_overcap": {"value": None, "availability": "not_exposed"},
    }
    audit = {
        "audit_schema_version": "0.1", "json_candidates": {"total": len(candidates), "valid": len(valid), "parse_failed": len(failed), "failed_offsets": [c.offset for c in failed]},
        "comparisons": [asdict(item) for item in comparisons], "apl": {"manual": asdict(manual_apl), "formal": asdict(formal_apl)},
        "raid_events": {"manual_expanded": None, "formal_expanded": raid_events, "occurrences_compared": False},
        "damage_normalization": {"manual_structured_charts": damage_charts, "formal_entries": damage_formal},
        "soul_shards": soul, "input_hashes_before": before,
        "hypotheses": [
            "La APL formal completa no está expuesta en los artefactos y continúa siendo una prioridad de investigación.",
            "La expansión manual de LightMovement no está expuesta; no puede confirmarse igualdad de raid events.",
            "Las líneas activas adicionales del perfil reconstruido por el informe pueden revelar configuración efectiva no presente en el perfil exportado."
        ],
        "causality_claimed": False,
    }
    options_output = {"audit_schema_version": "0.1", **option_groups}
    output.mkdir(parents=True, exist_ok=True)
    after = {path.resolve().as_posix(): sha256_file(path) for path in inputs}
    audit["input_hashes_after"] = after
    audit["input_hashes_verified"] = before == after
    md = f"""# Auditoría profunda manual frente a línea base\n\nObjetos JSON candidatos: {len(candidates)}; válidos: {len(valid)}; parse_failed: {len(failed)}.\n\n## Perfil\n\nSecuencia activa exacta idéntica: {profile_diff['exact_active_sequence_equal']}. Manual-only: {len(profile_diff['manual_only_lines'])}; formal-only: {len(profile_diff['formal_only_lines'])}; asignaciones distintas: {len(profile_diff['differing_assignments'])}.\n\n## Raid events\n\nEl formal expone {len(raid_events)} evento(s) expandido(s). El HTML solo expone LightMovement, por lo que la comparación expandida es unavailable.\n\n## APL\n\nManual: {manual_apl.completeness}, {manual_apl.action_count} acciones. Formal: {formal_apl.completeness}, {formal_apl.action_count} acciones. La igualdad global no se afirma salvo que ambas sean completas.\n\n## Soul Shards\n\nLos estados inicial/final y primeros movimientos no están expuestos inequívocamente: not_exposed.\n\nNo se ejecutó SimulationCraft ni se atribuyó causalidad.\n"""
    _atomic_json(output / "profile_lines_diff.json", profile_diff)
    _atomic_json(output / "sim_options_diff.json", options_output)
    _atomic_json(output / "audit.json", audit)
    _atomic_text(output / "audit.md", md)
    return audit


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-html", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    run_audit(args.manual_html.resolve(), args.profile.resolve(), args.run.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
