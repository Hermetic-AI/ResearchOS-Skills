#!/usr/bin/env python3
"""Plan multiplicity, interim alpha spending, stopping, and adaptations."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist


VERSION = "0.1.0"
METHODS = {"bonferroni", "weighted-bonferroni", "holm"}
SPENDING = {"obrien-fleming", "pocock", "none"}
ADAPTATION_FIELDS = {"id", "type", "timing", "decision_rule", "data_scope", "inference_adjustment", "operational_firewall"}


def load_spec(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read input JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("input root must be an object")
    return value


def validate(spec: dict) -> None:
    alpha = spec.get("family_alpha")
    if not isinstance(alpha, (int, float)) or isinstance(alpha, bool) or not 0 < alpha < 1:
        raise ValueError("family_alpha must be strictly between 0 and 1")
    if spec.get("sidedness", "two-sided") not in {"one-sided", "two-sided"}:
        raise ValueError("sidedness must be one-sided or two-sided")
    method = spec.get("multiplicity", {}).get("method")
    if method not in METHODS:
        raise ValueError("multiplicity.method must be bonferroni, weighted-bonferroni, or holm")
    endpoints = spec.get("endpoints")
    if not isinstance(endpoints, list) or not endpoints:
        raise ValueError("endpoints must be a non-empty array")
    ids = [item.get("id") for item in endpoints if isinstance(item, dict)]
    if len(ids) != len(endpoints) or any(not isinstance(item, str) or not item for item in ids):
        raise ValueError("every endpoint needs a non-empty id")
    if len(set(ids)) != len(ids):
        raise ValueError("endpoint ids must be unique")
    if method == "weighted-bonferroni":
        weights = [item.get("weight") for item in endpoints]
        if any(not isinstance(item, (int, float)) or isinstance(item, bool) or item <= 0 for item in weights):
            raise ValueError("weighted-bonferroni requires a positive weight on every endpoint")
    sequential = spec.get("sequential", {})
    spending = sequential.get("spending", "none")
    if spending not in SPENDING:
        raise ValueError("sequential.spending must be obrien-fleming, pocock, or none")
    fractions = sequential.get("information_fractions", [1.0])
    if not isinstance(fractions, list) or not fractions:
        raise ValueError("information_fractions must be a non-empty array")
    if any(not isinstance(item, (int, float)) or isinstance(item, bool) or not 0 < item <= 1 for item in fractions):
        raise ValueError("information fractions must be in (0, 1]")
    if fractions != sorted(set(fractions)) or not math.isclose(fractions[-1], 1.0, abs_tol=1e-12):
        raise ValueError("information fractions must be unique, increasing, and end at 1.0")
    if spending == "none" and len(fractions) > 1:
        raise ValueError("multiple looks require an explicit alpha-spending function")
    for index, adaptation in enumerate(spec.get("adaptations", [])):
        if not isinstance(adaptation, dict):
            raise ValueError(f"adaptations[{index}] must be an object")
        missing = sorted(ADAPTATION_FIELDS - adaptation.keys())
        if missing:
            raise ValueError(f"adaptations[{index}] missing prespecification fields: {', '.join(missing)}")
        if any("_TODO_" in str(adaptation[field]) for field in ADAPTATION_FIELDS):
            raise ValueError(f"adaptations[{index}] contains unresolved _TODO_ fields")
    for key in ("efficacy", "futility", "safety"):
        rule = spec.get("stopping_rules", {}).get(key)
        if rule is not None and (not isinstance(rule, dict) or not rule.get("decision_rule") or not rule.get("authority")):
            raise ValueError(f"stopping_rules.{key} requires decision_rule and authority")


def endpoint_allocations(spec: dict) -> tuple[list[dict], list[str]]:
    endpoints = spec["endpoints"]
    alpha = float(spec["family_alpha"])
    method = spec["multiplicity"]["method"]
    warnings: list[str] = []
    if method == "weighted-bonferroni":
        total = sum(float(item["weight"]) for item in endpoints)
        return [
            {**item, "normalized_weight": float(item["weight"]) / total, "local_alpha": alpha * float(item["weight"]) / total}
            for item in endpoints
        ], warnings
    if method == "bonferroni":
        share = alpha / len(endpoints)
        return [{**item, "normalized_weight": 1 / len(endpoints), "local_alpha": share} for item in endpoints], warnings
    thresholds = [alpha / (len(endpoints) - rank + 1) for rank in range(1, len(endpoints) + 1)]
    warnings.append("Holm thresholds apply to ordered p-values, not fixed endpoint-specific alpha allocations.")
    return [{**item, "local_alpha": None, "holm_rank_thresholds": thresholds} for item in endpoints], warnings


def spend(alpha: float, fraction: float, method: str, sides: int) -> float:
    if method == "none":
        return alpha if math.isclose(fraction, 1.0) else 0.0
    if method == "pocock":
        return alpha * math.log(1 + (math.e - 1) * fraction)
    critical = NormalDist().inv_cdf(1 - alpha / sides)
    return sides * (1 - NormalDist().cdf(critical / math.sqrt(fraction)))


def looks_for(alpha: float, fractions: list[float], method: str, sides: int) -> list[dict]:
    result = []
    prior = 0.0
    for index, fraction in enumerate(fractions, 1):
        cumulative = min(alpha, spend(alpha, fraction, method, sides))
        result.append({
            "look": index,
            "information_fraction": fraction,
            "cumulative_alpha_budget": cumulative,
            "incremental_alpha_budget": max(0.0, cumulative - prior),
        })
        prior = cumulative
    return result


def build(spec: dict, source: Path, argv: list[str]) -> dict:
    validate(spec)
    allocations, warnings = endpoint_allocations(spec)
    sequential = spec.get("sequential", {})
    fractions = [float(item) for item in sequential.get("information_fractions", [1.0])]
    spending = sequential.get("spending", "none")
    sides = 1 if spec.get("sidedness", "two-sided") == "one-sided" else 2
    for endpoint in allocations:
        local = endpoint.get("local_alpha")
        endpoint["looks"] = looks_for(local, fractions, spending, sides) if local is not None else []
    if len(fractions) > 1:
        warnings.append("Alpha budgets are not calibrated test-statistic boundaries; validate operating characteristics with suitable software or simulation before use.")
    if spec.get("adaptations"):
        warnings.append("Adaptive operating characteristics and inference adjustments require design-specific validation or simulation.")
    provenance = {
        "created_by": "experiment-designer/plan_sequential_design.py",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tool_version": VERSION,
        "command": " ".join(argv),
        "sources": [{"kind": "file", "locator": str(source.resolve())}],
        "warnings": warnings,
    }
    return {
        "schema_version": "1.0.0",
        "artifact_type": "sequential-design-plan",
        "study_id": spec.get("study_id"),
        "family_alpha": float(spec["family_alpha"]),
        "sidedness": spec.get("sidedness", "two-sided"),
        "multiplicity": spec["multiplicity"],
        "endpoints": allocations,
        "sequential": {"spending": spending, "information_fractions": fractions},
        "stopping_rules": spec.get("stopping_rules", {}),
        "adaptations": spec.get("adaptations", []),
        "simulation_plan": spec.get("simulation_plan"),
        "warnings": warnings,
        "provenance": provenance,
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--input", required=True, type=Path, help="design specification JSON")
    parser.add_argument("--out", type=Path, help="write JSON artifact instead of stdout")
    parser.add_argument("--force", action="store_true", help="replace an existing --out file")
    args = parser.parse_args(argv)
    if args.out and args.out.resolve() == args.input.resolve():
        parser.error("--out must not replace --input")
    if args.out and args.out.exists() and not args.force:
        parser.error(f"output exists: {args.out}; use --force to replace it")
    try:
        artifact = build(load_spec(args.input), args.input, [Path(sys.argv[0]).name, *(argv if argv is not None else sys.argv[1:])])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        atomic_write(args.out, text)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
