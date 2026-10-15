"""CPU-only, value-exact matching. No training or historical pair input."""
from __future__ import annotations
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

PARSER_VERSION = "tsbad-position-exact-v1;pandas-c-default;float64"
NAME = re.compile(r"^(\d+)_(.+?)_id_(\d+)_(.+?)_tr_(\d+)_1st_(\d+)\.csv$")

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def array_hash(a):
    # Canonical endian/type and signed-zero treatment only; no signal normalization.
    x = np.array(a, dtype="<f8", order="C", copy=True)
    x[x == 0] = 0.0
    h = hashlib.sha256(f"float64-le|{x.shape}|".encode())
    h.update(x.tobytes())
    return h.hexdigest()

def intervals(y):
    z = np.r_[False, np.asarray(y) != 0, False].astype(np.int8)
    return np.column_stack((np.flatnonzero(np.diff(z) == 1),
                            np.flatnonzero(np.diff(z) == -1) - 1)).astype(np.int64)

def safe_file(root, relative):
    r = Path(relative)
    if r.is_absolute() or ".." in r.parts or "\\" in str(relative) or ":" in str(relative):
        raise ValueError("Relative dataset path required")
    result = (Path(root) / r).resolve()
    if not result.is_relative_to(Path(root).resolve()):
        raise ValueError("Dataset path escapes supplied root")
    return result

def read_series(root, relative, track):
    p = safe_file(root, relative)
    m = NAME.match(p.name)
    if not m:
        raise ValueError(f"Unrecognized filename: {p.name}")
    with p.open(encoding="utf-8-sig", newline="") as f:
        header = next(csv.reader(f))
    if len(header) != len(set(header)):
        raise ValueError(f"Duplicate raw column names: {p.name}")
    df = pd.read_csv(p, engine="c")
    if not len(df) or not df.columns.is_unique:
        raise ValueError(f"Empty data or duplicate column names: {p.name}")
    labs = [c for c in df if c.casefold() in {"label", "labels", "anomaly", "is_anomaly"}]
    if len(labs) != 1 or df.columns[-1] != labs[0]:
        raise ValueError(f"One terminal label column required: {p.name}")
    cols = list(df.columns[:-1])
    if any(c.casefold() in {"timestamp", "time", "datetime", "date", "index"} or c.startswith("Unnamed:") for c in cols):
        raise ValueError(f"Possible metadata input column needs manual review: {p.name}")
    x = df[cols].to_numpy(dtype=np.float64)
    y = df[labs[0]].to_numpy(dtype=np.float64)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError(f"Nonfinite input: {p.name}")
    if not np.isin(y, [0, 1]).all():
        raise ValueError(f"Nonbinary label: {p.name}")
    if (track == "U" and x.shape[1] != 1) or (track == "M" and x.shape[1] < 2):
        raise ValueError(f"Track/channel mismatch: {p.name}")
    boundary = int(m[5])
    if not 0 < boundary <= len(y):
        raise ValueError(f"Invalid training prefix: {p.name}")
    iv = intervals(y)
    meta = dict(relative_file_path=Path(relative).as_posix(), filename=p.name,
                dataset_source=m[2], source_family=m[2], domain=m[4],
                source_instance_id=m[3], source_instance_id_scope="track-local filename identifier; physical identity unknown",
                source_identity_confidence="filename source-family plus exact content; not external physical identity",
                sequence_length=len(y), channel_count=x.shape[1], train_prefix_boundary=boundary,
                train_start_index=0, train_end_exclusive=boundary, evaluation_start_index=0,
                evaluation_end_exclusive=len(y), filename_first_anomaly=int(m[6]),
                observed_first_anomaly=int(iv[0, 0]) if len(iv) else -1,
                label_column=labs[0], signal_columns=json.dumps(cols, ensure_ascii=False),
                file_sha256=sha256(p), file_size=p.stat().st_size, parser_version=PARSER_VERSION,
                label_hash=array_hash(y), anomaly_interval_hash=array_hash(iv),
                signal_shape=json.dumps(list(x.shape)), signal_array_hash=array_hash(x),
                channel_hashes=json.dumps([array_hash(x[:, i]) for i in range(x.shape[1])]),
                boundary_basis="implementation-confirmed filename-prefix convention",
                alignment="position-index alignment", source_reference="TSB-AD evaluation input")
    return meta, x, y

