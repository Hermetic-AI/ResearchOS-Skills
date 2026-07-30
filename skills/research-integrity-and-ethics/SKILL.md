---
name: research-integrity-and-ethics
description: Prepare auditable research ethics, privacy, authorship, AI-disclosure, integrity, and reporting checklists. Use when users need an IRB/ethics readiness checklist, data privacy review, authorship contribution plan, AI-use disclosure, conflict-of-interest reminder, research-integrity audit, or reporting-guideline routing. Not for legal advice, ethics-board approval, or replacing institutional policy.
---

# Research Integrity and Ethics

This skill identifies decisions and evidence to document; it never grants approval or legal clearance. Follow the stricter applicable institutional, funder, journal, and jurisdictional rule.

## Create a readiness checklist

```bash
python scripts/ethics_checklist.py --study "Study title" --human-data --ai-use --out ethics-checklist.json
```

The output records required confirmations for human/animal data, privacy, consent, data sharing, authorship, conflicts, AI use, preregistration, and reporting. Existing outputs require explicit `--force`.

## Create a submission disclosure record

```bash
python scripts/init_disclosure_record.py --manuscript "Manuscript title" --out disclosures.json
```

This creates placeholders for contributor-confirmed CRediT-style roles, conflicts, funding, AI use, data/code availability and approval evidence. It never infers disclosures from manuscript text.

## Required boundaries

- Do not collect identifiable or sensitive data until the applicable approval/exemption and consent basis are documented.
- Do not de-identify by deleting only names; evaluate direct/indirect identifiers, linkage risk, access controls, retention, and sharing agreements.
- Use authorship criteria and contribution records prospectively; never fabricate author contributions or approvals.
- Disclose material AI assistance according to the venue policy; humans remain responsible for verification, citations, analyses, and final text.

`python scripts/audit_policy_coverage.py disclosures.json policy-map.json` checks a user-supplied policy field map against a disclosure record. It is a coverage screen, not policy interpretation or approval.

## Resources

- `scripts/ethics_checklist.py` — draft readiness checklist, not approval.
