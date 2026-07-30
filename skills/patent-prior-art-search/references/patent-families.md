# Patent Families — Timelines, Overlap, and Prior-Art Ranking

A patent family groups filings that share one or more priority claims. Mapping the
family is the first step in a prior-art assessment: it reveals the earliest
priority date, the jurisdictions covered, the prosecution timeline, and which
members are closest to the target invention. `patent_family.py` computes these
signals; it is research support, not a legal conclusion.

## Family structure

- **Priority claim**: the first filing date a member asserts. The family's
  effective priority is the earliest of these across all members.
- **Members**: the national/regional filings (provisional, PCT, national-stage,
  continuation, divisional) that claim that priority.
- **Family tree**: members ordered by filing date, showing how the invention
  propagated across jurisdictions and time.

`patent_family.py` accepts a `prior-art-search-ledger` (with `patent_records`
and `family_links`) or a dedicated `{"families": [...]}` file. Records not
attached to any `family_link` become singleton families.

## Timeline computation

For each family the script reports:

- `earliest_priority`: the oldest priority date in the family.
- `latest_filing`: the most recent filing date.
- `latest_publication`: the most recent publication/grant date.
- `family_span_days`: days between earliest priority and latest filing.
- `jurisdictions` and `statuses`: the coverage and prosecution state.

These dates are the factual backbone of a priority argument; verify every date
against the official register, because source data entry errors are common.

## Closest prior art by date and claims

`patent_family.py` ranks every family member as a candidate prior art against a
target, given a cutoff date (the target's priority/filing date) and, optionally,
the target's claims:

1. Only members with a priority/filing date **on or before the cutoff** are
   candidates — later filings cannot be prior art to the target.
2. Candidates are scored by:
   - **date proximity**: days before the cutoff (closer in time is stronger).
   - **claims overlap**: Jaccard similarity of the lowercased alphanumeric token
     sets of the target claims and the member's claims.
3. The score combines both (`days/365 + overlap*10`); candidates sort best-first.

The top candidate is reported as `closest_prior_art`.

### Limits of claims-token overlap

Token overlap is a crude proxy. It ignores claim structure, dependency,
construction of terms, and the legal standard of anticipation/obviousness. A high
token overlap may be legally irrelevant; a low overlap may still anticipate.
Treat the ranking as a *triage* signal for counsel, never as a conclusion.

## Family tree visualization

Two renderings are produced:

- **Text tree**: indented, ordered by filing date — quick to read in a terminal
  or email.
- **Mermaid flowchart** (`--mermaid-out`): a `flowchart TD` with one node per
  member and date-ordered edges — paste into any Mermaid renderer.

## Escalation rule

Every output of `patent_family.py` carries the warning that it is not a legal
analysis. Before any novelty, freedom-to-operate, or patentability statement, the
ranking and the underlying records must be reviewed by a qualified patent
attorney or search professional.
