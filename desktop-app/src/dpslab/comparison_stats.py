"""Analytical statistics for comparison schema 0.1."""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass
from typing import Callable, Sequence


CLASSIFICATIONS = frozenset({"winner_a", "winner_b", "equivalent", "inconclusive"})


class ComparisonAnalysisError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class IntervalAnalysis:
    estimate_percent: float
    standard_error: float
    degrees_of_freedom: float
    t_critical: float
    ci_low: float
    ci_high: float
    classification: str
    method: str

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ComparisonAnalysisResult:
    primary: IntervalAnalysis
    paired_sensitivity: IntervalAnalysis
    final_classification: str
    estimate_difference_percent_points: float
    classification_disagreement: bool


def classify(ci_low: float, ci_high: float, epsilon: float = 0.5) -> str:
    if ci_low > epsilon:
        return "winner_b"
    if ci_high < -epsilon:
        return "winner_a"
    if ci_low >= -epsilon and ci_high <= epsilon:
        return "equivalent"
    return "inconclusive"


def analyze_welch(a: Sequence[float], b: Sequence[float], *, probability: float, epsilon_percent: float, quantile: Callable[[float, float], float]) -> IntervalAnalysis:
    mean_a, mean_b = statistics.fmean(a), statistics.fmean(b)
    variance_a, variance_b = statistics.variance(a), statistics.variance(b)
    if not all(math.isfinite(value) for value in (mean_a, mean_b, variance_a, variance_b)):
        raise ComparisonAnalysisError("Medias o varianzas Welch no finitas")
    estimate = 100.0 * (mean_b / mean_a - 1.0)
    derivative_a, derivative_b = -100.0 * mean_b / mean_a**2, 100.0 / mean_a
    component_a = derivative_a**2 * variance_a / 8
    component_b = derivative_b**2 * variance_b / 8
    variance_estimate = component_a + component_b
    denominator = component_a**2 / 7 + component_b**2 / 7
    if variance_estimate <= 0 or denominator <= 0:
        raise ComparisonAnalysisError("Varianza o grados de libertad Welch no calculables")
    se = math.sqrt(variance_estimate); df = variance_estimate**2 / denominator
    critical = float(quantile(probability, df))
    low, high = estimate - critical * se, estimate + critical * se
    if not all(math.isfinite(value) for value in (estimate, se, df, critical, low, high)) or df <= 0:
        raise ComparisonAnalysisError("Welch produjo valores no finitos")
    return IntervalAnalysis(estimate, se, df, critical, low, high, classify(low, high, epsilon_percent), "welch_delta")


def analyze_paired(a: Sequence[float], b: Sequence[float], *, probability: float, epsilon_percent: float, quantile: Callable[[float, float], float]) -> IntervalAnalysis:
    if len(a) != 8 or len(b) != 8:
        raise ComparisonAnalysisError("Se requieren exactamente ocho pares")
    differences = [100.0 * (right / left - 1.0) for left, right in zip(a, b)]
    estimate = statistics.fmean(differences); sd = statistics.stdev(differences); se = sd / math.sqrt(8)
    critical = float(quantile(probability, 7)); low, high = estimate - critical * se, estimate + critical * se
    if not all(math.isfinite(value) for value in (*differences, estimate, sd, se, critical, low, high)):
        raise ComparisonAnalysisError("Sensibilidad produjo valores no finitos")
    return IntervalAnalysis(estimate, se, 7.0, critical, low, high, classify(low, high, epsilon_percent), "paired_t")


def analyze(a: Sequence[float], b: Sequence[float], *, confidence_level: float = 0.95, epsilon_percent: float = 0.5,
            welch: Callable[..., IntervalAnalysis] = analyze_welch,
            paired: Callable[..., IntervalAnalysis] = analyze_paired) -> ComparisonAnalysisResult:
    if isinstance(confidence_level, bool) or not math.isfinite(confidence_level) or not 0.0 < confidence_level < 1.0:
        raise ComparisonAnalysisError("confidence_level debe estar entre cero y uno")
    if isinstance(epsilon_percent, bool) or not math.isfinite(epsilon_percent) or epsilon_percent < 0:
        raise ComparisonAnalysisError("epsilon_percent debe ser finito y no negativo")
    if len(a) != 8 or len(b) != 8:
        raise ComparisonAnalysisError("Se requieren exactamente ocho bloques validos")
    values = [float(x) for x in (*a, *b)]
    if any(not math.isfinite(x) or x <= 0 for x in values):
        raise ComparisonAnalysisError("Todos los DPS deben ser positivos y finitos")
    try:
        from scipy.stats import t
    except ImportError as exc:
        raise ComparisonAnalysisError("SciPy es obligatorio") from exc
    probability = (1.0 + confidence_level) / 2.0
    primary = welch(a, b, probability=probability, epsilon_percent=epsilon_percent, quantile=t.ppf)
    paired_result = paired(a, b, probability=probability, epsilon_percent=epsilon_percent, quantile=t.ppf)
    if primary.method != "welch_delta" or paired_result.method != "paired_t":
        raise ComparisonAnalysisError("Metodo estadistico incorrecto")
    disagreement = primary.classification != paired_result.classification
    return ComparisonAnalysisResult(primary, paired_result, "inconclusive" if disagreement else primary.classification, paired_result.estimate_percent - primary.estimate_percent, disagreement)
