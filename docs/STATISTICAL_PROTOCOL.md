# Statistical protocol

## Input and contrast

The public frozen export contains 984 observations: 52 U views and 30 M parents, two tracks, conditions C/JC/LC/JLC, seeds 2000–2002, and six metrics. J is training Jitter, L is LSDP, C is CAC-only; M-C is final revised CAC without relative normalization. This diagnostic contrast is JLC−C and must not be labeled the main-table HA-PaAno−PaAno-Re improvement.

Per seed, subtract C from each U-view metric, average views equally within their M parent, and subtract the paired M condition difference to obtain H=U−M. Average the three seeds equally within each parent; point estimates then weight the 30 parents equally. The 52 views are not independent parent instances.

## Bootstrap

Use NumPy `default_rng(20260922)` / PCG64, 10,000 replicates. Draw seven source labels with replacement. Within each drawn source, draw its original number of parents with replacement. Concatenate drawn parent values and average; this is not equal-weight averaging of source means. Compute percentile limits using `quantile(method="linear")` at 0.025 and 0.975.

Retain one RNG stream over contrasts JC−C, LC−C, JLC−C, and within each contrast metrics VUS_PR, VUS_ROC, Range_F1, AUC_PR, AUC_ROC, Point_F1. All 18 slots are required to reproduce the historical Monte Carlo consumption. Reinitializing the RNG for the primary slot changes its interval. The script calculates statistics before reading the saved comparison reference.

## Reference and interpretation

U JLC−C=+0.009873219616343635; M JLC−C=−0.028851310533726547; H=+0.03872453015007018; H parent positive/negative/zero=17/13/0. The hierarchical 95% CI is [−0.01705001298510966,+0.10177953574410095]. Comparison tolerance is 1e-12; bitwise floating-point equality is not asserted.

The interval crosses zero. The resampled probability of a positive mean is not a separate significance-test p value. Uneven source counts and benchmark-internal selection limit interpretation; no causal channel effect, universal module preference, or independent OOD generality follows.

## Public metadata preparation

The public metric CSV omits `source_result_ref`, preserving every other original cell as its decimal string. Source logical IDs and SHA256 values remain. Sanitized JSON removes internal source paths; its public input hash is updated and the original export identity retained separately. No metric, parent effect, bootstrap reference value, or scientific algorithm is changed. See `manifests/public_copy_provenance.json`.

Original explanatory prose: Copyright (c) 2026 Peng Zhang, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain attribution/license notices and indicate changes. Numerical result values, separate statistical files and third-party rights are not newly licensed; see [LICENSING.md](../LICENSING.md).
