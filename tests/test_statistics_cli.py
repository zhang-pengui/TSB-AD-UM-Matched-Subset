import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_statistics import stats, fixtures

ROOT = Path(__file__).resolve().parents[1]

class StatisticsExitCodeTests(unittest.TestCase):
    def test_reference_mismatch_does_not_exit_success(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as d:
            d = Path(d)
            pairs, results = fixtures()
            pairs.to_csv(d / "pairs.csv", index=False)
            results.to_csv(d / "metrics.csv", index=False)
            row = dict(contrast="JLC-C", metric="VUS_PR", mean_H=0.2, median_H=0.2,
                       bootstrap_ci95_low=-0.1, bootstrap_ci95_high=0.5,
                       bootstrap_probability_mean_gt_zero=0.7,
                       positive_parents=2, negative_parents=1, zero_parents=0)
            (d / "reference.json").write_text(json.dumps({"results":[dict(row, mean_H=42.)]}))
            with patch.object(stats, "hierarchical_bootstrap", return_value={"results":[row]}), contextlib.redirect_stdout(io.StringIO()):
                code = stats.main(["--pairs",str(d/"pairs.csv"),"--results",str(d/"metrics.csv"),
                                   "--reference",str(d/"reference.json"),"--output-dir",str(d/"output")])
            self.assertEqual(code, 1)
            report = json.loads((d / "output/statistics_reference.json").read_text())
            self.assertEqual(report["historical_comparison"]["status"], "FAIL")

if __name__ == "__main__": unittest.main()
