# Limitations

- This is a matched subset inside TSB-AD, not a new independent dataset or OOD benchmark.
- Array equality establishes position-index alignment under one explicit CSV parser; it does not independently establish timestamps, physical-device identity, or unrecorded upstream processing.
- Current official archive contents match all 530 frozen evaluation inputs exactly (LEVEL 2), including all 82 matched-subset files. This is separate from historical archive identity: the original download archive and an upstream-authenticated historical checksum remain unverified. No LEVEL 1 historical-version claim is made.
- No tolerance or preprocessing repair is used to hide version mismatches. One unpaired WSD annotation conflict remains visible.
- The 161 ambiguous candidate rows remain unresolved. The strict subset is not the entire U/M population.
- Current discovery is model-metric independent; that does not establish historical preregistration or exclude all historical selection bias.
- The 52 U views are clustered within 30 parents and seven unevenly represented sources. Parent aggregation and hierarchical resampling address specific dependence, not every confounder.
- The principal CI crosses zero. Descriptive directional means cannot establish causal module preferences or universal benefit.
- Frozen metric reproduction does not reproduce model training or anomaly-score generation. Those components are not included.
- A same-machine relocated smoke test is not verification by an independent third party.
- Data terms, derivative-material rights, code licensing, and author approval remain distinct from automated file-content scanning. Absence of regex findings is not a legal or privacy guarantee.

Original prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Underlying factual results and third-party rights are not newly licensed; see [LICENSING.md](../LICENSING.md).
