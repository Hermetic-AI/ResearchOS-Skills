# Factor analysis, invariance, and IRT/Rasch

Psychometric validation is a program of evidence, not a single analysis. A high
alpha or a clean factor structure alone does not validate a scale.

## Exploratory factor analysis (EFA)

- **Extraction** — principal-factor (iterated communality) method. Start with
  squared-multiple-correlation communality estimates and iterate.
- **Rotation** — varimax (orthogonal) for interpretable, uncorrelated factors.
  Report the rotated loadings, communalities, and variance explained per
  factor.
- **Factor retention** — eigenvalues, scree, and parallel analysis. The script
  extracts a pre-specified number; justify it before fixing it.
- **Loadings** — flag cross-loadings and items with low communalities for
  review.

## Reliability

- **Cronbach's alpha** — internal consistency under tau-equivalence
  assumptions. Report item-total correlations and alpha-if-item-deleted.
- Alpha does not establish unidimensionality, validity, reliability for
  individual scores, or a universal adequacy threshold.

## Confirmatory factor analysis (CFA)

CFA tests a pre-specified factor structure with fit indices (CFI, RMSEA, SRMR).
This script implements EFA only; route CFA to a dedicated SEM tool and split or
replicate the sample.

## Measurement invariance

Test configural, metric, scalar, and strict invariance across groups/time
before comparing scores. Invariance testing is outside this script's scope.

## IRT / Rasch

- **Rasch (1PL)** — one item difficulty parameter, equal discrimination. The
  script fits a basic Rasch model via joint maximum likelihood on dichotomized
  items and reports item difficulty, person ability, and infit statistics.
- **IRT (2PL/3PL)** — extend to varying discrimination and guessing with a
  dedicated IRT package for publication-grade work.

## Boundaries

- Results depend on sample, item quality, and model assumptions.
- Do not reuse copyrighted instruments or claim validation without an
  appropriate sample and analysis.
- Split the sample for EFA/CFA or replicate on a holdout.
