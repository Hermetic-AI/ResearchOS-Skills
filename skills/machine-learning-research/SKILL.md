---
name: machine-learning-research
description: Plan auditable machine-learning research workflows with data splits, leakage controls, metrics, baselines, ablations, compute budgets, evaluation protocols, model-card evidence, and reproducibility handoffs. Use when users need an ML experiment plan, benchmark protocol, ablation plan, model evaluation checklist, model card evidence ledger, or training reproducibility plan.
---

# Machine Learning Research

Do not claim a model was trained, benchmarked, state of the art, fair, safe, or reproducible without run artifacts and an explicit evaluation protocol. Do not expose private training examples, credentials, weights, or license-restricted datasets in planning artifacts.

## Initialize an ML experiment plan

```bash
python scripts/init_ml_plan.py --out ml-plan.json --task "Task" --primary-metric "AUROC"
```

The plan records data split and leakage decisions, baselines, metrics, ablations, compute budget, evaluation protocol, risks, model-card evidence and reproducibility links. It does not run training.

## Workflow

1. Define the prediction task, unit of split, target, intended use, and prohibited uses before modeling.
2. Pre-specify train/validation/test isolation, temporal/group leakage controls, metrics, uncertainty, decision threshold, and baseline models.
3. Treat model selection on the test set as a protocol deviation; preserve seeds, code commit, dataset checksum, config, hardware and run artifacts using `reproduction-assistant`.
4. Route formal statistical comparisons to `data-analysis-assistant`, figures to `scientific-plot`, and data governance to `research-data-management`.

## Resources

- `scripts/init_ml_plan.py` — protected ML experiment and model-card evidence scaffold.
