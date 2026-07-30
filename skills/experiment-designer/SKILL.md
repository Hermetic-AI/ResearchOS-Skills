---
name: experiment-designer
description: Design studies before data collection by selecting randomized, blocked, factorial, response-surface, crossover, split-plot, or within-subject designs; creating preregistration and statistical analysis plan packages; planning controls, reproducible allocation, power and sample size; reviewing validity threats; and planning ML baselines, ablations, seeds, budgets, and leakage checks. Use for 帮我设计实验方案, 预注册, 统计分析计划, SAP, 实验分组, 对照组, 随机分组, 区组, 分层随机, 样本量, 功效分析, DOE, 因子设计, 消融实验, baseline, benchmark泄漏, or how should I set up this study. Not for analysis after data collection (data-analysis-assistant), literature reading, manuscript writing, knowledge graphs, or reproducing an existing experiment.
---

# Experiment Designer

Helps plan experiments **before** any data is collected. No analysis can rescue a confounded or pseudoreplicated design after the fact — the decisions made here (what is randomized, what is controlled, at what level units replicate) determine what the data can ever answer.

> **NOT for literature surveys, paper reading, or manuscript writing** — this skill is for empirical experiment design only. Use literature-reader / paper-writing-assistant for those.

Capabilities, use independently or in sequence:

1. **Design recommendation** — pick the right design type (CRD, randomized block, full/fractional factorial, response surface, Latin square, crossover, split-plot) and the control groups.
2. **Factor-space exploration** — enumerate, fractionate, or response-surface the factor combinations to run, with alias, rank, estimability, conditioning, and D-efficiency diagnostics.
3. **Control-group design** — negative/positive/vehicle/sham controls, what each isolates.
4. **Randomization, blocking & stratification** — reproducible allocation schedules with fixed seeds.
5. **Power / sample-size estimation** — a priori n for t-tests (independent / one-sample / paired), two-proportion, and correlation tests; standardized noninferiority/equivalence; cluster and attrition inflation.
6. **ML/AI experiment planning** — baseline discipline, ablation matrices, hyperparameter search budgets, seed replication, benchmark-leakage checks, compute-budget reporting.
7. **Validity review** — systematic check of internal / external / construct / statistical-conclusion validity threats before sign-off.
8. **Preregistration and SAP package** — render schema-valid design/analysis artifacts, reviewable Markdown, freeze gates, provenance, and checksums from one structured specification.
9. **Multiple endpoints and adaptive monitoring** — allocate confirmatory alpha, plan interim information fractions and spending budgets, and audit stopping/adaptation prespecification.
10. **Longitudinal and survival sizing** — screen repeated-mean, linear-slope, and proportional-hazards event requirements with explicit assumptions and limitations.

**Global conventions**
- **User-facing reports in Chinese**; content written into artifacts (design briefs, CSV/JSON run sheets) follows the artifact's language.
- **Never invent numbers.** Effect sizes, baseline rates, and nuisance factors come from the user, pilot data, or literature — surface uncertainty instead of guessing.
- **Seeded and auditable.** Every generated schedule/design carries its seed so it can be archived, regenerated, and pre-registered.
- **Pre-data artifact boundary.** For reusable projects, read `references/artifact-contracts.md`; write a `design-brief` and confirmed `analysis-plan` before data collection, and record later deviations rather than silently changing the plan.

## When to use / not use

Use when the user is planning a study and mentions any of: 实验设计, 对照组, 随机分组, 区组, 分层随机, 样本量, 功效分析, 因子设计, DOE, 响应面, 交叉设计, 被试内, 消融实验, baseline 选择, 超参数搜索, benchmark 泄漏, 效度威胁, "how many samples do I need", "how to avoid confounding", "assign subjects to groups", "is my benchmark evaluation valid".

Not for: statistical analysis of collected data (→ data-analysis-assistant), paper writing/formatting (→ paper-writing-assistant), literature reading (→ literature-reader), knowledge graphs (→ knowledge-graph-builder), reproducing an existing published experiment (→ reproduction-assistant).

## Workflow

Follow these steps in order; skip any the user has already settled. **Do not read all references up front** — read each only when its step is reached.