def write_csv(path, rows, fields=None):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(rows[0]) if rows else ["status"])
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def manifest_names(path):
    rows = read_csv(path)
    if not rows:
        raise ValueError("Empty candidate manifest")
    names = [r.get("relative_file_path", r.get("file_name", r.get("filename", ""))) for r in rows]
    if not all(names) or len(names) != len(set(names)):
        raise ValueError("Missing or duplicate candidate manifest identity")
    return sorted(names)

def inventory(root, names, track):
    data, errors = [], []
    for n in names:
        try:
            meta, x, y = read_series(root, n, track)
            data.append(meta)
            del x, y
        except (ValueError, OSError, pd.errors.ParserError) as e:
            # Do not serialize private absolute exception paths.
            errors.append(dict(track=track, relative_file_path=n, error_type=type(e).__name__))
    return data, errors

def classify(candidates):
    """No arbitrary tie-breaking. All eligible one-to-many ambiguity is excluded."""
    eligible = [r for r in candidates if r["checks_pass"]]
    by_u, by_mc = defaultdict(list), defaultdict(list)
    for r in eligible:
        by_u[r["u_relative_path"]].append(r)
        by_mc[(r["m_relative_path"], r["m_channel_index"])].append(r)
    for r in candidates:
        reasons = []
        if r["checks_pass"]:
            group = by_u[r["u_relative_path"]]
            if len({a["m_relative_path"] for a in group}) > 1:
                reasons.append("MULTIPLE_M_PARENTS")
            if len(group) > len({a["m_relative_path"] for a in group}):
                reasons.append("MULTIPLE_CHANNELS_IN_PARENT")
            if len(by_mc[(r["m_relative_path"], r["m_channel_index"])]) > 1:
                reasons.append("MULTIPLE_U_FILES_FOR_CHANNEL")
        r["ambiguity"] = ";".join(reasons)
        r["status"] = ("AMBIGUOUS" if reasons else "STRICT_UNAMBIGUOUS") if r["checks_pass"] else "REJECTED"
    return candidates

def discover(u_root, m_root, u_meta, m_meta):
    index = defaultdict(list)
    for m in m_meta:
        for i, h in enumerate(json.loads(m["channel_hashes"])):
            index[(int(m["sequence_length"]), h)].append((m, i))
    grouped = defaultdict(list)
    unmatched = []
    for u in u_meta:
        found = index.get((int(u["sequence_length"]), json.loads(u["channel_hashes"])[0]), [])
        if not found:
            unmatched.append(dict(u_relative_path=u["relative_file_path"], reason="NO_EXACT_SIGNAL_HASH_CANDIDATE"))
        for m, i in found:
            grouped[m["relative_file_path"]].append((u, m, i))
    candidates = []
    for mpath in sorted(grouped):
        _, mx, my = read_series(m_root, mpath, "M")
        for u, m, i in sorted(grouped[mpath], key=lambda t: (t[0]["relative_file_path"], t[2])):
            _, ux, uy = read_series(u_root, u["relative_file_path"], "U")
            signal = bool(np.array_equal(ux[:, 0], mx[:, i]))
            label = bool(np.array_equal(uy, my))
            iv = bool(np.array_equal(intervals(uy), intervals(my)))
            bound = u["train_prefix_boundary"] == m["train_prefix_boundary"]
            source = u["source_family"] == m["source_family"] and u["domain"] == m["domain"]
            first = u["filename_first_anomaly"] == m["filename_first_anomaly"]
            annotation = (u["filename_first_anomaly"] == u["observed_first_anomaly"]
                          and m["filename_first_anomaly"] == m["observed_first_anomaly"])
            checks = dict(signal_exact=signal, labels_exact=label, anomaly_intervals_exact=iv,
                          train_boundary_exact=bound, source_family_consistent=source,
                          filename_first_anomaly_consistent=first,
                          filename_label_annotation_consistent=annotation)
            row = dict(pair_id=hashlib.sha256(f'{u["relative_file_path"]}|{mpath}|{i}'.encode()).hexdigest()[:20],
                       u_relative_path=u["relative_file_path"], m_relative_path=mpath,
                       m_channel_index=i, m_channel_name=json.loads(m["signal_columns"])[i],
                       source_family=u["source_family"], domain=u["domain"],
                       u_file_sha256=u["file_sha256"], m_file_sha256=m["file_sha256"],
                       signal_hash=json.loads(u["channel_hashes"])[0], label_hash=u["label_hash"],
                       anomaly_interval_hash=u["anomaly_interval_hash"],
                       sequence_length=u["sequence_length"], train_prefix_boundary=u["train_prefix_boundary"],
                       evaluation_start_index=0, evaluation_end_exclusive=u["sequence_length"],
                       physical_source_instance="UNKNOWN", alignment="position-index alignment", **checks,
                       checks_pass=all(checks.values()),
                       rejection_reason=";".join(k for k, v in checks.items() if not v))
            candidates.append(row)
            del ux, uy
        del mx, my
    return classify(candidates), unmatched

