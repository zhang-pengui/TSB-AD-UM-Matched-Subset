from test_discovery import MatchingFixture

class DuplicateCases(MatchingFixture):
    def test_duplicate_u_files(self):
        self.u(); self.u(ident=2); self.m()
        c, _ = self.run_discovery()
        self.assertEqual(len(c), 2)
        self.assertTrue(all(r["status"] == "AMBIGUOUS" for r in c))
        self.assertTrue(all("MULTIPLE_U_FILES" in r["ambiguity"] for r in c))
    def test_multiple_parent_ambiguity(self):
        self.u(); self.m(); self.m(ident=2)
        c, _ = self.run_discovery()
        self.assertEqual(len(c), 2)
        self.assertTrue(all("MULTIPLE_M_PARENTS" in r["ambiguity"] for r in c))
    def test_duplicate_channel_ambiguity(self):
        self.u(); self.m(duplicate_channel=True)
        c, _ = self.run_discovery()
        self.assertEqual(len(c), 2)
        self.assertTrue(all("MULTIPLE_CHANNELS_IN_PARENT" in r["ambiguity"] for r in c))

if __name__ == "__main__":
    import unittest
    unittest.main()
