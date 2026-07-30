# Threats to Validity — Design-Stage Checklist

Read this at workflow step 2 (design review) or step 6 (plan sign-off). Validity questions are settled at design time: no analysis can add back a control group or un-confound a variable. The four-validity framework below (Campbell 1957; Cook & Campbell 1979; Shadish, Cook & Campbell 2002) names each threat, its signature, and the design move that neutralizes it. Walk the plan through every checklist row; mark each as addressed, accepted-with-justification, or a fatal flaw to fix.

## Internal validity — is the observed difference actually caused by the treatment?

| Threat | Signature | Design-stage countermeasure |
|---|---|---|
| Confounding | Treatment aligns with another variable (day, batch, site) | Randomize across, or block on, every nameable nuisance factor |
| Selection bias | Groups differ at baseline (self-selection, convenience assignment) | Seeded random allocation; check baseline balance; stratify on prognostic covariates |
| History | External event co-occurs with treatment | Concurrent (never historical) controls run in the same window |
| Maturation / spontaneous change | Units change on their own over time | Negative control; within-subject pre/post with control arm |
| Regression to the mean | Units selected BECAUSE extreme (worst patients enrolled) | Randomize within the selected extreme group; expect drift toward mean in both arms |
| Attrition | Dropout differs by arm | Pre-fixed missing-data plan; worst-case sensitivity bounds; dropout-inflated enrollment (see `--dropout` in power_analysis.py) |
| Instrumentation drift | Measurement device/rater changes over time | Recalibration schedule; interleave conditions across measurement sessions; blinded raters |
| Diffusion / contamination | Control units get the treatment (spillover, shared equipment) | Physical separation; cluster randomization at the spillover boundary |
| Experimenter / observer bias | Raters unconsciously favor a condition | Allocation concealment + blinded measurement; automate endpoints where possible |

Checkpoint: *name the three most plausible alternative explanations for your expected result, and identify which control or randomization step kills each one.*

## Statistical conclusion validity — is the statistical inference itself sound?

| Threat | Signature | Design-stage countermeasure |
|---|---|---|
| Low power | Real effect missed; null result uninterpretable | A priori power analysis (`scripts/power_analysis.py`); report the MDE, not just n |
| Pseudoreplication | Repeated measures of one unit counted as replicates | Replicate at the level the treatment is applied (n = mice, not cells) |
| Multiple comparisons | 20 endpoints → one "significant" by chance | Pre-specify ONE primary endpoint; correction plan (Bonferroni/FDR) for the rest |
| Violated assumptions | t-test on skewed small samples; independence violated by clustering | Plan the analysis to match the design (blocks/strata/clusters in the model) or pre-specify a robust/nonparametric alternative |
| Fishing / HARKing | Analysis chosen after seeing data; hypothesis invented post hoc | Pre-register hypotheses, endpoints, and analysis code before data collection |
| Unreliable measurement | Noisy endpoint shrinks detectable effects | Estimate measurement reliability up front; average repeated measures; fix the instrument before the sample size |

Checkpoint: *write the primary analysis as one sentence — "test T on endpoint E comparing arms A vs B with covariates C" — before any data exists.*

## Construct validity — do your operations actually instantiate the concepts?

| Threat | Signature | Design-stage countermeasure |
|---|---|---|
| Proxy mismatch | Measuring a proxy instead of the construct (test score for "learning", accuracy for "understanding") | State the construct→operation mapping explicitly; justify the proxy or add a convergent measure |
| Mono-operation bias | One manipulation, one measure, one setting | Multiple operationalizations of key constructs where feasible |
| Inadequate manipulation | Treatment too weak to instantiate the construct | Manipulation check (did the independent variable actually change?) built into the protocol |
| Demand characteristics / expectancy | Participants or raters infer the hypothesis and comply | Blinding; cover story; unobtrusive measures |
| Confounded constructs | "Treatment" bundles several constructs (drug + extra attention) | Additive control arms that strip one component at a time (vehicle, sham) |
| Level-of-measurement error | Construct defined at one level, measured at another (team construct, individual survey) | Align construct, treatment, measurement, and unit of analysis |

Checkpoint: *for each key variable, finish the sentence "by CONSTRUCT we operationally mean MEASURE, and the main way these could diverge is …".*

## External validity — to whom, where, and when does the result generalize?

| Threat | Signature | Design-stage countermeasure |
|---|---|---|
| Population restriction | Convenience sample (WEIRD undergrads, one cell line, one hospital) | Define the target population FIRST; sample representatively or state the restriction as the claim's scope |
| Setting artifacts | Lab conditions nothing like deployment | Field replication or ecologically valid conditions for the final confirmatory run |
| Interaction of selection × treatment | Effect only in the sampled subpopulation | Stratify enrollment across the moderating variable; report subgroup heterogeneity |
| Time-dependence | Result tied to a cohort, season, or model version | Replicate across cohorts/time points; state the temporal scope of the claim |
| Treatment variation | Effect depends on exact dose/protocol | Sample across treatment variants (factorial over protocol parameters) |

Checkpoint: *state the claim's scope in one sentence — population, setting, treatment range — and confirm the sampling plan actually covers it. Narrow claims honestly stated beat broad claims silently unsupported.*

## How the four validities trade off

- Internal vs. external: tight lab control buys internal validity at the price of ecological realism. Standard resolution: establish the causal effect under tight control, then run ONE confirmatory study under realistic conditions.
- Construct vs. internal: blinding and sham controls protect both; skipping them is the most common joint failure.
- Statistical conclusion validity gates everything: an underpowered study answers none of the other three questions.

## Design-stage sign-off checklist

- [ ] Three alternative explanations named, each killed by a control or randomization step
- [ ] Allocation seeded, concealed, and archived
- [ ] Primary endpoint + primary analysis pre-specified (one sentence)
- [ ] A priori power/MDE reported over a plausible effect-size range
- [ ] Construct→measure mapping stated for every key variable
- [ ] Claim scope (population/setting/time) stated and matched by sampling
- [ ] Dropout, exclusion, and missing-data rules fixed in advance
