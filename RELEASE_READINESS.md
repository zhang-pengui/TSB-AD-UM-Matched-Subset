# Repository status and release-gate context

## Current repository status

The repository has been created and uploaded and is **PUBLIC** at [zhang-pengui/TSB-AD-UM-Matched-Subset](https://github.com/zhang-pengui/TSB-AD-UM-Matched-Subset). Its default branch is `main`, available to external readers. This status was verified through the GitHub API on **2026-10-16**; that verification date is not asserted to be the original publication date.

The author has authorized this documentation, citation, and release-metadata maintenance commit and push. That limited maintenance authorization neither changes repository visibility nor certifies third-party rights. No tagged software release, release version, or DOI is asserted by this update.

## Reproducibility scope

The public materials contain **52 U channel views / 30 M parent instances / 7 sources**, candidate discovery and pair-verification tools, strict mapping manifests, **984 frozen three-seed metric rows**, and statistical reproduction procedures preserving **18 bootstrap slots**. They support the strict same-instance U/M analysis in HA-PaAno within TSB-AD.

They do not contain original signals, model checkpoints, the complete HA-PaAno training/inference implementation, a complete ten-seed experimental release package, or independent OOD validation. The 52 views represent 30 parents rather than 52 independent parents. The hierarchical CI crosses zero; position-index matching does not independently verify physical devices or timestamps. No causal channel effect or universal module preference follows from these materials.

## Technical verification

Technical evidence consists of CPU unit tests, CLI help checks, hash-bound file-integrity checks, and reproduction of the 984-row / 18-slot frozen statistics. Current maintenance reruns these lightweight checks without signal processing, model training, inference, or evaluator execution. The exact environment remains documented in [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md); a same-machine check is not independent third-party reproduction.

The 2026-10-16 maintenance check passed **77 CPU tests**, **five CLI help checks**, and **all 18 frozen statistical slots** against the reference (absolute tolerance 1e-12; maximum observed difference 0). The payload remains 60 files, with no content findings from the unchanged release scanner. These technical results are separate from its retained approval-gate result below.

The unchanged `scripts/check_release.py` separately checks payload integrity, source provenance, and evidence-based approval. With the preserved historical approval flags and no external private review store, it can return **NOT_READY (exit 2)** even when payload checks pass. That result must not be called a frozen-statistic reproduction failure or used to deny the observed PUBLIC visibility. Conversely, PUBLIC visibility is not a substitute for rights-review evidence. Genuine missing files, content mismatches, unknown payload files, and hash drift remain findings; no checker or test is weakened by this update.

## Source provenance

Current official archives match all **530** frozen evaluation files exactly, including all **82** subset files: **LEVEL 2**. Original historical download-archive identity and an upstream-authenticated historical checksum remain unverified; **LEVEL 1 is not claimed**. Current official content equality is not official authentication of the historical downloaded archive. Correctly disclosed LEVEL 2 evidence can pass the source gate with limitations; it is not itself a publication or rights decision.

## Licensing and third-party limitations

The implemented author grants are MIT for **15** enumerated original Python scripts/tests, CC BY 4.0 for original prose in **11** inventoried documents, and CC BY 4.0 for the author's licensable original pair-mapping/hash-index organization and metadata/metric/statistical compilations. Copyright is 2026 Peng Zhang. Software authorship is distinct from paper authorship; the author's declaration is not an independently signed legal certification. The standard license texts and third-party exceptions remain unchanged. See [LICENSING.md](LICENSING.md), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), and [docs/LICENSE_NOTES.md](docs/LICENSE_NOTES.md).

Specific remaining uncertainties concern SMAP/MSL telemetry/annotation terms, first-anomaly/boundary/index metadata, possible substantial source-index/database extraction, and the applicability of Exathlon's data conditions to retained derived materials. The full Exathlon candidate scope is broader than its three strict parents. Public availability does not resolve those uncertainties. Existing source conditions must be satisfied where applicable; author-created facts, code, prose and independent model numbers must not automatically be treated as source adaptations. Unresolved applicable scope remains **NEEDS_RIGHTS_HOLDER_CONFIRMATION**, without inventing a blanket extra written-permission requirement for every mapping or number.

## Historical release-gate context

The original preparation candidate was **NOT_READY** and its sanitized summary recorded **PUBLIC_RELEASE_NOT_APPROVED**. The author subsequently made the repository public. Those are facts from different stages: the former describes the pre-publication evidence gate; the latter describes actual current visibility.

Historical approval booleans in `manifests/release_authorization.json` and the license-scope records are retained, explicitly contextualized, and not silently promoted to verified rights clearance. Current repository status is recorded separately. Historical provenance hashes remain historical; `manifests/release_allowlist.json` binds current payload bytes and excludes its own self-hash. Updated document/data-scope hashes do not change scientific values or create new permission evidence.

Private declarations, correspondence, signatures and internal reports are not public payload. The checker can use only an explicitly supplied external review directory through `--authorization-root`; this maintenance supplies no new private legal evidence and does not fabricate historical approval. Technical validation, public visibility, and third-party rights remain separate matters.

Original prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Underlying facts/data and third-party rights are not newly licensed; see [LICENSING.md](LICENSING.md).
