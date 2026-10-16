# Component-specific licensing

**This repository is publicly available on GitHub.** Its current status is recorded in [RELEASE_READINESS.md](RELEASE_READINESS.md), separately from historical pre-publication gate records. Public visibility and author maintenance authorization do not certify third-party rights clearance. Choosing a license for particular original contributions does not resolve excluded materials' rights.

## MIT applies only to the enumerated original Python code

Copyright (c) 2026 Peng Zhang. The author declared that this reproduction project was developed independently with Codex, without other direct code developers or reported institutional/project agreement restrictions. This is an author declaration, not an independently signed legal certification.

The complete [MIT License](LICENSES/MIT.txt) applies **only** to the original Python source and test files enumerated with SHA256 in [code_license_scope.json](manifests/code_license_scope.json). That list covers the present seven `scripts/*.py` and eight `tests/*.py` files. Future files are not automatically included. No frozen scientific file was edited merely to insert a license header. The inventory makes the application scope explicit without replacing the standard MIT text.

The license includes comments/docstrings within those enumerated Python files. It does **not** extend the phrase "associated documentation" to the separate documents or datasets excluded below. MIT's permission text does not impose an additional noncommercial condition on the licensed code. Historical project-release holds recorded a preparation-stage workflow decision, not an amendment to MIT's terms or the current repository visibility.

## CC BY 4.0 applies to enumerated original document prose

Copyright (c) 2026 Peng Zhang. The author has selected **Creative Commons Attribution 4.0 International (CC BY 4.0)** for the original, author-owned prose in the eleven documents listed in [document_license_scope.json](manifests/document_license_scope.json). The scope is README, REPRODUCIBILITY, DATA_SOURCES, RELEASE_READINESS, LICENSING, THIRD_PARTY_NOTICES, and the five standalone documents in `docs/`: MATCHING_PROTOCOL, STATISTICAL_PROTOCOL, ENVIRONMENT, LIMITATIONS and LICENSE_NOTES.

Use the [official license](https://creativecommons.org/licenses/by/4.0/) and its [unchanged local legal text](LICENSES/CC-BY-4.0.txt). When sharing covered material, retain supplied creator/copyright, license and disclaimer notices, provide a reasonably practicable source link, link or reproduce the license, and indicate modifications while retaining prior change indications. Suggested credit: **Peng Zhang (2026), document title and source, CC BY 4.0; describe any changes.** No NonCommercial or ShareAlike requirement is added to this original prose. Commercial reuse is not excluded by the author's CC BY grant.

This grant is limited to the author's rights. Third-party titles, names, citations, original copyright/permission notices, license legal texts and other protected third-party expressions retain their original status. Individual facts do not acquire new exclusive rights from this notice. The separate data/compilation grant below is explicit, not inferred from the document grant. Scope exceptions are explicit per file in the inventory; no unidentified copied third-party prose is knowingly relicensed.

## CC BY 4.0 applies to the author's licensable original mappings and compilations

Copyright (c) 2026 Peng Zhang. The author separately selects CC BY 4.0 for original pair-mapping organization, hash-index organization, metadata compilation, frozen model-metric compilation and statistical compilation listed with SHA256 in [data_license_scope.json](manifests/data_license_scope.json). The grant covers only the author's rights, including applicable author-held compilation/database rights. It does not create exclusive rights over individual facts, identifiers, hashes or numerical values, and does not relicense third-party source data, annotations, protected selection/arrangement, database rights or original legal notices. Listing a mixed file does not mean the author owns every field in it.

Retain supplied creator/copyright, source, license and disclaimer notices; link to CC BY 4.0 or reproduce it; indicate changes and retain previous change indications. Suggested credit: Peng Zhang (2026), TSB-AD U/M Strict Matched Subset, relevant file title, CC BY 4.0; describe changes. No extra NonCommercial or ShareAlike restriction is added to independent author contributions. Applicable third-party conditions still govern excluded material. Scope exclusions do not themselves clear third-party rights.

The historical internal hold on uploading **this mixed-material package** was a project workflow status, not an additional restriction on recipients' lawful use of MIT code or CC BY prose. It does not amend either standard license or require separate permission for uses already permitted by them. Current PUBLIC visibility does not waive any applicable third-party condition.

## Materials not granted MIT by this project

- Inventoried standalone documents: original prose has the separate CC BY 4.0 scope above, not MIT. CITATION and other metadata are covered only where explicitly enumerated in the separate data scope.
- Pair mappings, parent tables, candidate tables, U/M manifests and filename/hash indices: author-licensable original organization/compilation is CC BY 4.0; source annotation/boundary and third-party database rights are excluded from that grant.
- Frozen model metrics, parent effects and statistical reference outputs: author-licensable original compilation is CC BY 4.0; source identifiers retain their applicable source conditions. Public distribution does not certify clearance of excluded third-party rights.
- Third-party licenses, attribution facts and notices: remain governed by their original terms, not relicensed here.
- Original TSB-AD/source signals, archives, annotations and external repositories: not distributed here and never licensed by this MIT grant.

No blanket license is assigned to every CSV/JSON/text file. The absence of raw signals does not settle every database or derived-material right. Source-specific statements in [LICENSE_NOTES](docs/LICENSE_NOTES.md) and [License_Matrix](docs/License_Matrix.csv) remain relevant; unresolved applicability is NEEDS_RIGHTS_HOLDER_CONFIRMATION.

Source credits and applicable-notice reminders are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). That file is not a certification that every third-party permission or notice obligation is closed.

Newly discovered relationships, locally computed digests, individual model-evaluation numbers and original statistical calculations are not automatically adapted source data merely because source data were inputs. Their factual or author-generated nature must be distinguished from protected source annotations or substantial database extraction. The author's data/compilation license is decided and implemented; the repository is public, while specific third-party applicability questions remain disclosed. No evidence has established a blanket extra written-permission requirement for all such outputs. Where existing source licenses cover a particular redistribution, apply those conditions rather than mechanically requesting the same permission again; genuine unresolved scope questions remain specific to the affected fields/material.

## Private approval evidence is separate

The public package contains only a sanitized decision summary. Private author declarations, approval records, correspondence and signatures stay outside the publication inventory. A local author can supply an external review store to `check_release.py --authorization-root`; its hashes and exact scope are checked without copying evidence into this package. Hashes alone cannot authenticate legal authority. Historical approval flags in the scope inventories and `release_authorization.json` describe the pre-publication gate, not current visibility or new legal clearance. This maintenance does not supply new private rights-review evidence or retroactively pass that gate.

We use `LICENSES/MIT.txt` plus this explicit scope and machine-readable inventory rather than a blanket root LICENSE. Automated repository license badges may not recognize this nested/mixed scope reliably. Clear scope takes priority over a badge; repository availability must not be read as a blanket MIT or CC BY license for every file and field.

Original prose in this document: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), subject to the explicit third-party/data exceptions above. Retain attribution/license notices and indicate changes.
