"""Verify the complete pinned candidate universe before independent discovery."""
import argparse
import csv
import json
from pathlib import Path
from matching_core import *

def verify(root, manifest, track):
    rows = read_csv(manifest)
    result = []
    for r in rows:
        errors = []
        review = []
        try:
            p = safe_file(root, r["relative_file_path"])
            if sha256(p) != r["file_sha256"]: errors.append("FILE_SHA256_MISMATCH")
            if p.stat().st_size != int(r["file_size"]): errors.append("FILE_SIZE_MISMATCH")
            with p.open(encoding="utf-8-sig", newline="") as f:
                header = next(csv.reader(f))
            if len(set(header)) != len(header): errors.append("DUPLICATE_COLUMN_NAMES")
            if header != json.loads(r["signal_columns"]) + [r["label_column"]]: errors.append("HEADER_MISMATCH")
            if int(r["filename_first_anomaly"]) != int(r["observed_first_anomaly"]):
                review.append("FILENAME_FIRST_ANOMALY_INCONSISTENT_WITH_LABELS")
        except (ValueError, KeyError, OSError, StopIteration) as e:
            errors.append(type(e).__name__)
        result.append(dict(track=track, relative_file_path=r["relative_file_path"],
                           passed=not errors, errors=errors, metadata_review=review))
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["u-root", "m-root", "u-manifest", "m-manifest", "output"]:
        p.add_argument("--"+name, required=True, type=Path)
    a = p.parse_args()
    if any(a.output.resolve().is_relative_to(x.resolve()) for x in [a.u_root, a.m_root]):
        p.error("Output must be outside data roots")
    rows = verify(a.u_root, a.u_manifest, "U") + verify(a.m_root, a.m_manifest, "M")
    report = dict(status="PASS" if rows and all(x["passed"] for x in rows) else "FAIL", checked=len(rows),
                  failed=sum(not x["passed"] for x in rows),
                  metadata_review_required=sum(bool(x["metadata_review"]) for x in rows),
                  metadata_policy="Inconsistent filename annotation must not qualify as a strict pair; data is not repaired", rows=rows)
    write_json(a.output, report)
    print(json.dumps({k:v for k,v in report.items() if k != "rows"}))
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__": raise SystemExit(main())