1. **Build the design brief.** Walk the user through the 5-segment interview (hypothesis → variables → treatments & controls → sample & randomization → measurement & analysis plan). Read `references/design-brief.md` for the question template and the brief file format. If the user can't answer a segment, mark it `_TODO_` and move on — do not fabricate.
2. **Recommend a design type.** From the brief, choose: completely randomized vs. randomized block (known nuisance factor?), full vs. fractional factorial (how many factors, interactions needed?), response surface (optimizing, curvature matters?), Latin square / crossover (two blocking factors, repeated measures?), split-plot (hard-to-change factor?), within- vs between-subject. Read `references/design-types.md` for the selection guide, control-design principles, and pitfalls — check the user's plan against them explicitly. **ML/AI experiments:** if the unit is a model/training run, read `references/ml-experiments.md` instead for baseline discipline, hyperparameter budgets, seeds, and the leakage checklist.
3. **Generate and audit the factor layout** (multi-factor experiments): run `scripts/doe_designs.py` (requires numpy — `pip install numpy`). Full/fractional factorial, Box-Behnken, central composite, or Latin square run sheets use real units and a seeded run order. Read `references/doe-diagnostics.md`; reject a design that cannot estimate a required effect or aliases it with a scientifically plausible effect. **Ablation matrices:** run `scripts/ablation_planner.py` (zero dependencies) for leave-one-out / full / cumulative ablation run matrices.
4. **Generate the allocation schedule**: run `scripts/randomization.py` (zero dependencies) for complete, permuted-block, or stratified (`--strata`) randomization with a fixed seed.
5. **Estimate and validate sample size / power**: run `scripts/power_analysis.py` (zero dependencies, normal approximation) for two-sample / one-sample / paired t-tests, two proportions, or correlations. For noninferiority, equivalence, cluster randomization, or attrition inflation, first read `references/noninferiority-equivalence-and-clusters.md`. For repeated measurements, longitudinal slopes, or survival endpoints, read `references/longitudinal-and-survival-power.md` and run `scripts/longitudinal_power.py`. Before final sign-off, read `references/power-validation.md` and cross-check with a method aligned to the planned analysis; maintainers can run `scripts/validate_power_calculations.py`. Always report a sensitivity range over plausible assumptions—not a single n; warn against post-hoc ("observed") power.
6. **Review validity, then write the plan.** Read `references/threats-to-validity.md` and walk the design through the four-validity checklist (internal / statistical-conclusion / construct / external); mark each threat addressed, accepted-with-justification, or fatal. Then summarize the design brief + chosen design + schedule + power justification (in Chinese) for the user to confirm before any data collection.
7. **Plan multiplicity and adaptations when applicable.** For multiple confirmatory endpoints, outcome-data interim looks, stopping, or adaptation, read `references/multiple-endpoints-and-adaptive-designs.md` and run `scripts/plan_sequential_design.py`. Treat emitted alpha spending as a budget, not a calibrated statistical boundary; complex operating characteristics require design-specific software or simulation.
8. **Create the preregistration package.** Read `references/preregistration-and-sap.md`, encode the confirmed decisions in one study-spec JSON, and run `scripts/create_preregistration.py`. Keep unresolved decisions as `_TODO_`; use `--freeze` only before outcome access and only when the package has no unresolved items. Treat checksums as an audit aid, not proof of external registration.

## Script usage

```bash
# Factorial / response-surface / Latin square sheets (numpy required)
python scripts/doe_designs.py --design full  --factors factors.json --seed 42 --out runs.csv
python scripts/doe_designs.py --design frac2k --factors factors.json --generators "d=ab" --seed 42 --out runs.json
python scripts/doe_designs.py --design boxbehnken --factors factors3.json --seed 42
python scripts/doe_designs.py --design ccd --factors factors3.json --alpha face --seed 42
python scripts/doe_designs.py --design latin --factors-json '{"dose_mg":[0,10,50]}' --seed 42

# Ablation run matrix (stdlib only)
python scripts/ablation_planner.py --mode loo --components encoder,pretrain,augment --seed 42

# Randomization (stdlib only)
python scripts/randomization.py complete   --n 60 --arms treatment,control --seed 42
python scripts/randomization.py block      --n 60 --arms drug,placebo --ratio 2:1 --block-size 6 --seed 42
python scripts/randomization.py stratified --strata male:30,female:30 --arms t,c --seed 42

# Power / sample size (stdlib only)
python scripts/power_analysis.py --test t_ind    --solve n     --effect-size 0.5 --power 0.8
python scripts/power_analysis.py --test t_paired --solve n     --effect-size 0.5 --power 0.9
python scripts/power_analysis.py --test corr     --solve n     --effect-size 0.3
python scripts/power_analysis.py --test two_prop --solve power --p1 0.40 --p2 0.55 --n 80
python scripts/power_analysis.py --test t_ind --solve n --hypothesis equivalence --effect-size 0 --margin 0.30 --power 0.90
python scripts/power_analysis.py --test t_ind --solve n --effect-size 0.40 --cluster-size 20 --icc 0.04 --cluster-cv 0.30 --dropout 0.15
python scripts/longitudinal_power.py repeated-mean --effect-size 0.40 --measurements 4 --correlation 0.50 --dropout 0.15
python scripts/longitudinal_power.py longitudinal-slope --slope-effect 0.10 --times 0,1,3,6 --correlation 0.50
python scripts/longitudinal_power.py survival --hazard-ratio 0.70 --event-probability 0.60 --power 0.90
python scripts/validate_power_calculations.py --out power-validation.json  # requires .[validation]

# Registry-neutral preregistration + statistical analysis plan package
python scripts/create_preregistration.py --input study.json --out-dir prereg-draft
python scripts/create_preregistration.py --input study.json --out-dir prereg-v1 --protocol-version 1.0.0 --freeze

# Multiple endpoints, alpha spending, stopping, and prespecified adaptation
python scripts/plan_sequential_design.py --input sequential.json --out sequential-design-plan.json
```

