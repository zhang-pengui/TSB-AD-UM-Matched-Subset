# TSB-AD U/M Strict Matched Subset

Local release candidate supporting the same-instance representation analysis in **HA-PaAno: Heterogeneity-Aware Patch Representation Refinement for Univariate and Multivariate Time-Series Anomaly Detection**.

**Status: local preparation only; no remote repository or upload is authorized.** Current official archive contents are verified at **LEVEL 2**: all 530 evaluation CSVs, including the 82 matched-subset files, are byte-identical to the frozen inputs. Historical download identity remains unverified. Technical preparation, third-party scope, and permission to publish are separate matters; see [RELEASE_READINESS.md](RELEASE_READINESS.md).

**Scoped code license: MIT, Copyright (c) 2026 Peng Zhang.** This applies only to the enumerated original Python scripts and tests in [code_license_scope.json](manifests/code_license_scope.json), under [LICENSES/MIT.txt](LICENSES/MIT.txt). It does not license the whole repository, separate documentation, mapping CSVs, indices, frozen metrics or third-party materials. See [LICENSING.md](LICENSING.md). **This local offline package is NOT_AUTHORIZED_FOR_PUBLICATION; do not upload it.**

**Scoped document license: CC BY 4.0, Copyright (c) 2026 Peng Zhang.** This covers the author-owned original prose in [document_license_scope.json](manifests/document_license_scope.json), with explicit third-party exceptions. **Scoped data/compilation license: CC BY 4.0** covers the author's licensable original pair-mapping organization, hash-index organization, metadata compilation, frozen model-metric compilation and statistical compilation listed in [data_license_scope.json](manifests/data_license_scope.json). Retain credit, source/license notices and indications of changes. This grant creates no exclusive rights over individual facts and does not relicense third-party data, annotations or database rights. No additional noncommercial or share-alike condition is imposed on the author's independent contributions; applicable third-party conditions remain intact.

