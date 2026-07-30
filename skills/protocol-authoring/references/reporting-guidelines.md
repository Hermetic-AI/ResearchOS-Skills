# Reporting Guidelines — Mapping, Checklists, and Registration

A study's design implies a reporting standard. `protocol_mapper.py` maps a
protocol to the most likely guideline with a heuristic score; the match must be
confirmed against the actual design and the governing standard before submission.

## Guideline selection

| Guideline | Study type | Primary registry / context |
|---|---|---|
| **CONSORT** | randomized parallel-group (and variant) trials | journal submission of trial results |
| **SPIRIT** | trial *protocols* (interventional) | protocol registration, journal protocols |
| **STROBE** | observational studies (cohort, case-control, cross-sectional) | journal submission of observational results |
| **PRISMA** | systematic reviews and meta-analyses | review registration (PROSPERO), journal submission |
| **ARRIVE** | animal / preclinical in vivo research | journal submission of animal work |

`protocol_mapper.py` scores each guideline by keyword hits in the declared
design (weighted 3x) plus a point per checklist item whose primary field is
populated. The highest score wins; ties keep the first match in the table above.

### When the mapping is ambiguous

- A *pilot* or *feasibility* trial usually still maps to CONSORT/SPIRIT but with
  a reduced checklist; note the pilot scope explicitly.
- A study with both an intervention and a long observational follow-up may need
  CONSORT for the intervention and STROBE for the observational component.
- Qualitative, simulation-only, and theoretical work is not covered by these
  checklists; map to the closest fit and document the deviation.

## Compliance checklist

For the matched guideline, `protocol_mapper.py` marks each item
`satisfied` / `partial` / `missing` based on whether the protocol fields that
satisfy it are populated. Treat the checklist as a *planning* aid:

- `missing` items are gaps to fill before registration or submission.
- `partial` items have some supporting content but need completion.
- `satisfied` items still require human verification — population of a field does
  not guarantee the content meets the guideline's intent.

Always cross-check the generated checklist against the official, versioned
checklist (CONSORT 2010, SPIRIT 2013, STROBE, PRISMA 2020, ARRIVE 2.0).

## Registration-ready summary

`protocol_mapper.py --registry` shapes populated protocol fields into the
structure a registry expects:

- **ClinicalTrials.gov**: `brief_title`, `study_type` (Interventional /
  Observational from the mapped guideline), `condition`, `intervention_name`,
  `primary_outcome`, `eligibility_criteria`.
- **OSF**: `title`, `description`, `category` (analysis for PRISMA, otherwise
  project), `tags` (guideline id + design).

The summary is a *draft*. It does not submit a registration, and every field must
be verified against the registry's current schema before submission.

## Minimum protocol content

Regardless of guideline, a registration-ready protocol should state:

1. Objectives and pre-specified hypotheses.
2. Population, eligibility, and recruitment source.
3. Allocation, blinding, and intervention/exposure definition.
4. Primary and secondary outcomes with estimands and measurement timing.
5. Sample-size evidence and the assumptions it depends on.
6. Analysis plan, missing-data strategy, and multiplicity handling.
7. Monitoring, stopping rules, and deviation handling.
8. Ethics, consent, privacy, data governance, and registration status.