def duplicate_groups(metas, track):
    rows = []
    for kind, key in [("BYTE_IDENTICAL_FILE", "file_sha256"), ("SIGNAL_AND_LABEL_IDENTICAL", None)]:
        groups = defaultdict(list)
        for m in metas:
            ident = m[key] if key else (m["signal_array_hash"], m["label_hash"])
            groups[ident].append(m["relative_file_path"])
        for group in groups.values():
            if len(group) > 1:
                rows.append(dict(track=track, duplicate_type=kind, files=json.dumps(sorted(group))))
    return rows

def check_pair(row, u_root, m_root):
    errors = []
    try:
        u, ux, uy = read_series(u_root, row["u_relative_path"], "U")
        m, mx, my = read_series(m_root, row["m_relative_path"], "M")
        i = int(row["m_channel_index"])
        if not 0 <= i < mx.shape[1]:
            return ["INVALID_CHANNEL_INDEX"]
        for k, actual in [("u_file_sha256", u["file_sha256"]), ("m_file_sha256", m["file_sha256"]),
                          ("label_hash", u["label_hash"]), ("signal_hash", array_hash(ux[:, 0])),
                          ("anomaly_interval_hash", u["anomaly_interval_hash"])]:
            if row.get(k) != actual:
                errors.append(k.upper() + "_MISMATCH")
        if json.loads(m["signal_columns"])[i] != row.get("m_channel_name"):
            errors.append("CHANNEL_NAME_MISMATCH")
        if not np.array_equal(ux[:, 0], mx[:, i]): errors.append("SIGNAL_MISMATCH")
        if not np.array_equal(uy, my): errors.append("LABEL_MISMATCH")
        if not np.array_equal(intervals(uy), intervals(my)): errors.append("INTERVAL_MISMATCH")
        if u["train_prefix_boundary"] != m["train_prefix_boundary"] or int(row["train_prefix_boundary"]) != u["train_prefix_boundary"]:
            errors.append("BOUNDARY_MISMATCH")
        if u["source_family"] != m["source_family"] or u["domain"] != m["domain"]:
            errors.append("SOURCE_CONFLICT")
        if row.get("source_family") != u["source_family"] or row.get("domain") != u["domain"]:
            errors.append("SOURCE_METADATA_MISMATCH")
        if int(row["sequence_length"]) != len(uy): errors.append("LENGTH_MISMATCH")
        if int(row["evaluation_start_index"]) != 0 or int(row["evaluation_end_exclusive"]) != len(uy):
            errors.append("EVALUATION_RANGE_MISMATCH")
        if u["filename_first_anomaly"] != m["filename_first_anomaly"]:
            errors.append("FIRST_ANOMALY_METADATA_MISMATCH")
        if any(meta["filename_first_anomaly"] != meta["observed_first_anomaly"] for meta in [u, m]):
            errors.append("FILENAME_LABEL_ANNOTATION_INCONSISTENT")
    except (ValueError, OSError, KeyError, IndexError, pd.errors.ParserError) as e:
        errors.append(type(e).__name__)
    return errors
