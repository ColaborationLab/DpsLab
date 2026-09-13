"""Strict decoder for the player-requested live-analysis SavedVariables bridge."""

from __future__ import annotations

import re

from .addon_live_analysis_transport import MAX_BYTES, LiveAnalysisSnapshot, parse_live_analysis_export

_ASSIGNMENT = re.compile(
    rb'^DpsLabObservationExport = "live_analysis:([0-9a-f]+)"\r?$', re.MULTILINE
)


class LiveAnalysisSavedVariableError(ValueError):
    pass


def decode_live_analysis_saved_variable(raw: bytes) -> tuple[str, LiveAnalysisSnapshot]:
    if not isinstance(raw, bytes):
        raise LiveAnalysisSavedVariableError("live_analysis_saved_variable_invalid")
    matches = _ASSIGNMENT.findall(raw)
    if len(matches) != 1 or len(matches[0]) > MAX_BYTES * 2:
        raise LiveAnalysisSavedVariableError("live_analysis_saved_variable_invalid")
    try:
        text = bytes.fromhex(matches[0].decode("ascii")).decode("utf-8")
        return text, parse_live_analysis_export(text)
    except (UnicodeDecodeError, ValueError) as exc:
        raise LiveAnalysisSavedVariableError("live_analysis_saved_variable_invalid") from exc


def parse_live_analysis_saved_variable(raw: bytes) -> LiveAnalysisSnapshot:
    return decode_live_analysis_saved_variable(raw)[1]
