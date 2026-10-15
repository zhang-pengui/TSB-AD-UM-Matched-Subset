import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_release import scan

class ReleaseTests(unittest.TestCase):
    def test_gitignore_does_not_hide_secrets(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as d:
            p = Path(d)
            (p / ".gitignore").write_text("private.txt\n")
            (p / "private.txt").write_text("token=" + "sk-" + "a" * 30)
            r = scan(p)
            self.assertEqual(r["status"], "NOT_READY")
            self.assertIn("POSSIBLE_API_KEY", [x["kind"] for x in r["content_findings"]])
    def test_raw_signal_not_licensed_by_gitignore(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as d:
            p = Path(d)
            (p / "signal.csv").write_text("Data,Label\n1,0\n")
            self.assertIn("POSSIBLE_RAW_SIGNAL_CSV", [x["kind"] for x in scan(p)["content_findings"]])

if __name__ == "__main__": unittest.main()
