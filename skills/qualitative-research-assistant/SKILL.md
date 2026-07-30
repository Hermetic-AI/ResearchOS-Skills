---
name: qualitative-research-assistant
description: Plan auditable qualitative research workflows for interviews, observations, documents, codebooks, thematic analysis, coder agreement, saturation, reflexivity, and audit trails. Use when users ask to design qualitative coding, build a codebook, analyze interview transcripts, assess coding agreement, document saturation, or prepare a thematic-analysis audit trail.
---

# Qualitative Research Assistant

Treat interpretation as a documented human analytic process. Do not infer participant meaning from metadata, fabricate quotations, erase divergent cases, or present AI suggestions as coded findings.

## Initialize a codebook

```bash
python scripts/init_codebook.py --out codebook.json --study "Study title" --approach thematic-analysis
```

The draft codebook records code definitions, inclusion/exclusion rules, examples, coder decisions, reflexivity, negative cases, saturation, and agreement plan. Add codes only after reviewing source material.

## Validate a coding audit trail

```bash
python scripts/validate_coding_log.py --codebook codebook.json --log coding-log.json --out coding-audit.json
```

Each entry needs the source ID, location, code, coder and rationale. The validator only checks audit-record completeness and codebook membership; it never evaluates participant meaning or coding quality.

## Workflow

1. Confirm consent, de-identification, access controls, transcription accuracy, and unit of analysis.
2. Choose deductive/inductive/hybrid coding and preserve a dated codebook version.
3. Keep source location, coder, rationale, and disagreement resolution for every coded segment.
4. Treat agreement statistics as one quality signal, not proof of validity; report reflexivity and disconfirming cases.
5. Stop at a defensible saturation rationale, not a target count alone.

`python scripts/coding_agreement.py coding.csv --coder-a coder1 --coder-b coder2` computes nominal Cohen's κ for one pre-specified code per item and reports unpaired items; it does not replace adjudication or validity analysis.

`python scripts/saturation_trace.py coding-log.json --source-order i1,i2,i3` reports manually ordered new-code accumulation; it never declares saturation.

## Saturation and agreement

```bash
python scripts/saturation.py --mode saturation --log coding-log.json --threshold 0.05 --out saturation.json
python scripts/saturation.py --mode alpha --data data.json --level nominal --out alpha.json
```

`--mode saturation` tracks new-code accumulation across rounds and reports when
the new-code rate drops below a threshold (descriptive only). `--mode alpha`
computes Krippendorff's alpha for nominal/ordinal/interval/ratio data with
missing values.

## Resources

- `scripts/saturation.py` — team saturation curves and Krippendorff's alpha.
- `references/saturation-and-agreement.md` — saturation judgment and coder agreement rules.
- `scripts/init_codebook.py` — protected qualitative codebook and audit-trail scaffold.
