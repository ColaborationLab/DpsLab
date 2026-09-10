"""Strict decoder for the player-requested live-analysis SavedVariables bridge."""

from __future__ import annotations

import re

from .addon_live_analysis_transport import MAX_BYTES, LiveAnalysisSnapshot, parse_live_analysis_export

_ASSIGNMENT = re.compile(
    rb'\A(?:\r?\n)?DpsLabObservationExport = "live_analysis:([0-9a-f]+)"\r?\n\Z'
)


class LiveAnalysisSavedVariableError(ValueError):
    pass


def decode_live_analysis_saved_variable(raw: bytes) -> tuple[str, LiveAnalysisSnapshot]:
    if not isinstance(raw, bytes):
        raise LiveAnalysisSavedVariableError("live_analysis_saved_variable_invalid")
    match = _ASSIGNMENT.fullmatch(raw)
    if match is None or len(match.group(1)) > MAX_BYTES * 2:
        raise LiveAnalysisSavedVariableError("live_analysis_saved_variable_invalid")
    try:
        text = bytes.fromhex(match.group(1).decode("ascii")).decode("utf-8")
        return text, parse_live_analysis_export(text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise LiveAnalysisSavedVariableError("live_analysis_saved_variable_invalid") from exc


def parse_live_analysis_saved_variable(raw: bytes) -> LiveAnalysisSnapshot:
    return decode_live_analysis_saved_variable(raw)[1]
