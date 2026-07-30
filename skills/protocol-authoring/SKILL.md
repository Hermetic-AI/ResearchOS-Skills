---
name: protocol-authoring
description: Create auditable research protocol planning artifacts with objectives, design, outcomes, eligibility, analysis, monitoring, ethics, registrations, and deviation tracking. Use when users need a study protocol, clinical protocol outline, preregistration-ready methods plan, protocol review, or amendment/deviation log.
---

# Protocol Authoring

Create a protocol that separates planned work from completed work. This skill does not grant ethical approval, register a study, or determine regulatory requirements; attach the governing source and institutional decision before making those claims.

## Initialize a protocol charter

```bash
python scripts/init_protocol.py --out protocol.json --title "Study title" --design "Randomized trial"
```

The output is a structured planning artifact with explicit uncertainty and deviation fields. Use `experiment-designer` for design details and `data-analysis-assistant` for analysis specification.

`python scripts/render_protocol_markdown.py protocol.json --out protocol.md` renders a structured charter for review, preserving missing sections as placeholders.

## Map to a reporting guideline and draft a registration

```bash
python scripts/protocol_mapper.py --protocol protocol.json --registry clinicaltrials.gov \
    --out protocol-mapping.json
```

Maps the declared study design to the most likely reporting guideline (CONSORT / SPIRIT / STROBE / PRISMA / ARRIVE) by scoring design keywords and populated fields, generates a compliance checklist for the matched guideline, and produces a registration-ready summary shaped for ClinicalTrials.gov or OSF (`--registry`). The mapping is heuristic — confirm the matched guideline against the actual design and the official checklist before submission. Read `references/reporting-guidelines.md` when selecting a guideline or preparing a registration.

## Minimum protocol workflow

1. State objectives, hypotheses, population, eligibility, outcomes, and estimands without implying results.
2. Define allocation, blinding, intervention/exposure, sample-size evidence, and stopping/monitoring rules where relevant.
3. Link analysis, missing-data, multiplicity, and sensitivity plans to versioned artifacts.
4. List consent, privacy, registration, data governance, safety, and amendment decisions with their evidence sources.

## Resources

- `scripts/init_protocol.py` — protected protocol and deviation-log scaffold.
- `scripts/protocol_mapper.py` — guideline mapping, compliance checklist, and registration-ready summary.
