# Strict matching protocol

## Fixed universe, not a selected success list

All 350 U and 180 M evaluation files are inventoried before model metrics are read. Every one of the 5,244 M channels is indexed. Discovery accepts no performance table or historical pair list. Historical reconciliation is a subsequent set comparison; the current reconstruction does not imply historical preregistration.

## Exactness contract

The unchanged `scripts/matching_core.py` specifies `tsbad-position-exact-v1;pandas-c-default;float64`. CSV values are parsed by the pandas C parser and represented as float64. Hashing includes shape and little-endian float64 bytes, with positive/negative zero encoded consistently. This is exact equality under the named parser, not a claim that every CSV textual representation is identical.

NaN/Inf, nonbinary labels, repeated raw column names, suspicious timestamp/metadata signal columns, and wrong track column counts are rejected. Labels must be the unique final column; U has one signal column and M at least two. No rounding, tolerance, affine adjustment, normalization, interpolation, correlation, or DTW is used.

For each U signal, the `(length,signal_hash)` index provides candidate M channels. Source files are reopened and signal arrays compared elementwise. Labels, closed anomaly intervals, `[0,tr)` training prefix, `[0,T)` evaluation range, source/domain annotation, and first-anomaly consistency must also pass. Hash indexing alone does not establish a pair.

## Ambiguity and identity

All exact-signal candidates are retained. Multiple admissible parents, multiple M channels, or competing U files for one M channel are explicit ambiguities, not opportunities to take the first sorted result. Multiple distinct U channels belonging to the same M parent can be retained and are aggregated within parent for statistics.

There are 216 candidate rows: 52 strict, 161 ambiguous, and 3 rejected. Ambiguity involves 27 U files; three other U files have rejected candidates; 268 have no exact-signal candidate. All these units differ from the count of candidate rows. A known unmatched WSD filename-first-anomaly conflict is quarantined, not corrected.

The inferred relation is a benchmark-internal channel/parent relation with **position-index alignment**. No true timestamp, external physical collection identity, or shared U/M device ID is independently established. Filename source IDs are track-local; identical numeric IDs are not a matching prerequisite.

## Verification scope

`verify_dataset.py` checks the pinned universe's bytes and headers. `verify_pairs.py` reopens and verifies the supplied strict mapping. Only full-universe `discover_pairs.py` addresses uniqueness among all candidates. Pair IDs need not match old string lengths; the stable relation key is `(u_relative_path,m_relative_path,m_channel_index)`.

Original prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Underlying data and third-party expressions are excluded; see [LICENSING.md](../LICENSING.md).