This package reconstructs channel-level relationships within the existing [TSB-AD benchmark](https://github.com/TheDatumOrg/TSB-AD). It is not a new dataset, independent benchmark, OOD evaluation, or full HA-PaAno implementation. It contains no raw signals, checkpoints, model, training code, or evaluator. Public data availability does not imply unrestricted redistribution.

## Scope and reference mapping

The fixed evaluation universe is **350 U sequences and 180 M sequences**, containing **5,244 M channels**. Exact signal indexing followed by elementwise verification yields **52 U views / 30 M parents / 7 sources**. Matching does not read model metrics or use the historical mapping as a discovery input. This current reconstruction does not establish historical preregistration or exclude all historical selection bias.

| Source | U views | M parents |
|---|---:|---:|
| Daphnet | 1 | 1 |
| Exathlon | 3 | 3 |
| LTDB | 6 | 3 |
| MSL | 2 | 2 |
| SMAP | 12 | 12 |
| SMD | 19 | 2 |
| SVDB | 9 | 7 |

Of 216 exact-signal candidate rows, 52 are strictly unambiguous, 161 are ambiguous, and 3 are rejected. The 161 ambiguous rows involve 27 U files, not 161 independent sequences. Three further U files have rejected candidates; 268 U files have no exact-signal candidate. All candidates are retained in `manifests/all_discovered_candidate_pairs.csv`.

## Data acquisition and environment

Acquire U/M data through the [official TSB-AD repository](https://github.com/TheDatumOrg/TSB-AD) under the applicable source-specific terms. The data archives are [TSB-AD-U.zip](https://www.thedatum.org/datasets/TSB-AD-U.zip) and [TSB-AD-M.zip](https://www.thedatum.org/datasets/TSB-AD-M.zip). See [DATA_SOURCES.md](DATA_SOURCES.md) for version limits. Do not assume any archive version matches merely because its filenames agree.

Python 3.12.14, NumPy 2.3.5, and pandas 3.0.1 were used for the frozen validation. `requirements.txt` pins that parser/statistics environment, not a tested minimum-version range. Two additional existing environments were tested as discrete compatibility points; see [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md). No GPU or original research directory is needed. Third parties may install dependencies in their own environment:

```text
python -m pip install -r requirements.txt
```

Extract each official ZIP into your own data directory. The verified archives contain `TSB-AD-U/<CSV files>` and `TSB-AD-M/<CSV files>`. Set the roots to those directories; only entries in the fixed evaluation manifests are read. The current snapshots contain 870 U and 200 M CSVs, of which 350/180 are evaluated here. Do not rewrite source data to make it pass.

```text
DATA_ROOT/
  TSB-AD-U/<CSV files>
  TSB-AD-M/<CSV files>
```

## Reproduction commands

Run from this package root; replace `DATA_ROOT` with your own path. Output directories must be new and outside the input data roots.

```text
python -B scripts/verify_dataset.py --u-root DATA_ROOT/TSB-AD-U --m-root DATA_ROOT/TSB-AD-M --u-manifest manifests/u_eval_manifest.csv --m-manifest manifests/m_eval_manifest.csv --output reports/dataset_verification.json
python -B scripts/discover_pairs.py --u-root DATA_ROOT/TSB-AD-U --m-root DATA_ROOT/TSB-AD-M --u-manifest manifests/u_eval_manifest.csv --m-manifest manifests/m_eval_manifest.csv --output-dir rebuilt
python -B scripts/verify_pairs.py --u-root DATA_ROOT/TSB-AD-U --m-root DATA_ROOT/TSB-AD-M --pairs manifests/pairs_52.csv --output reports/pair_verification.json
python -B scripts/reproduce_statistics.py --pairs manifests/pairs_52.csv --results statistics/matched_seed_results.csv --output-dir reproduced_statistics --reference statistics/statistics_reference.json
python -B scripts/run_cpu_tests.py
python -B scripts/check_release.py --root . --output reports/release_scan.json
```

Compare discovered identities `(u_relative_path, m_relative_path, m_channel_index)` with `manifests/pairs_52.csv`; do not compare row positions only. Pair verification validates supplied pairs but does not replace full-universe discovery and ambiguity checks. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for interpretation and failure behavior.

The release scanner returns **2** for NOT_READY even when there are no content findings. It checks payload integrity, source provenance, and authorization separately. Disclosed LEVEL 2 provenance is eligible for further checks, not an automatic failure or approval. Unresolved rights and author approval still block publication. Test output logs are local validation artifacts, not additional scientific evidence.

`manifests/release_allowlist.json` is the explicit hash-bound proposed payload inventory (excluding its own self-hash), not approval to publish. Root Git metadata, bytecode associated with inventoried source, recognized pytest metadata, and validated CPU/release-run reports are non-payload. Other files, including ignored files, require explicit review; do not upload an entire working directory after running reproduction commands. `manifests/release_authorization.json` is a sanitized summary, not private evidence or a permission grant. Author-side review evidence stays outside the package and is read only when an explicit `--authorization-root` is supplied. Future approval must cover the exact inventory and include final human review; machine checks cannot authenticate rights holders or replace legal review.

## Strict matching

The original CSV parser policy and matching algorithm are retained byte-for-byte. All signal values, binary labels, anomaly intervals, training-prefix boundaries, evaluation ranges, and source/domain annotations must match. Hashes only index candidates; arrays are reopened and compared exactly under the documented float64 parsing policy. No tolerance, normalization, affine transform, DTW, or performance-based selection is used.

Duplicates, multiple parents, and competing views of one M channel remain unresolved candidates, never first-match choices. Alignment is **position-index alignment**, not independently established timestamp or physical-device identity. Track-local numeric source IDs need not agree. A known, unmatched WSD filename annotation conflict is explicitly retained in `manifests/metadata_review_required.csv` and never repaired. See [docs/MATCHING_PROTOCOL.md](docs/MATCHING_PROTOCOL.md).

## Frozen statistics

The 984 metric observations cover U/M × C/JC/LC/JLC × seeds 2000–2002 × six metrics. C is CAC-only; J is Jitter; L is LSDP. M-C uses revised CAC without relative normalization. This comparison is **JLC−C**, not the main-table HA-PaAno−PaAno-Re comparison.

| Quantity | Reference value |
|---|---:|
| U JLC−C, parent-aggregated | +0.009873219616343635 |
| M JLC−C | −0.028851310533726547 |
| H = U−M | +0.03872453015007018 |
| H parent positive/negative/zero | 17/13/0 |
| Source→parent 95% CI | [−0.01705001298510966, +0.10177953574410095] |

The bootstrap runs 10,000 replicates with one PCG64 stream seeded 20260922, preserving all 18 historical contrast/metric slots. The CI crosses zero. These are descriptive benchmark-subset results; they do not establish causal channel effects or universally preferred modules. See [docs/STATISTICAL_PROTOCOL.md](docs/STATISTICAL_PROTOCOL.md).

## Licenses, citation, and release approval

The author has selected MIT for the specified original Python code/tests and CC BY 4.0 for the inventoried original document prose and the author's licensable mapping/hash/metadata/metric/statistical compilations. TSB-AD's code/curation license does not automatically cover all source data; third-party exceptions remain explicit in [LICENSING.md](LICENSING.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Raw signals are deliberately excluded. `CITATION.cff` identifies the declared software author separately from manuscript authorship, without inventing a DOI, existing public repository, release version, or publication date. Creating a remote repository, uploading, and changing visibility still require separate authorization.

Public copies omit internal metric-source paths while preserving logical IDs, source hashes, and every numerical cell. `manifests/public_copy_provenance.json` records exact-copy, metadata-only, and release-policy remediation changes. Core matching and statistical algorithms are unchanged; only release checking and its tests/documentation were remediated. Known limitations are listed in [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

Original prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Third-party expressions and underlying factual/source/result data are excepted as specified in [LICENSING.md](LICENSING.md).
