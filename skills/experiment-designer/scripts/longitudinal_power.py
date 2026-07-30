#!/usr/bin/env python3
"""Approximate sample sizes for repeated, longitudinal, and survival designs."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from statistics import NormalDist


VERSION = "0.1.0"
Z = NormalDist()


def critical(alpha: float, sides: int) -> float:
    return Z.inv_cdf(1 - alpha / sides)


def validate_common(args) -> None:
    if not 0 < args.alpha < 1 or not 0 < args.power < 1:
        raise ValueError("--alpha and --power must be in (0, 1)")
    if not 0 <= args.dropout < 1:
        raise ValueError("--dropout must be in [0, 1)")


def two_group_base(effect: float, alpha: float, power: float, sides: int) -> float:
    if effect <= 0:
        raise ValueError("--effect-size must be > 0")
    return 2 * (critical(alpha, sides) + Z.inv_cdf(power)) ** 2 / effect ** 2


def repeated_mean(args) -> dict:
    if args.measurements < 2:
        raise ValueError("--measurements must be >= 2")
    if not 0 <= args.correlation < 1:
        raise ValueError("--correlation must be in [0, 1)")
    base = two_group_base(args.effect_size, args.alpha, args.power, args.sides)
    variance_ratio = (1 + (args.measurements - 1) * args.correlation) / args.measurements
    analyzable = math.ceil(base * variance_ratio)
    enroll = math.ceil(analyzable / (1 - args.dropout))
    return {
        "design": "repeated-mean",
        "estimand": "constant between-group mean difference averaged across measurements",
        "effect_size": args.effect_size,
        "measurements": args.measurements,
        "compound_symmetry_correlation": args.correlation,
        "variance_ratio_vs_single_measure": variance_ratio,
        "n_analyzable_per_group": analyzable,
        "n_enroll_per_group": enroll,
        "n_enroll_total": 2 * enroll,
        "notes": [
            "normal approximation with equal allocation and complete compound-symmetric measurements",
            "effect size is the constant mean difference divided by the marginal per-measure SD",
            "use simulation or dedicated software for time-varying effects, nonspherical covariance, or intermittent missingness",
        ],
    }


def parse_times(value: str) -> list[float]:
    try:
        times = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise ValueError("--times must be comma-separated numbers") from exc
    if len(times) < 2 or len(set(times)) != len(times) or times != sorted(times):
        raise ValueError("--times must contain at least two unique increasing values")
    return times


def longitudinal_slope(args) -> dict:
    times = parse_times(args.times)
    if not 0 <= args.correlation < 1:
        raise ValueError("--correlation must be in [0, 1)")
    if args.slope_effect == 0:
        raise ValueError("--slope-effect must be nonzero")
    centered = [item - sum(times) / len(times) for item in times]
    sxx = sum(item ** 2 for item in centered)
    variance_factor = (1 - args.correlation) / sxx
    raw = 2 * variance_factor * (critical(args.alpha, args.sides) + Z.inv_cdf(args.power)) ** 2 / args.slope_effect ** 2
    analyzable = math.ceil(raw)
    enroll = math.ceil(analyzable / (1 - args.dropout))
    return {
        "design": "longitudinal-slope",
        "estimand": "between-group difference in linear slopes",
        "standardized_slope_difference_per_time_unit": args.slope_effect,
        "times": times,
        "compound_symmetry_correlation": args.correlation,
        "slope_variance_factor": variance_factor,
        "n_analyzable_per_group": analyzable,
        "n_enroll_per_group": enroll,
        "n_enroll_total": 2 * enroll,
        "notes": [
            "normal approximation, equal allocation, linear change, common marginal SD, and compound symmetry",
            "slope effect is the group slope difference per time unit divided by the marginal outcome SD",
            "random slopes, nonlinear change, visit-specific variance, and missing-data patterns require simulation or dedicated longitudinal software",
        ],
    }


def survival(args) -> dict:
    if args.hazard_ratio <= 0 or math.isclose(args.hazard_ratio, 1.0):
        raise ValueError("--hazard-ratio must be > 0 and not equal to 1")
    if not 0 < args.event_probability <= 1:
        raise ValueError("--event-probability must be in (0, 1]")
    if args.allocation_ratio <= 0:
        raise ValueError("--allocation-ratio must be > 0")
    treatment_fraction = args.allocation_ratio / (1 + args.allocation_ratio)
    events_raw = (critical(args.alpha, args.sides) + Z.inv_cdf(args.power)) ** 2 / (
        treatment_fraction * (1 - treatment_fraction) * math.log(args.hazard_ratio) ** 2
    )
    events = math.ceil(events_raw)
    enrolled = math.ceil(events / args.event_probability / (1 - args.dropout))
    treatment = math.ceil(enrolled * treatment_fraction)
    control = math.ceil(treatment / args.allocation_ratio)
    return {
        "design": "survival-logrank",
        "estimand": "constant hazard ratio under proportional hazards",
        "hazard_ratio": args.hazard_ratio,
        "allocation_ratio_treatment_to_control": args.allocation_ratio,
        "assumed_overall_event_probability": args.event_probability,
        "required_events": events,
        "n_enroll_treatment": treatment,
        "n_enroll_control": control,
        "n_enroll_total": treatment + control,
        "notes": [
            "Schoenfeld event approximation; event probability converts events to participants",
            "accrual, follow-up, censoring, competing risks, and arm-specific event rates are not modeled",
            "do not use this approximation when proportional hazards is implausible; choose an estimand/test and simulate that design",
        ],
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
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--alpha", type=float, default=0.05)
    common.add_argument("--power", type=float, default=0.80)
    common.add_argument("--sides", type=int, choices=[1, 2], default=2)
    common.add_argument("--dropout", type=float, default=0.0)
    common.add_argument("--out", type=Path)
    common.add_argument("--force", action="store_true")
    sub = parser.add_subparsers(dest="design", required=True)
    repeated = sub.add_parser("repeated-mean", parents=[common], help="constant mean effect averaged over repeated outcomes")
    repeated.add_argument("--effect-size", type=float, required=True)
    repeated.add_argument("--measurements", type=int, required=True)
    repeated.add_argument("--correlation", type=float, required=True)
    slope = sub.add_parser("longitudinal-slope", parents=[common], help="difference in linear slopes")
    slope.add_argument("--slope-effect", type=float, required=True)
    slope.add_argument("--times", required=True, help="increasing comma-separated measurement times")
    slope.add_argument("--correlation", type=float, required=True)
    event = sub.add_parser("survival", parents=[common], help="Schoenfeld log-rank event approximation")
    event.add_argument("--hazard-ratio", type=float, required=True)
    event.add_argument("--event-probability", type=float, required=True, help="overall event probability by analysis time")
    event.add_argument("--allocation-ratio", type=float, default=1.0, help="treatment:control ratio")
    args = parser.parse_args(argv)
    if args.out and args.out.exists() and not args.force:
        parser.error(f"output exists: {args.out}; use --force to replace it")
    try:
        validate_common(args)
        result = repeated_mean(args) if args.design == "repeated-mean" else longitudinal_slope(args) if args.design == "longitudinal-slope" else survival(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    result.update({"alpha": args.alpha, "power": args.power, "sides": args.sides, "dropout_rate": args.dropout, "method": "normal approximation"})
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
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
