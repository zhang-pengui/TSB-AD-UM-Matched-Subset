import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from matching_core import *

class MatchingFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / "tests")
        self.root = Path(self.tmp.name)
        self.ur = self.root / "u"
        self.mr = self.root / "m"
        self.ur.mkdir(); self.mr.mkdir()
        self.x = np.array([2., 3., 5., 8., 13.])
        self.y = np.array([0, 0, 0, 1, 1])
    def tearDown(self):
        self.tmp.cleanup()
    def u(self, ident=1, boundary=2, x=None, y=None):
        name = f"001_Test_id_{ident}_Sensor_tr_{boundary}_1st_3.csv"
        pd.DataFrame({"Data":self.x if x is None else x, "Label":self.y if y is None else y}).to_csv(self.ur / name, index=False)
        return name
    def m(self, ident=1, boundary=2, x=None, y=None, duplicate_channel=False):
        name = f"002_Test_id_{ident}_Sensor_tr_{boundary}_1st_3.csv"
        sig = self.x if x is None else x
        pd.DataFrame({"a":sig, "b":sig if duplicate_channel else sig * 2 + 1, "Label":self.y if y is None else y}).to_csv(self.mr / name, index=False)
        return name
    def run_discovery(self):
        u, ue = inventory(self.ur, sorted(p.name for p in self.ur.glob("*.csv")), "U")
        m, me = inventory(self.mr, sorted(p.name for p in self.mr.glob("*.csv")), "M")
        self.assertFalse(ue + me)
        return discover(self.ur, self.mr, u, m)
class MatchingCases(MatchingFixture):
    def test_exact(self):
        self.u(); self.m()
        c, _ = self.run_discovery()
        self.assertEqual([r["status"] for r in c], ["STRICT_UNAMBIGUOUS"])
        self.assertEqual(check_pair(c[0], self.ur, self.mr), [])
    def test_length_mismatch(self):
        self.u(); self.m(x=self.x[:-1], y=self.y[:-1])
        c, unmatched = self.run_discovery()
        self.assertFalse(c); self.assertEqual(len(unmatched), 1)
    def test_label_mismatch(self):
        self.u(); self.m(y=np.zeros(5))
        c, _ = self.run_discovery()
        self.assertEqual(c[0]["status"], "REJECTED")
        self.assertFalse(c[0]["labels_exact"])
    def test_boundary_mismatch(self):
        self.u(); self.m(boundary=3)
        c, _ = self.run_discovery()
        self.assertFalse(c[0]["train_boundary_exact"])
    def test_multiple_views_single_parent(self):
        self.u(); self.u(ident=2, x=self.x * 2 + 1); self.m()
        c, _ = self.run_discovery()
        self.assertEqual(sum(r["status"] == "STRICT_UNAMBIGUOUS" for r in c), 2)
    def test_signed_zero_hash_matches_equality(self):
        self.assertEqual(array_hash(np.array([-0., 1.])), array_hash(np.array([0., 1.])))
    def test_nonfinite_rejected(self):
        name = self.u(x=np.array([np.inf, 3., 5., 8., 13.]))
        _, errors = inventory(self.ur, [name], "U")
        self.assertEqual(len(errors), 1)
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError): safe_file(self.ur, "../data.csv")
    def test_inconsistent_filename_annotation_rejected(self):
        self.u(y=np.array([0, 0, 1, 1, 1])); self.m(y=np.array([0, 0, 1, 1, 1]))
        c, _ = self.run_discovery()
        self.assertEqual(c[0]["status"], "REJECTED")
        self.assertFalse(c[0]["filename_label_annotation_consistent"])
    def test_duplicate_raw_header_rejected(self):
        name = self.m()
        (self.mr / name).write_text("a,a,Label\n1,2,0\n2,3,1\n")
        _, errors = inventory(self.mr, [name], "M")
        self.assertEqual(len(errors), 1)

if __name__ == "__main__": unittest.main()
