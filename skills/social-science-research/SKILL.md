---
name: social-science-research
description: Plan auditable social-science research workflows with questions, theory, sampling, measurement, fieldwork, consent, qualitative/quantitative analysis, causal boundaries, preregistration, and reporting decisions. Use when users need a social-science study plan, survey/fieldwork protocol, sampling plan, measurement plan, mixed-methods workflow, or social-science reproducibility checklist.
---

# Social Science Research

Do not claim representativeness, causal identification, participant consent, field access, validity, or generalizability without corresponding design and evidence. This skill does not replace local ethics review, community governance, legal requirements, or disciplinary expertise.

## Initialize a study plan

```bash
python scripts/init_social_science_plan.py --out social-plan.json --question "Question" --design mixed-methods
```

The plan records theory, population/sampling, measurement, fieldwork, consent, analysis, preregistration, reflexivity and reporting decisions. It does not collect data or select participants.

## Workflow

1. Define the theoretical construct, unit of analysis, target population, sampling frame, recruitment/access constraints, and generalization boundary.
2. Document instrument/measurement validation, translation, pilot/cognitive testing, interview/observation protocols, positionality and fieldwork safety where relevant.
3. Pre-specify quantitative/qualitative analysis, missing data, causal claims, deviations, and data-access constraints.
4. Use `survey-and-psychometrics`, `qualitative-research-assistant`, `causal-inference-assistant`, `research-integrity-and-ethics`, and `research-data-management` for specialist artifacts.

## Resources

- `scripts/init_social_science_plan.py` — protected social-science study-planning scaffold.
