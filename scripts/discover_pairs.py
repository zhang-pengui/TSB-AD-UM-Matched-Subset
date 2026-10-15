"""Independent discovery CLI. Does not accept historical mapping or model metrics."""
import argparse
import platform
import time
from pathlib import Path
import numpy as np
import pandas as pd
from matching_core import *

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--u-root", required=True, type=Path)
    p.add_argument("--m-root", required=True, type=Path)
    p.add_argument("--u-manifest", required=True, type=Path)
    p.add_argument("--m-manifest", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    a = p.parse_args()
    out = a.output_dir.resolve()
    if any(out.is_relative_to(x.resolve()) for x in [a.u_root, a.m_root]):
        p.error("Output must not be under data roots")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "discovery_seal.json").exists():
        p.error("Sealed output already exists; use a new output directory")
    start = time.perf_counter()
    un, mn = manifest_names(a.u_manifest), manifest_names(a.m_manifest)
    u, ue = inventory(a.u_root, un, "U")
    print(f"U inventory {len(u)}/{len(un)} errors={len(ue)}", flush=True)
    m, me = inventory(a.m_root, mn, "M")
    print(f"M inventory {len(m)}/{len(mn)} errors={len(me)}", flush=True)
    write_csv(out / "u_eval_manifest.csv", u)
    write_csv(out / "m_eval_manifest.csv", m)
    write_csv(out / "parser_errors.csv", ue + me, ["track", "relative_file_path", "error_type"])
    review = [dict(track=track, relative_file_path=r["relative_file_path"],
                   filename_first_anomaly=r["filename_first_anomaly"], observed_first_anomaly=r["observed_first_anomaly"],
                   action="QUARANTINED_FROM_STRICT_MATCHING; input not modified")
              for track, metas in [("U", u), ("M", m)] for r in metas
              if r["filename_first_anomaly"] != r["observed_first_anomaly"]]
    write_csv(out / "metadata_review_required.csv", review,
              ["track", "relative_file_path", "filename_first_anomaly", "observed_first_anomaly", "action"])
    c, unmatched = discover(a.u_root, a.m_root, u, m)
    strict = [r for r in c if r["status"] == "STRICT_UNAMBIGUOUS"]
    write_csv(out / "all_discovered_candidate_pairs.csv", c)
    write_csv(out / "pairs_discovered.csv", strict, list(c[0]) if c else None)
    write_csv(out / "unmatched_u.csv", unmatched, ["u_relative_path", "reason"])
    write_csv(out / "duplicate_groups.csv", duplicate_groups(u, "U") + duplicate_groups(m, "M"), ["track", "duplicate_type", "files"])
    parents = []
    for f in sorted({r["m_relative_path"] for r in strict}):
        g = [r for r in strict if r["m_relative_path"] == f]
        parents.append(dict(m_relative_path=f, source_family=g[0]["source_family"], domain=g[0]["domain"], n_u_views=len(g), m_file_sha256=g[0]["m_file_sha256"]))
    write_csv(out / "parents_discovered.csv", parents)
    seal = dict(schema_version=1, parser_version=PARSER_VERSION,
                python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
                u_candidate_count=len(un), m_candidate_count=len(mn), parsed_u=len(u), parsed_m=len(m),
                parser_errors=len(ue)+len(me), signal_hash_candidates=len(c),
                metadata_review_required=len(review),
                strict_pairs=len(strict), unique_u=len({r["u_relative_path"] for r in strict}),
                unique_m_parents=len(parents), source_count=len({r["source_family"] for r in strict}),
                ambiguous_candidate_rows=sum(r["status"] == "AMBIGUOUS" for r in c),
                rejected_candidate_rows=sum(r["status"] == "REJECTED" for r in c),
                model_metrics_read=False, historical_mapping_read=False,
                elapsed_seconds=time.perf_counter()-start,
                inputs=dict(u_manifest_sha256=sha256(a.u_manifest), m_manifest_sha256=sha256(a.m_manifest)),
                script_sha256=sha256(Path(__file__)), core_sha256=sha256(Path(__file__).with_name("matching_core.py")),
                outputs={f.name:sha256(f) for f in sorted(out.glob("*.csv"))})
    write_json(out / "discovery_seal.json", seal)
    print(json.dumps(seal, indent=2), flush=True)
    return 1 if ue or me else 0

if __name__ == "__main__":
    raise SystemExit(main())
