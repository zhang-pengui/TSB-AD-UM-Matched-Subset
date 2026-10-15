"""CPU-only statistics from fixed pair mappings and exported frozen metrics.

This is an independently written implementation, not a model/evaluator entry.
Method reference (not a runtime dependency):
revision_experiments/tsbad_um_strict_paired_representation_audit/run_paired_audit.py
SHA256: c608338cbefdf48d7e9a2042591182d033fc2262f12705e35718dcb47ce68d7e
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SEEDS = (2000, 2001, 2002)
CONDITIONS = ("C", "JC", "LC", "JLC")
CONTRASTS = ("JC-C", "LC-C", "JLC-C")
METRICS = ("VUS_PR", "VUS_ROC", "Range_F1", "AUC_PR", "AUC_ROC", "Point_F1")
BOOTSTRAP_SEED = 20260922
RESAMPLES = 10_000
METHOD_REFERENCE = {
    "logical_id": "historical_strict_paired_audit_algorithm",
    "project_relative_path": "revision_experiments/tsbad_um_strict_paired_representation_audit/run_paired_audit.py",
    "sha256": "c608338cbefdf48d7e9a2042591182d033fc2262f12705e35718dcb47ce68d7e",
    "reuse": "independently rewritten method; upstream code not redistributed",
}


def file_hash(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def basename(value: str) -> str:
    return str(value).replace("\\", "/").rsplit("/", 1)[-1]


def checked_pairs(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize mapping names, without selecting or discovering any pairs."""
    aliases = {
        "pair_id": ("pair_id", "strict_pair_id"),
        "u_file": ("u_relative_path", "u_file", "U_file"),
        "m_parent": ("m_relative_path", "m_parent", "m_file", "M_file"),
        "source": ("source_family", "source"),
        "domain": ("domain",),
    }
    selected = {}
    for field, choices in aliases.items():
        found = next((name for name in choices if name in raw), None)
        if found is None:
            raise ValueError(f"Pair mapping lacks {field}")
        if raw[found].isna().any():
            raise ValueError(f"Pair mapping contains missing {field}")
        selected[field] = raw[found].astype(str)
    pairs = pd.DataFrame(selected)
    for field in ("u_file", "m_parent"):
        pairs[field] = pairs[field].map(basename)
    if pairs.empty or pairs.pair_id.duplicated().any() or pairs.u_file.duplicated().any():
        raise ValueError("Pairs must be nonempty with unique pair IDs and U views")
    parent_meta = pairs.groupby("m_parent")[["source", "domain"]].nunique()
    if (parent_meta > 1).any().any():
        raise ValueError("A parent has contradictory source/domain metadata")
    status_column = next((name for name in ("pair_status", "status") if name in raw), None)
    if status_column:
        statuses = set(raw[status_column].astype(str))
        if not statuses <= {"STRICT_MATCH", "VERIFIED", "PASS", "VALID", "STRICT", "LEVEL_A", "STRICT_UNAMBIGUOUS"}:
            raise ValueError(f"Non-strict or unresolved pairing status: {sorted(statuses)}")
    if "checks_pass" in raw and not raw.checks_pass.astype(str).str.lower().eq("true").all():
        raise ValueError("Pair mapping contains failed exact-data checks")
    return pairs


