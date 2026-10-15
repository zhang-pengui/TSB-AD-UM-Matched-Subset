# Reproduction guide

## 1. Obtain the source data

Use the official links in `DATA_SOURCES.md` and comply with each source's terms. The verified ZIPs extract as `TSB-AD-U/<CSV files>` and `TSB-AD-M/<CSV files>`; use these directories as the respective roots. They contain 870 and 200 CSVs, and the fixed manifests select 350/180. Each root must expose the manifest relative paths directly. The manifests describe CSV bytes, columns, parsed-array hashes, labels, and boundary annotations; they are not raw-signal files. The current downloaded snapshots match all 530 frozen evaluation files byte-for-byte. Hash your downloaded archives and verify every selected CSV; matching names alone are insufficient, and historical archive identity is not established merely by current content agreement.

Do not rename unmatched files, reorder columns, normalize, round, or insert missing observations to force agreement. If a current archive differs, report the difference instead of changing the frozen manifests.

## 2. Validate the candidate universe

From the package root:

```text
python -B scripts/verify_dataset.py --u-root DATA_ROOT/TSB-AD-U --m-root DATA_ROOT/TSB-AD-M --u-manifest manifests/u_eval_manifest.csv --m-manifest manifests/m_eval_manifest.csv --output reports/dataset_verification.json
```

This checks all 530 file identities and column headers. Exit 0 means the pinned file checks pass. An existing unmatched WSD metadata annotation is separately reported; its content is not repaired. A byte or header mismatch returns nonzero. This step is not model evaluation and does not establish independent physical-source identity.

## 3. Discover independently

```text
python -B scripts/discover_pairs.py --u-root DATA_ROOT/TSB-AD-U --m-root DATA_ROOT/TSB-AD-M --u-manifest manifests/u_eval_manifest.csv --m-manifest manifests/m_eval_manifest.csv --output-dir rebuilt
```

`rebuilt` must be new: sealed output is not overwritten. Discovery inventories every listed file and every M channel, then compares exact candidates. It receives neither frozen model metrics nor a historical mapping. Expected strict counts are 52 U views, 30 M parents, and 7 sources; a different outcome is a finding, not permission to alter rules.

Inspect `rebuilt/all_discovered_candidate_pairs.csv`, `unmatched_u.csv`, `duplicate_groups.csv`, and `metadata_review_required.csv`. Compare the identity set in `rebuilt/pairs_discovered.csv` with `(u_relative_path,m_relative_path,m_channel_index)` in `manifests/pairs_52.csv`. Historical pair IDs used a different string length and are not the comparison key.

## 4. Reopen and verify the selected pairs

```text
python -B scripts/verify_pairs.py --u-root DATA_ROOT/TSB-AD-U --m-root DATA_ROOT/TSB-AD-M --pairs manifests/pairs_52.csv --output reports/pair_verification.json
```

Missing files, wrong channels, changed hashes, invalid statuses, or duplicate identities fail. Pairwise verification alone cannot establish candidate-universe uniqueness; retain the discovery seal and all candidate rows.

## 5. Reproduce the frozen statistics without signal data

```text
python -B scripts/reproduce_statistics.py --pairs manifests/pairs_52.csv --results statistics/matched_seed_results.csv --output-dir reproduced_statistics --reference statistics/statistics_reference.json
```

This is CPU-only aggregation of already frozen metrics, not training, inference, or an evaluator run. The output directory must be new. The script computes parent effects and all 18 bootstrap slots before consulting the reference. A reference mismatch exits 1; invalid inputs exit 2. Reference comparisons use absolute tolerance 1e-12, not an assertion of floating-point bit identity.

## 6. Run tests and release checks

```text
python -B scripts/run_cpu_tests.py
python -B scripts/check_release.py --root . --output reports/release_scan.json
```

The inherited suite contains 34 CPU tests. Additional release-gate tests use explicitly synthetic provenance and approval fixtures; these are not real permissions or official-data evidence. Fixtures are created inside this package and cleaned up. Tests do not establish third-party official-archive reproducibility. The runner writes its own `reports/cpu_tests.json` and log. The release scanner inspects files even when ignored by `.gitignore`, and returns 2 while the release is NOT_READY. Do not remove licensing blockers to obtain a green exit code.

The proposed payload inventory is `manifests/release_allowlist.json`, not a publication grant. Known Git/cache/run metadata are non-payload; unknown files are not silently ignored. Discovery and statistics outputs created by the above commands are analysis products, not automatically approved additions to the publication inventory. Review and inventory them separately before any future publication. LEVEL 2 source evidence and publication authorization are independent gates. `manifests/release_authorization.json` is a sanitized public summary, not private evidence; a status string or a license file alone is insufficient.

The enumerated original Python code/tests have the scoped MIT license. Original tutorial/method prose and the author's licensable mapping/hash/metadata/metric/statistical compilations have scoped CC BY 4.0 grants described in `LICENSING.md` and the three license-scope inventories. Third-party exceptions are not relicensed. Private declarations, correspondence and approval evidence must not be copied into this package. The local author-side checker optionally accepts `--authorization-root AUTH_REVIEW_ROOT`, an explicit directory outside (and not a parent of) the package. It verifies evidence hashes, the exact material scope and a final human-review record, without distributing the evidence. Ordinary recipients do not need that private store to reproduce the frozen statistics. Local technical preparation is not public-release approval: the unchanged release scanner correctly returns NOT_READY while public approval is withheld. No remote creation or upload is authorized in this stage.

See `docs/ENVIRONMENT.md` for the pinned environment, separately tested compatibility points, and the user-reported environment that was not rerun here. No minimum Python release or continuous package-version range has been validated.

## Evidence levels

Report separately: UNIT_TEST_PASS; LOCAL_FROZEN_DATA_INTEGRATION_PASS; OFFICIAL_ARCHIVE_REPRODUCTION_PASS; THIRD_PARTY_ENVIRONMENT_VERIFIED. A relocated copy on the same machine is a portability smoke test, not an independent third-party environment. The latest source-verification status must be read from `DATA_SOURCES.md` and `RELEASE_READINESS.md`.

Original prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Third-party expressions and underlying data are excluded; see [LICENSING.md](LICENSING.md).
