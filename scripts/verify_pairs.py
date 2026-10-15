"""Re-read pair content, checksums and metadata. Exit 1 on any failed row."""
import argparse
import json
from collections import Counter
from pathlib import Path
from matching_core import *

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ["u-root", "m-root", "pairs", "output"]:
        p.add_argument("--" + n, required=True, type=Path)
    a = p.parse_args()
    if any(a.output.resolve().is_relative_to(r.resolve()) for r in [a.u_root, a.m_root]):
        p.error("Output must not be under data roots")
    rows = read_csv(a.pairs)
    identities = Counter((r["u_relative_path"], r["m_relative_path"], r["m_channel_index"]) for r in rows)
    uc = Counter(r["u_relative_path"] for r in rows)
    mc = Counter((r["m_relative_path"], r["m_channel_index"]) for r in rows)
    result = []
    for r in rows:
        errors = check_pair(r, a.u_root, a.m_root)
        if r.get("status") != "STRICT_UNAMBIGUOUS" or r.get("ambiguity", ""):
            errors.append("UNRESOLVED_AMBIGUITY_OR_NONSTRICT_STATUS")
        if uc[r["u_relative_path"]] > 1 or mc[(r["m_relative_path"], r["m_channel_index"])] > 1:
            errors.append("DUPLICATE_OR_AMBIGUOUS_PAIR_LIST")
        result.append(dict(pair_id=r["pair_id"], passed=not errors, errors=errors))
    summary = dict(pair_count=len(rows), passed=sum(r["passed"] for r in result), failed=sum(not r["passed"] for r in result),
                   status="PASS" if rows and all(r["passed"] for r in result) else "FAIL",
                   pair_manifest_sha256=sha256(a.pairs), scope="listed pairs only; uniqueness against full universe belongs to sealed discovery", rows=result)
    write_json(a.output, summary)
    print(json.dumps({k:v for k,v in summary.items() if k != "rows"}))
    return 0 if summary["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
