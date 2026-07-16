from __future__ import annotations

import math
import unittest

from dpslab.comparison_stats import ComparisonAnalysisError, IntervalAnalysis, analyze, analyze_paired, analyze_welch, classify


class ComparisonStatsTests(unittest.TestCase):
    def test_independent_welch_failure_matrix(self) -> None:
        a = [100000.0 + i * 10 for i in range(8)]
        b = [101000.0 + i * 11 for i in range(8)]
        cases = (
            ("exception_before", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("before"))),
            ("nonfinite_quantile", lambda p, df: float("inf")),
        )
        for label, injected in cases:
            with self.subTest(label=label), self.assertRaises(Exception):
                if label == "exception_before": analyze(a, b, welch=injected)
                else: analyze_welch(a, b, probability=.975, epsilon_percent=.5, quantile=injected)
        with self.assertRaises(ComparisonAnalysisError): analyze_welch([1.0] * 8, [2.0] * 8, probability=.975, epsilon_percent=.5, quantile=lambda p, df: 2.0)

    def test_independent_paired_failure_matrix(self) -> None:
        a = [100000.0 + i * 10 for i in range(8)]
        b = [101000.0 + i * 11 for i in range(8)]
        cases = (
            ("exception_before", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("before"))),
            ("nonfinite_quantile", lambda p, df: float("nan")),
        )
        for label, injected in cases:
            with self.subTest(label=label), self.assertRaises(Exception):
                if label == "exception_before": analyze(a, b, paired=injected)
                else: analyze_paired(a, b, probability=.975, epsilon_percent=.5, quantile=injected)
        with self.assertRaises(ComparisonAnalysisError): analyze_paired(a[:7], b[:7], probability=.975, epsilon_percent=.5, quantile=lambda p, df: 2.0)

    def test_wrong_method_from_each_boundary_is_rejected(self) -> None:
        a = [100000.0 + i * 10 for i in range(8)]; b = [101000.0 + i * 11 for i in range(8)]
        wrong = IntervalAnalysis(1, 1, 7, 2, -1, 3, "inconclusive", "wrong")
        with self.assertRaises(ComparisonAnalysisError): analyze(a, b, welch=lambda *args, **kwargs: wrong)
        with self.assertRaises(ComparisonAnalysisError): analyze(a, b, paired=lambda *args, **kwargs: wrong)
    def test_exact_classification_boundaries(self) -> None:
        self.assertEqual(classify(0.50001, 1.0), "winner_b")
        self.assertEqual(classify(-1.0, -0.50001), "winner_a")
        self.assertEqual(classify(-0.5, 0.5), "equivalent")
        self.assertEqual(classify(0.5, 0.7), "inconclusive")
        self.assertEqual(classify(-0.7, -0.5), "inconclusive")

    def test_welch_delta_and_paired_are_analytical(self) -> None:
        a = [100, 101, 99, 102, 98, 100.5, 99.5, 101.5]
        b = [102, 103, 101, 104, 100, 102.5, 101.5, 103.5]
        result = analyze(a, b)
        self.assertTrue(math.isfinite(result.primary.degrees_of_freedom))
        self.assertGreater(result.primary.t_critical, 1.96)
        self.assertEqual(result.final_classification, "winner_b")

    def test_classification_disagreement_forces_inconclusive(self) -> None:
        a = [100, 200, 100, 200, 100, 200, 100, 200]
        b = [101, 201, 101, 201, 101, 201, 101, 201]
        result = analyze(a, b)
        if result.primary.classification != result.paired_sensitivity.classification:
            self.assertEqual(result.final_classification, "inconclusive")

    def test_nonpositive_and_nonfinite_dps_are_rejected(self) -> None:
        for value in (0.0, -1.0, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ComparisonAnalysisError):
                analyze([100.0] * 7 + [value], [101.0] * 8)

    def test_less_than_eight_blocks_is_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonAnalysisError, "ocho"):
            analyze([100.0] * 7, [101.0] * 7)

    def test_both_zero_variances_are_rejected(self) -> None:
        with self.assertRaisesRegex(ComparisonAnalysisError, "Varianza"):
            analyze([100.0] * 8, [101.0] * 8)

    def test_zero_paired_variance_is_valid_when_welch_is_calculable(self) -> None:
        a = [100, 101, 102, 103, 104, 105, 106, 107]
        b = [x * 1.01 for x in a]
        result = analyze(a, b)
        self.assertAlmostEqual(result.paired_sensitivity.standard_error, 0.0, places=12)

    def test_invalid_analysis_parameters_are_rejected(self) -> None:
        for confidence, epsilon in ((0.0, 0.5), (1.0, 0.5), (0.95, -0.1)):
            with self.subTest(confidence=confidence, epsilon=epsilon), self.assertRaises(ComparisonAnalysisError):
                analyze(range(100, 108), range(101, 109), confidence_level=confidence, epsilon_percent=epsilon)

    def test_known_independent_reference_values(self) -> None:
        a = [100, 101, 99, 102, 98, 100.5, 99.5, 101.5]
        b = [102, 103, 101, 104, 100, 102.5, 101.5, 103.5]
        result = analyze(a, b)
        self.assertAlmostEqual(result.primary.estimate_percent, 1.99625701809107, places=12)
        self.assertAlmostEqual(result.primary.degrees_of_freedom, 13.994533871101645, places=12)
        self.assertAlmostEqual(result.paired_sensitivity.estimate_percent, 1.99656800406423, places=12)


if __name__ == "__main__":
    unittest.main()