All scripts print structured JSON to stdout by default (CSV where a table is the natural output); `--help` lists every option. All randomness takes `--seed`.

## File index

- `references/design-brief.md` — 5-segment interview template that produces a design brief. Read at workflow step 1.
- `references/design-types.md` — design-type selection guide (CRD, RBD, factorial, response surface, Latin square, crossover, split-plot, within- vs between-subject), control-group principles, pitfalls. Read only when choosing or reviewing a design.
- `references/ml-experiments.md` — ML/AI experiment design: baseline discipline, ablation design, hyperparameter search budgets, seeds & variance, benchmark-leakage checklist, compute-budget reporting. Read when the experimental unit is a model or training run.
- `references/threats-to-validity.md` — internal / external / construct / statistical-conclusion validity threats, countermeasures, and the design-stage sign-off checklist. Read at the review step before plan sign-off.
- `references/artifact-contracts.md` — `research-gap`/`paper-note` inputs and `design-brief`/`analysis-plan` output contracts. Read for cross-skill projects.
- `references/preregistration-and-sap.md` — source-spec fields, draft/freeze rules, amendment policy, and package validation. Read before creating a preregistration package.
- `references/multiple-endpoints-and-adaptive-designs.md` — endpoint families, alpha spending, stop/adaptation prespecification, limitations, and primary sources.
- `references/noninferiority-equivalence-and-clusters.md` — margin semantics, TOST, cluster design effects, attrition order, and limitations.
- `references/longitudinal-and-survival-power.md` — repeated-mean, linear-slope, and event-driven survival assumptions, formulas, examples, and sources.
- `references/doe-diagnostics.md` — model rank, residual degrees of freedom, alias groups, estimability, conditioning, and comparable-use limits for D-efficiency.
- `references/power-validation.md` — SciPy/Statsmodels reference grid, observed approximation errors, acceptance limits, and uncovered methods.
- `scripts/doe_designs.py` — full/fractional factorial, Box-Behnken, central composite, and Latin square generator with DOE diagnostics (numpy); seeded; CSV/JSON.
- `scripts/ablation_planner.py` — ablation experiment matrices: leave-one-out, full 2^k−1, cumulative add-one (stdlib only); seeded run order.
- `scripts/randomization.py` — complete, permuted-block, and stratified randomization (stdlib only); seeded allocation tables.
- `scripts/power_analysis.py` — sample size / power / MDE, noninferiority/equivalence, and cluster/dropout inflation (stdlib only, normal approximation).
- `scripts/create_preregistration.py` — zero-dependency generator for design brief, analysis plan, human-readable preregistration/SAP, and checksum manifest.
- `scripts/plan_sequential_design.py` — zero-dependency multiplicity allocation, alpha-spending budget, stopping-rule, and adaptation audit generator.
- `scripts/longitudinal_power.py` — zero-dependency screening approximations for repeated means, longitudinal slopes, and log-rank event counts.
- `scripts/validate_power_calculations.py` — optional SciPy/Statsmodels numerical cross-validation with a machine-readable case report.

## Related skills

- **data-analysis-assistant** — analysis after data collection.
- **paper-writing-assistant** — writing and checking the manuscript.
- **literature-reader** — extracting prior effect sizes / baseline rates from papers (feed them into step 5).
- **reproduction-assistant** — reproducing someone else's existing experiment.
- **knowledge-graph-builder** — structuring concepts/relations, not experiment planning.
