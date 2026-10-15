"""Run package tests without bytecode caches, GPU imports, or external writes."""
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                       cwd=ROOT, capture_output=True, text=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
    log = p.stdout + p.stderr
    (ROOT / "reports").mkdir(parents=True, exist_ok=True)
    (ROOT / "reports/cpu_tests.log").write_text(log, encoding="utf-8")
    report = dict(returncode=p.returncode, status="PASS" if p.returncode == 0 else "FAIL",
                  test_case_count=log.count(" ... ok"), command="python -B -m unittest discover -s tests -v",
                  synthetic_fixture_scope="script tests only; not model experiments", gpu_used=False)
    (ROOT / "reports/cpu_tests.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(p.returncode)
