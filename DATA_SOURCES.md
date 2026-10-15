# Data sources and version identity

The authority is [TheDatumOrg/TSB-AD](https://github.com/TheDatumOrg/TSB-AD), not this derivative matching package. No signal archive is redistributed here.

## Fixed evaluation lists

The frozen lists originate from commit `6beac72e11d1155ade40870492c00d0d1cfdcaaf`:

| Track | Official repository path | Entries | Official-list SHA256 |
|---|---|---:|---|
| U | `Datasets/File_List/TSB-AD-U-Eva.csv` | 350 | `6f4e1d4ddbde195f9687f2c5a951b51faff54dda4b658d85f0c07e3e2879615a` |
| M | `Datasets/File_List/TSB-AD-M-Eva.csv` | 180 | `ef6353b5aad8519fb2e5ff366ae21cf626ecd56d1a05942ac3b5c02d9e4b32a4` |

These official-list bytes differ from the richer package manifests: `manifests/u_eval_manifest.csv` and `m_eval_manifest.csv` add file identities and parsed metadata. Do not compare their hashes as if they were the same artifact.

## Official archive entry points

- [TSB-AD-U archive](https://www.thedatum.org/datasets/TSB-AD-U.zip)
- [TSB-AD-M archive](https://www.thedatum.org/datasets/TSB-AD-M.zip)

Archive URLs do not themselves identify historical bytes. A locally computed download hash fixes the bytes acquired, but is not an independently authenticated historical upstream checksum. Current package agreement also cannot prove every earlier download was identical.

## Current source-verification status

**LEVEL 2 / PARTIALLY_VERIFIED historical identity.** Both current official archives were downloaded from `www.thedatum.org` on 2026-10-15 UTC. Every archive member passed CRC and CSV parsing checks: 870 U and 200 M CSVs. The 350 U and 180 M evaluation files are **EXACT_BYTE_MATCH**, also matching parsed signal/label identities and prefix boundaries. All 82 files used by the 52-view/30-parent subset match. No format transform was required.

| Archive | Compressed bytes | Uncompressed bytes | SHA256 | Download completed (UTC) |
|---|---:|---:|---|---|
| TSB-AD-U.zip | 72900868 | 329554266 | `0c47020d3423723c70773736dbd800369f2b487328becbf339450d1ae5020961` | 2026-10-15T12:43:47.009681+00:00 |
| TSB-AD-M.zip | 540383983 | 2577892903 | `7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d` | 2026-10-15T12:45:39.939246+00:00 |

These are locally calculated acquisition hashes, not upstream-authenticated historical checksums. The original historical download archive identity and a signed/published upstream archive checksum remain unverified. Thus current content equality is established, but LEVEL 1 historical-version closure is not claimed. The release remains NOT_READY because data/derivative license scope and author licensing decisions are unresolved.

`manifests/public_current_official_snapshot.json` records the current archive snapshot; `manifests/official_evaluation_verification.csv` records all 530 per-file comparisons. Both archives extract under `TSB-AD-U/` or `TSB-AD-M/`; use those directories as the CLI roots. No signals or archives are included in this candidate.

The observed official default-branch commit is `ed74348e7876c9268b7a737c77f2f5f56f7fa458`; the historical list commit remains `6beac72e11d1155ade40870492c00d0d1cfdcaaf`. U/M official evaluation-list bytes agree between these commits. Package expanded-manifest U row order differs from official-list order while the filename set is identical; M order agrees. Discovery and verification use stable file identities rather than treating row order as a hidden match key. Neither Git commit is represented as a version label for the separately hosted signal archives.

## Data layout and parser contract

CSV input must preserve ordered numeric signal columns and one binary label column at the end. U has exactly one signal column; M has at least two. Source-family/domain, prefix boundary `tr`, and first-anomaly annotation are filename fields. Numeric source-instance IDs are track-local and are not external device identifiers. Evaluation uses `[0,T)` and the training prefix is `[0,tr)`; see `docs/MATCHING_PROTOCOL.md`.

## Rights

The seven matched source families are Daphnet, Exathlon, LTDB, MSL, SMAP, SMD, and SVDB. Their licenses are not interchangeable. TSB-AD's code and curation license is not blanket permission for original signals. See `docs/LICENSE_NOTES.md`; the package supplies manifests and frozen metric exports only, with final redistribution authorization still pending.

Original explanatory prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Official source names, URLs, file/archive hashes, underlying data and third-party rights are not newly licensed by this notice; see [LICENSING.md](LICENSING.md).
