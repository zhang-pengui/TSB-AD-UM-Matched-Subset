"""Synthetic CPU tests only; these fixtures are not model experiments."""

import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

MODULE = Path(__file__).parents[1] / "scripts" / "reproduce_statistics.py"
SPEC = importlib.util.spec_from_file_location("matched_statistics", MODULE)
stats = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stats)


def fixtures():
    pairs = pd.DataFrame([
        {"pair_id": "a", "u_relative_path": "u1.csv", "m_relative_path": "m1.csv", "source_family": "A", "domain": "X"},
        {"pair_id": "b", "u_relative_path": "u2.csv", "m_relative_path": "m1.csv", "source_family": "A", "domain": "X"},
        {"pair_id": "c", "u_relative_path": "u3.csv", "m_relative_path": "m2.csv", "source_family": "A", "domain": "X"},
        {"pair_id": "d", "u_relative_path": "u4.csv", "m_relative_path": "m3.csv", "source_family": "B", "domain": "Y"},
    ])
    rows = []
    effects = {"U": {"u1.csv": .2, "u2.csv": .4, "u3.csv": -.1, "u4.csv": .5},
               "M": {"m1.csv": .1, "m2.csv": .2, "m3.csv": -.2}}
    for track, series_values in effects.items():
        for series, effect in series_values.items():
            for seed in stats.SEEDS:
                for index, condition in enumerate(stats.CONDITIONS):
                    value = .3 + index * effect / 3 + (seed - 2000) * .001
                    rows.append({"track": track, "condition": condition, "seed": seed, "series_file": series,
                                 **{metric: value + number * .01 for number, metric in enumerate(stats.METRICS)}})
    normalized = stats.checked_pairs(pairs)
    return normalized, stats.checked_results(pd.DataFrame(rows), normalized)


class StatisticsTest(unittest.TestCase):
    def test_parent_aggregation_does_not_treat_views_as_parents(self):
        pairs, results = fixtures()
        effects = stats.parent_effects(pairs, results)
        averaged = stats.average_seeds(effects)
        primary = averaged[averaged.contrast == "JLC-C"]
        self.assertEqual(len(primary), 3)
        first = primary[primary.m_parent == "m1.csv"].iloc[0]
        self.assertAlmostEqual(first.U_delta_VUS_PR, .3)
        self.assertAlmostEqual(first.M_delta_VUS_PR, .1)
        self.assertAlmostEqual(first.H_VUS_PR, .2)
        self.assertAlmostEqual(primary.H_VUS_PR.mean(), (.2 - .3 + .7) / 3)

    def test_bootstrap_exact_repeatability(self):
        pairs, results = fixtures()
        averaged = stats.average_seeds(stats.parent_effects(pairs, results))
        a = stats.hierarchical_bootstrap(averaged, resamples=31)
        b = stats.hierarchical_bootstrap(averaged, resamples=31)
        self.assertEqual(a, b)

    def test_historical_rng_order_matches_slow_independent_oracle(self):
        pairs, results = fixtures()
        averaged = stats.average_seeds(stats.parent_effects(pairs, results))
        actual = stats.hierarchical_bootstrap(averaged, resamples=23)
        rng = np.random.default_rng(stats.BOOTSTRAP_SEED)
        for record in actual["results"]:
            subset = averaged[averaged.contrast == record["contrast"]]
            source_names = sorted(subset.source.unique())
            draws = []
            for _ in range(23):
                chosen = rng.choice(source_names, len(source_names))
                values = []
                for source in chosen:
                    candidates = subset[subset.source == source]["H_" + record["metric"]].to_numpy(float)
                    values.extend(rng.choice(candidates, len(candidates)))
                draws.append(np.mean(values))
            self.assertEqual(record["bootstrap_ci95_low"], float(np.quantile(draws, .025)))
            self.assertEqual(record["bootstrap_ci95_high"], float(np.quantile(draws, .975)))

    def test_missing_seed_rejected(self):
        pairs, results = fixtures()
        with self.assertRaisesRegex(ValueError, "missing="):
            stats.checked_results(results.iloc[1:], pairs)

    def test_duplicate_metric_rejected(self):
        pairs, results = fixtures()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            stats.checked_results(pd.concat([results, results.iloc[:1]]), pairs)

    def test_nonfinite_metric_rejected(self):
        pairs, results = fixtures()
        results.loc[0, "VUS_PR"] = np.nan
        with self.assertRaisesRegex(ValueError, "NaN"):
            stats.checked_results(results, pairs)

    def test_unexpected_seed_rejected(self):
        pairs, results = fixtures()
        results.loc[results.seed == 2002, "seed"] = 2003
        with self.assertRaisesRegex(ValueError, "Metric keys differ"):
            stats.checked_results(results, pairs)

    def test_duplicate_u_view_rejected(self):
        pairs, _ = fixtures()
        with self.assertRaisesRegex(ValueError, "unique"):
            stats.checked_pairs(pd.concat([pairs, pairs.iloc[:1]]))

    def test_conflicting_parent_source_rejected(self):
        pairs, _ = fixtures()
        pairs.loc[1, "source"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "contradictory"):
            stats.checked_pairs(pairs)

    def test_ambiguous_status_rejected(self):
        pairs, _ = fixtures()
        pairs["status"] = "AMBIGUOUS"
        with self.assertRaisesRegex(ValueError, "Non-strict"):
            stats.checked_pairs(pairs)

    def test_failed_pair_checks_rejected(self):
        pairs, _ = fixtures()
        pairs["checks_pass"] = False
        with self.assertRaisesRegex(ValueError, "failed exact-data"):
            stats.checked_pairs(pairs)

    def test_historical_reference_cannot_change_computation(self):
        pairs, results = fixtures()
        averaged = stats.average_seeds(stats.parent_effects(pairs, results))
        computed = stats.hierarchical_bootstrap(averaged, resamples=17)
        self.assertEqual(stats.compare_historical(computed, computed)["status"], "PASS")
        import copy
        changed = copy.deepcopy(computed)
        changed["results"][0]["mean_H"] += 1
        self.assertEqual(stats.compare_historical(computed, changed)["status"], "FAIL")
        self.assertEqual(computed, stats.hierarchical_bootstrap(averaged, resamples=17))


if __name__ == "__main__":
    unittest.main()
