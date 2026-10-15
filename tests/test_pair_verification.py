from test_discovery import MatchingFixture
from matching_core import check_pair

class VerificationCases(MatchingFixture):
    def pair(self):
        self.u(); self.m()
        return self.run_discovery()[0][0]
    def test_missing_file(self):
        r = self.pair(); r["u_relative_path"] = "001_Test_id_99_Sensor_tr_2_1st_3.csv"
        self.assertIn("FileNotFoundError", check_pair(r, self.ur, self.mr))
    def test_hash_change(self):
        r = self.pair()
        with (self.ur / r["u_relative_path"]).open("a") as f: f.write("\n")
        self.assertIn("U_FILE_SHA256_MISMATCH", check_pair(r, self.ur, self.mr))
    def test_wrong_channel(self):
        r = self.pair(); r["m_channel_index"] = 1
        errors = check_pair(r, self.ur, self.mr)
        self.assertIn("SIGNAL_MISMATCH", errors)
        self.assertIn("CHANNEL_NAME_MISMATCH", errors)
    def test_tampered_manifest_boundary(self):
        r = self.pair(); r["train_prefix_boundary"] = 3
        self.assertIn("BOUNDARY_MISMATCH", check_pair(r, self.ur, self.mr))

if __name__ == "__main__":
    import unittest
    unittest.main()