def checked_results(raw: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Require every specified observation; missing rows never become zero."""
    columns = ["track", "condition", "seed", "series_file", *METRICS]
    missing = sorted(set(columns) - set(raw))
    if missing:
        raise ValueError(f"Metrics lack columns: {missing}")
    result = raw.copy()
    result["series_file"] = result.series_file.map(basename)
    numeric_seed = pd.to_numeric(result.seed, errors="raise")
    if not np.equal(numeric_seed, numeric_seed.astype(int)).all():
        raise ValueError("Seeds must be integers")
    result["seed"] = numeric_seed.astype(int)
    result[list(METRICS)] = result[list(METRICS)].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(result[list(METRICS)].to_numpy(float)).all():
        raise ValueError("Metrics contain NaN or infinity")
    keys = ["track", "condition", "seed", "series_file"]
    if result.duplicated(keys).any():
        raise ValueError("Duplicate frozen metric observation")
    expected = {
        (track, condition, seed, series)
        for track, series_set in (("U", pairs.u_file.unique()), ("M", pairs.m_parent.unique()))
        for condition in CONDITIONS for seed in SEEDS for series in series_set
    }
    actual = set(result[keys].itertuples(index=False, name=None))
    if actual != expected:
        raise ValueError(f"Metric keys differ: missing={len(expected-actual)}, extra={len(actual-expected)}")
    return result


def parent_effects(pairs: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    """Within each seed, equal-weight U views before pairing with M."""
    lookup = results.set_index(["track", "condition", "seed", "series_file"])
    rows = []
    for contrast in CONTRASTS:
        high, low = contrast.split("-")
        for seed in SEEDS:
            for parent, views in pairs.groupby("m_parent", sort=True):
                row = {"contrast": contrast, "seed": seed, "source": views.source.iloc[0],
                       "domain": views.domain.iloc[0], "m_parent": parent, "n_u_channels": len(views)}
                for metric in METRICS:
                    u_values = [float(lookup.loc[("U", high, seed, series), metric] -
                                      lookup.loc[("U", low, seed, series), metric])
                                for series in views.u_file]
                    u_difference = float(np.mean(u_values))
                    m_difference = float(lookup.loc[("M", high, seed, parent), metric] -
                                         lookup.loc[("M", low, seed, parent), metric])
                    row[f"U_delta_{metric}"] = u_difference
                    row[f"M_delta_{metric}"] = m_difference
                    row[f"H_{metric}"] = u_difference - m_difference
                rows.append(row)
    return pd.DataFrame(rows)


def average_seeds(parents: pd.DataFrame) -> pd.DataFrame:
    effects = [name for name in parents if name.startswith(("U_delta_", "M_delta_", "H_"))]
    identifiers = ["contrast", "source", "domain", "m_parent", "n_u_channels"]
    counts = parents.groupby(identifiers).seed.agg(["count", "nunique"])
    if not (counts == len(SEEDS)).all().all():
        raise ValueError("Every parent/contrast must have exactly three distinct seeds")
    # pandas groupby sorting and means reproduce the historical parent-row order.
    return parents.groupby(identifiers, as_index=False, sort=True)[effects].mean()


def hierarchical_bootstrap(averaged: pd.DataFrame, resamples: int = RESAMPLES,
                           random_seed: int = BOOTSTRAP_SEED) -> dict:
    """Source→parent percentile bootstrap, preserving historical RNG consumption.

    The RNG is NOT reset between contrasts or metrics. All 18 preceding/order
    slots are evaluated, even when the main interest is JLC-C / VUS_PR.
    Sampled parents are concatenated and averaged, not source-equal weighted.
    """
    if resamples < 2:
        raise ValueError("Bootstrap requires at least two resamples")
    rng = np.random.default_rng(random_seed)
    records = []
    for contrast in CONTRASTS:
        current = averaged[averaged.contrast == contrast]
        sources = sorted(current.source.unique())
        if not sources:
            raise ValueError(f"Missing contrast {contrast}")
        for metric in METRICS:
            groups = {source: current.loc[current.source == source, f"H_{metric}"].to_numpy(float)
                      for source in sources}
            samples = np.empty(resamples, dtype=float)
            for draw in range(resamples):
                source_draw = rng.choice(sources, size=len(sources), replace=True)
                parent_draws = []
                for source in source_draw:
                    group = groups[source]
                    parent_draws.extend(rng.choice(group, size=len(group), replace=True))
                samples[draw] = np.mean(parent_draws)
            values = current[f"H_{metric}"].to_numpy(float)
            records.append({
                "contrast": contrast, "metric": metric, "parents": int(len(values)),
                "sources": int(len(sources)), "mean_H": float(values.mean()),
                "median_H": float(np.median(values)),
                "positive_parents": int((values > 1e-12).sum()),
                "negative_parents": int((values < -1e-12).sum()),
                "zero_parents": int((np.abs(values) <= 1e-12).sum()),
                "bootstrap_ci95_low": float(np.quantile(samples, .025, method="linear")),
                "bootstrap_ci95_high": float(np.quantile(samples, .975, method="linear")),
                "bootstrap_probability_mean_gt_zero": float((samples > 0).mean()),
                "bootstrap_draws_sha256": hashlib.sha256(samples.astype("<f8").tobytes()).hexdigest(),
            })
    return {"method": "source-to-parent hierarchical cluster bootstrap", "resamples": resamples,
            "rng_seed": random_seed, "bit_generator": type(rng.bit_generator).__name__,
            "contrast_order": list(CONTRASTS), "metric_order": list(METRICS),
            "rng_reinitialized_between_slots": False, "quantile_method": "linear",
            "replacement": "at source level and then within each sampled source",
            "replicate_weighting": "mean of all concatenated sampled parents; source sizes retained",
            "statistical_unit": "unique M parent after within-parent U-view and three-seed averaging",
            "results": records}


def summarize(averaged: pd.DataFrame) -> dict:
    def describe(values):
        values = np.asarray(values, dtype=float)
        return {"mean": float(values.mean()), "median": float(np.median(values)),
                "wins": int((values > 1e-12).sum()), "losses": int((values < -1e-12).sum()),
                "ties": int((np.abs(values) <= 1e-12).sum())}
    output = {}
    for contrast in CONTRASTS:
        current = averaged[averaged.contrast == contrast]
        output[contrast] = {key: describe(current[f"{key}_VUS_PR"])
                            for key in ("U_delta", "M_delta", "H")}
        output[contrast]["source_sensitivity"] = [
            {"source": source, "parents": len(group),
             **{f"mean_{key}": float(group[f"{key}_VUS_PR"].mean())
                for key in ("U_delta", "M_delta", "H")}}
            for source, group in current.groupby("source", sort=True)]
        output[contrast]["leave_one_source_out"] = [
            {"omitted_source": source, "remaining_parents": int((current.source != source).sum()),
             "mean_H": float(current.loc[current.source != source, "H_VUS_PR"].mean())}
            for source in sorted(current.source.unique()) if current.source.nunique() > 1]
    return output


def compare_historical(computed: dict, reference: dict, tolerance: float = 1e-12) -> dict:
    """Comparison only; reference values never affect computed estimates or draws."""
    old = {(row["contrast"], row["metric"]): row for row in reference["results"]}
    checks = []
    for row in computed["results"]:
        key = (row["contrast"], row["metric"])
        if key not in old:
            checks.append({"contrast": key[0], "metric": key[1], "status": "MISSING_REFERENCE"})
            continue
        fields = ("mean_H", "median_H", "bootstrap_ci95_low", "bootstrap_ci95_high",
                  "bootstrap_probability_mean_gt_zero", "positive_parents", "negative_parents", "zero_parents")
        differences = {name: float(row[name] - old[key][name]) for name in fields}
        checks.append({"contrast": key[0], "metric": key[1], "absolute_tolerance": tolerance,
                       "differences": differences,
                       "status": "PASS" if all(abs(value) <= tolerance for value in differences.values()) else "FAIL"})
    return {"status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL", "checks": checks}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--reference", type=Path, help="Optional saved bootstrap JSON, used only after calculation")
    args = parser.parse_args(argv)
    try:
        pairs = checked_pairs(pd.read_csv(args.pairs))
        metrics = checked_results(pd.read_csv(args.results), pairs)
        parents = parent_effects(pairs, metrics)
        averaged = average_seeds(parents)
        bootstrap = hierarchical_bootstrap(averaged)
        reference = {
            "schema_version": "1.0", "seeds": list(SEEDS),
            "pair_count": len(pairs), "parent_count": pairs.m_parent.nunique(),
            "source_count": pairs.source.nunique(), "metric_row_count": len(metrics),
            "input_sha256": {"pairs": file_hash(args.pairs), "results": file_hash(args.results)},
            "method_reference": METHOD_REFERENCE,
            "runtime": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__},
            "aggregation_order": "condition subtraction per U view and seed; equal U views within parent; M subtraction; H=U-M; equal three seeds per parent; equal-parent point estimates",
            "summary": summarize(averaged), "bootstrap": bootstrap,
            "limits": ["descriptive paired benchmark subset, not independent OOD",
                       "views belonging to one parent are not independent parents",
                       "CI including zero does not establish a direction or causal module preference"],
        }
        if args.reference:
            historical = json.loads(args.reference.read_text(encoding="utf-8-sig"))
            reference["historical_comparison"] = compare_historical(bootstrap, historical.get("bootstrap", historical))
            reference["historical_reference_sha256"] = file_hash(args.reference)
        destinations = [args.output_dir / name for name in
                        ("matched_parent_results.csv", "statistics_reference.json")]
        if any(path.exists() for path in destinations):
            raise ValueError("Refusing to overwrite outputs; select a new output directory")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        parents.to_csv(destinations[0], index=False, encoding="utf-8", float_format="%.17g")
        destinations[1].write_text(json.dumps(reference, ensure_ascii=False, indent=2), encoding="utf-8")
        comparison_ok = reference.get("historical_comparison", {}).get("status", "PASS") == "PASS"
        print(json.dumps({"status": "PASS" if comparison_ok else "REFERENCE_MISMATCH", "pairs": len(pairs), "parents": pairs.m_parent.nunique(),
                          "metrics": len(metrics), "primary": reference["summary"]["JLC-C"]}, ensure_ascii=False))
        return 0 if comparison_ok else 1
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f"Statistics reproduction failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
