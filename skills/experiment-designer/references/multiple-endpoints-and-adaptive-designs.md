# Multiple endpoints, sequential monitoring, and adaptive designs

Use this resource when a design has multiple confirmatory claims, interim outcome looks, early stopping, or prospectively planned adaptations. It is a planning and audit aid, not a substitute for design-specific statistical validation or regulatory advice.

## Minimum decisions before enrollment

1. Identify every confirmatory endpoint and hypothesis, including direction, timepoint, analysis population, and estimand. Label all others exploratory.
2. State the family of claims whose Type I error is controlled, the family alpha, sidedness, and multiplicity procedure. Do not add a confirmatory endpoint after seeing results.
3. Define interim looks by information fraction rather than calendar date alone. Identify who sees unblinded comparative data and who has authority to stop or adapt.
4. For every efficacy, futility, or safety stop, specify the decision statistic/rule, whether a futility rule is binding, and the decision authority. A Data Monitoring Committee recommendation and an automatic statistical boundary are not interchangeable.
5. For every adaptation, predefine its type, timing, data scope, decision rule, inferential adjustment, and operational firewall. Include a simulation plan for complex adaptations.

These controls reflect the FDA principle that adaptations be prospectively planned while trial validity and integrity are preserved, and the ACE reporting definition of pre-planned opportunities to modify a trial using accumulating data.

## Supported deterministic planning

`scripts/plan_sequential_design.py` supports:

- equal or weighted Bonferroni endpoint allocation;
- Holm ordered-testing thresholds;
- Lan-DeMets-style O'Brien–Fleming or Pocock cumulative alpha-spending budgets at prespecified information fractions;
- structured efficacy, futility, and safety decision rules;
- prespecification completeness checks for adaptations.

The generated alpha values are **spending budgets, not calibrated test-statistic boundaries**. Correlation across looks/endpoints, information drift, sample-size re-estimation, population selection, arm dropping, response-adaptive randomization, and combination tests require fit-for-purpose software or simulation. Preserve the simulation code, seeds, scenarios, and operating-characteristic acceptance criteria.

## Input example

```json
{
  "study_id": "study-001",
  "family_alpha": 0.05,
  "sidedness": "two-sided",
  "multiplicity": {"method": "weighted-bonferroni"},
  "endpoints": [
    {"id": "primary-score", "role": "primary", "weight": 0.8},
    {"id": "key-secondary", "role": "key-secondary", "weight": 0.2}
  ],
  "sequential": {
    "spending": "obrien-fleming",
    "information_fractions": [0.5, 0.75, 1.0]
  },
  "stopping_rules": {
    "efficacy": {"decision_rule": "use validated endpoint-specific efficacy boundaries", "authority": "independent monitoring committee"},
    "futility": {"decision_rule": "nonbinding conditional-power rule defined in the protocol", "authority": "independent monitoring committee", "binding": false}
  },
  "adaptations": [{
    "id": "ssr-1",
    "type": "blinded sample-size re-estimation",
    "timing": "50% information",
    "decision_rule": "protocol-defined nuisance-variance rule",
    "data_scope": "blinded pooled variance",
    "inference_adjustment": "not required under the prespecified blinded rule; validate assumptions",
    "operational_firewall": "independent statistician returns sample-size decision only"
  }],
  "simulation_plan": "Evaluate Type I error, power, expected and maximum sample size, adaptation frequency, and bias across prespecified scenarios."
}
```

```bash
python scripts/plan_sequential_design.py --input sequential.json --out sequential-design-plan.json
python tools/validate_artifact.py sequential-design-plan.json --type sequential-design-plan
```

## Source basis

- FDA, *Adaptive Designs for Clinical Trials of Drugs and Biologics: Guidance for Industry* (2019): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/adaptive-design-clinical-trials-drugs-and-biologics-guidance-industry
- EMA, *Points to Consider on Multiplicity Issues in Clinical Trials*: https://www.ema.europa.eu/en/multiplicity-issues-clinical-trials-scientific-guideline
- Dimairo et al., *Adaptive designs CONSORT Extension (ACE)*, BMJ 2020;369:m115: https://doi.org/10.1136/bmj.m115
- DeMets and Lan, *Interim analysis: the alpha spending function approach*, Statistics in Medicine 1994;13:1341–1352: https://doi.org/10.1002/sim.4780131308
