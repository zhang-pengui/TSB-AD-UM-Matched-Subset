# Environment evidence

## Exact frozen validation environment

Python **3.12.14**, NumPy **2.3.5**, pandas **3.0.1**. `requirements.txt` pins the two non-standard-library dependencies to that verified environment. It is not a claim about minimum compatible versions. Scripts use Python's standard library plus NumPy/pandas; no model framework, evaluator, GPU, original project, or private module is required.

## Additional observed compatibility points

The following pre-existing CPU environments were tested independently as discrete points on the same machine:

| Python | NumPy | pandas | Observed validation |
|---|---|---|---|
| 3.11.15 | 2.3.2 | 2.3.1 | Inherited 34 tests, five core CLI help checks, all 984 metric rows / 18 bootstrap slots, official-current-cache 530-file discovery to 52/30 and pair verification |
| 3.12.7 | 1.26.4 | 2.2.2 | Same checks |

Both environments reparsed all 530 evaluation files with no differences from the pinned manifests in signal/label/interval/channel hashes, signal-column names, lengths, channel counts, or training boundaries. These checks support compatibility at the listed points, not an entire version interval. They used cached official inputs with established hashes; no new model evaluation was performed.

A separate user-reported check used NumPy 2.3.5 and pandas 2.2.3 and passed the inherited tests/statistics. That precise environment was **not reproduced in this run**; its Python version is unspecified. It must not be conflated with the locally tested pandas 2.2.2 point.

## Limits

No lowest supported Python version has been established. Python 3.11.15 passing does not establish support for every Python 3.11 release or older versions. No broad pandas/NumPy range, new operating system, or genuinely independent third-party machine has been certified. Retain the exact pins for the primary reproducibility target and record actual versions when testing another environment.

The release gate uses only the standard library. Its tests add synthetic policy fixtures to the inherited suite; these never grant real publication permission. Command parameters are documented in `README.md` and can be checked with each script's `--help`.

Original prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Third-party names, terms and underlying factual information retain their status; see [LICENSING.md](../LICENSING.md).
