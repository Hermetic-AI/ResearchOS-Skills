---
name: researchos
description: Orchestrate 28 research skills (literature, design, data, figures, writing, reproduction, etc.). Routes user tasks to the right sub-skill. Use when starting a research project, picking a research tool, asking "what's next" in a research workflow, or chaining literature→design→data→figures→writing. Not for executing domain workflows directly — routes to sub-skills.
---

# ResearchOS (Research Skill Orchestrator)

ResearchOS is a suite of 28 independent, zero-dependency research skills. This is the **orchestrator** — it routes your task to the right sub-skill. Each sub-skill is invoked via its slash command (e.g., `/literature-reader`) and runs independently.

## How to use

1. Tell me your research task in natural language (Chinese or English).
2. I'll route you to the correct sub-skill based on the trigger table below.
3. Invoke the sub-skill with its slash command, or ask me to continue and I'll load it.

## Routing table

### Literature & Evidence

| User wants... | Slash command | Triggers |
|---|---|---|
| Read/extract/audit papers, PDF/OCR, DOI check, Zotero/BibTeX/RIS convert | `/literature-reader` | read papers, PDF extract, deduplicate literature, Zotero convert, extract, audit papers |
| Build concept graphs from notes, trace research lineages | `/knowledge-graph-builder` | knowledge graph, research lineage, paper-note to graph, trace lineage |
| Plan database searches, deduplicate citations, export RIS/BibTeX/CSV | `/scholarly-search-manager` | search query, DOI dedupe, literature exchange, search strategy |
| Systematic review, meta-analysis, PICOS, PRISMA, effect sizes, I² | `/systematic-review-meta-analysis` | systematic review, meta-analysis, PRISMA, effect size, meta-analysis |

### Study Design & Data

| User wants... | Slash command | Triggers |
|---|---|---|
| Design experiments, DOE, randomization, power analysis, preregistration | `/experiment-designer` | experiment design, preregistration, sample size, power analysis, DOE, power |
| Analyze data, regression, GLM, Cox, SARIMAX, panel, MICE, equivalence | `/data-analysis-assistant` | data analysis, regression, survival analysis, time series, analyze data |
| Causal inference, DAG, propensity score, DiD, RDD, IV, E-value | `/causal-inference-assistant` | causal inference, propensity score, difference-in-differences, DAG, causal |
| Qualitative coding, codebooks, Krippendorff's α, saturation | `/qualitative-research-assistant` | codebook, qualitative research, saturation, qualitative |
| Survey design, EFA, CFA, IRT, Rasch, Cronbach's α | `/survey-and-psychometrics` | survey, factor analysis, reliability, validity, psychometrics |

### Writing & Communication

| User wants... | Slash command | Triggers |
|---|---|---|
| Write/check papers, citation audit, DOCX/LaTeX format, DOI verify | `/paper-writing-assistant` | paper writing, citation check, format check, typesetting, citation audit |
| Convert Markdown→LaTeX, footnotes, theorems, cross-refs, CSL→BibTeX | `/md2latex` | md to latex, markdown to tex, IEEEtran, convert to ctex |
| Publication figures, statistical charts, journal themes, SVG/PDF export | `/scientific-plot` | research figures, statistical charts, forest plot, survival curve, figure |
| Presentations, posters, Beamer/reveal.js, WCAG contrast | `/academic-presentation-poster` | presentation, poster, slides, presentation, poster |
| Thesis defense, mock Q&A, contribution-evidence audit | `/thesis-defense-assistant` | defense, mock Q&A, defense preparation |

### Reproduction & Integrity

| User wants... | Slash command | Triggers |
|---|---|---|
| Reproduce paper code, compare results, isolation planning | `/reproduction-assistant` | reproduce paper, result comparison, reproduce, reproduction |
| Peer review triage, response matrix, CONSORT/STROBE/PRISMA check | `/peer-review-and-rebuttal` | peer review, response matrix, rebuttal, review |
| Ethics checklist, authorship, AI disclosure, policy coverage | `/research-integrity-and-ethics` | ethics, authorship, AI disclosure, ethics, integrity |

### Management & Planning

| User wants... | Slash command | Triggers |
|---|---|---|
| Research proposal, Specific Aims, budget, milestones | `/research-proposal-and-grant` | research plan, proposal, proposal, grant |
| Data management plan, FAIR, anonymization, release readiness | `/research-data-management` | DMP, FAIR, data management, anonymization |
| Project orchestration, artifact routing, decision provenance | `/research-project-orchestrator` | project orchestration, workflow, orchestrate |
| Software quality, release audit, benchmark, CITATION.cff | `/research-software-quality` | software quality, release audit, release audit |
| Research protocol, reporting guidelines, registry summary | `/protocol-authoring` | research protocol, guideline mapping, protocol |
| Patent prior-art search, family parsing, Mermaid tree | `/patent-prior-art-search` | patent search, family parsing, prior art |

### Domain-Specific

| User wants... | Slash command | Triggers |
|---|---|---|
| ML experiment plan, baselines, ablations, model card | `/machine-learning-research` | ML experiment, ablation, baseline, model card |
| Biomedical study plan, endpoints, specimens, safety | `/biomedical-research` | biomedical, clinical trial, biomedical |
| Materials experiment, synthesis, characterization, provenance | `/materials-research` | materials experiment, synthesis, materials |
| Chemistry experiment, reagents, analytical, hazard/waste | `/chemistry-research` | chemistry experiment, reagents, chemistry |
| Social-science study, sampling, measurement, mixed-methods | `/social-science-research` | social science, survey, social science |

## Workflow patterns

**Full pipeline** (literature → design → data → figures → writing):
```
/literature-reader → /experiment-designer → /data-analysis-assistant → /scientific-plot → /paper-writing-assistant
```

**Reproduction** (paper code → results):
```
/reproduction-assistant
```

**Knowledge synthesis** (notes → graph → gaps):
```
/literature-reader → /knowledge-graph-builder
```

## Installation

Each skill is self-contained. To install the full suite:

```bash
# Clone the repository
git clone <repo-url> researchos-skills

# Install all skills to user-level (.claude/skills/)
python researchos-skills/tools/install_skills.py

# Or install to project-level
python researchos-skills/tools/install_skills.py --scope project
```

After installation, all 28 skills appear as slash commands in Claude Code.
