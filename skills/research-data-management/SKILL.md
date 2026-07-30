---
name: research-data-management
description: Create auditable data-management plans covering data inventory, sensitivity classification, metadata, FAIR readiness, access, retention, licensing, sharing, and preservation decisions. Use when users need a DMP, data governance plan, FAIR checklist, data release plan, anonymization planning, or research-data archive plan.
---

# Research Data Management

This skill plans governance; it does not anonymize data, grant access, publish data, or make legal/ethics determinations. Never include secrets, direct identifiers, or controlled data in planning artifacts.

## Initialize a DMP

```bash
python scripts/init_dmp.py --out dmp.json --project "Project name" --owner "Responsible role"
```

The resulting artifact records data categories and classification decisions, metadata/FAIR plans, access controls, retention, sharing and preservation decisions. Its warnings remain until an authorized policy and repository are attached.

## Screen release readiness

```bash
python scripts/release_readiness.py --dmp dmp.json --out release-readiness.json
```

The screen requires declared repository, license, access route, metadata and documentation decisions; restricted/controlled categories need recorded constraints. Passing means only that the DMP is ready for human review, never that data may be released.

`python scripts/audit_dataset_metadata.py metadata.json --pretty` checks declared dataset metadata/release-review fields without opening data files.

## Workflow

1. Inventory each dataset without copying its contents; record owner, source, format, expected volume, and sensitivity.
2. Classify access needs conservatively. Escalate personal, health, contractual, export-controlled, or indigenous/community-governed data to the appropriate authority.
3. Define metadata, identifiers, formats, documentation, versioning, checksums, and a repository before calling data FAIR or releasable.
4. Attach governing policy, consent/DUA constraints, retention period, license, and approved access route before publication.
5. Use `reproduction-assistant` for checksums/provenance and `research-integrity-and-ethics` for readiness review.

## Resources

- `scripts/init_dmp.py` — protected DMP scaffold; contains no data transformation or publication action.
