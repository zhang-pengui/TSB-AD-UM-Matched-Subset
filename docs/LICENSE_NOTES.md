# License notes — implemented author grants and third-party exceptions

This repository is **PUBLIC**. Historical **NOT_READY** / **NOT_AUTHORIZED_FOR_PUBLICATION** preparation records are not descriptions of current visibility; see [RELEASE_READINESS.md](../RELEASE_READINESS.md). The author has selected MIT solely for the original Python scripts/tests explicitly inventoried in `manifests/code_license_scope.json`; see `LICENSING.md` and `LICENSES/MIT.txt`. There is no blanket root license for separate documents, manifests, metric exports or third-party materials. Public availability is not certification of third-party rights clearance.

The author has selected CC BY 4.0 for original prose in eleven inventoried documents, and separately for author-licensable original pair-mapping/hash-index organization, metadata compilation, frozen model-metric compilation and statistical compilation. See `manifests/document_license_scope.json` and `manifests/data_license_scope.json` at the package root. These license choices are decided and implemented. Historical approval flags are preserved with their preparation-stage context, not treated as evidence that all source rights are cleared. Third-party source annotations, data and database rights are not relicensed.

The scripts use Python, NumPy, and pandas as dependencies. They do not bundle model/evaluator implementations or third-party source repositories. The author declared independent development with Codex, no other direct code developers, and no applicable institutional/project agreement restrictions. Copyright is 2026 Peng Zhang as expressly confirmed by the author. File review has not found third-party vendoring, but that is not an independent legal certification of authorship or ownership. Software authorship and manuscript authorship are distinct; no rights of third parties are granted by that declaration.

TSB-AD identifies Apache-2.0 for code and preprocessing/curation materials, not blanket rights to every original dataset. Source families have separate terms. In particular, Exathlon's code and dataset licenses differ; its dataset uses noncommercial/share-alike terms. SMAP/MSL scope and derived-material obligations require careful review. Daphnet, LTDB, SVDB, and SMD also retain their own attribution and use conditions.

This public package excludes all 82 raw signal files, archives, checkpoints, model binaries, and original experiment logs. It includes filenames, hashes, pair annotations, and frozen metric exports. Exclusion of raw data does not automatically resolve every database/derivative right. The author's scoped license grants and documentation-maintenance authorization do not replace applicable source terms.

Using Exathlon as an input does not, by itself, establish that independently written scripts or every filename/hash or model-metric table is Adapted Material. Applicability of copyright and database rights to each redistributed artifact requires separate review under the [CC BY-NC-SA 4.0 legal text](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en). Do not apply the upstream Apache code license to the data, automatically impose ShareAlike on every script, or presume all derived tables are unrestricted. SMAP/MSL software-versus-telemetry scope likewise needs clarification against the actual [Caltech license text](https://github.com/khundman/telemanom/blob/master/LICENSE.txt), not the README wording alone. Unresolved cases remain **NEEDS_RIGHTS_HOLDER_CONFIRMATION**.

Detailed observed source URLs and review evidence are recorded in `manifests/upstream_source_review.json`. The latest component-by-component review is included as `docs/License_Matrix.csv`; completing that investigation is not equivalent to resolving every obligation. The matrix separates code, curation, original data, derived mapping/statistics, documentation, and separately installed dependencies.

| Component | Observed terms | Remaining condition |
|---|---|---|
| TSB-AD code and stated processing/curation | Apache-2.0, source data excluded from blanket grant | Retain applicable notices; do not generalize to signals |
| Daphnet | CC BY 4.0 | Attribution and appropriate changes notices |
| Exathlon data | CC BY-NC-SA 4.0, distinct from Apache-2.0 code | Noncommercial/ShareAlike and derived-material scope review |
| LTDB / SVDB | Open Data Commons Attribution License v1.0 | Database attribution and applicable notices |
| SMD source repository | MIT | Preserve applicable notices; transformed-data scope remains separate |
| SMAP / MSL | Actual Caltech redistribution conditions differ from README Apache wording | Software/external telemetry-data scope unresolved |
| Enumerated original Python scripts/tests | MIT, 2026 Peng Zhang, on the author's declaration | Scoped code grant only; no blanket grant over other materials |
| Enumerated original document prose | CC BY 4.0, 2026 Peng Zhang; third-party/data exceptions | Retain supplied notices/credit/source/license and indicate changes; no added NC/SA requirement |
| Separate mapping, metadata and metric/statistical compilation | CC BY 4.0 for the author's licensable original contributions, 2026 Peng Zhang | Third-party fields/rights excluded; source conditions preserved; public availability does not certify clearance |

## Narrow retained field-scope uncertainties

In `manifests/u_eval_manifest.csv` and `m_eval_manifest.csv`, the retained `relative_file_path`, `filename`, `source_instance_id`, `filename_first_anomaly`, `observed_first_anomaly`, `train_prefix_boundary` and training/evaluation range fields retain source-index/annotation context. In `pairs_52.csv`, `all_discovered_candidate_pairs.csv` and `parents_30.csv`, source filenames/channel associations and source-derived boundaries retain that same context. The full Exathlon candidate-table scope is broader than its three strict parents. In the statistical CSVs, `series_file`/`m_parent` row keys retain source identifiers; metric/difference values are independently computed results.

No concrete blanket prohibition on these independent facts/metrics has been established, but the author's CC BY grant cannot clear excluded third-party rights. For covered distribution, address an actually applicable gap by documenting existing terms covering the retained fields or obtaining narrow clarification if necessary. If a concrete condition cannot be satisfied, request separate authorization for a field-adjusted public derivative; do not edit frozen scientific files or silently drop sources. Existing conditions do not automatically require additional written permission. Neither free hosting nor private visibility alone satisfies an applicable NonCommercial condition.

Current official-data byte verification does not grant redistribution rights. The source review is evidence, not legal assurance or proof that all obligations have been satisfied. The repository is already uploaded and PUBLIC; no formal tagged release or DOI is asserted, and actual visibility does not retroactively pass the historical evidence gate.

Original commentary: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Actual third-party notices, protected expressions, legal texts and underlying data are excluded; see [LICENSING.md](../LICENSING.md).
