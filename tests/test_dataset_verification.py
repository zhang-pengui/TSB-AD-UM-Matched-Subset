from test_discovery import MatchingFixture
from matching_core import inventory, write_csv
from verify_dataset import verify

class DatasetVerificationTests(MatchingFixture):
    def test_all_candidate_hashes_checked(self):
        name = self.u()
        rows, _ = inventory(self.ur, [name], "U")
        manifest = self.root / "manifest.csv"
        write_csv(manifest, rows)
        self.assertTrue(verify(self.ur, manifest, "U")[0]["passed"])
        with (self.ur / name).open("a") as f: f.write("\n")
        self.assertFalse(verify(self.ur, manifest, "U")[0]["passed"])
    def test_missing_file_is_failure(self):
        name = self.u()
        rows, _ = inventory(self.ur, [name], "U")
        rows[0]["relative_file_path"] = "missing.csv"
        manifest = self.root / "manifest.csv"
        write_csv(manifest, rows)
        self.assertFalse(verify(self.ur, manifest, "U")[0]["passed"])

if __name__ == "__main__":
    import unittest
    unittest.main()
