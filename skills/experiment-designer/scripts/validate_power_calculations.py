#!/usr/bin/env python3
"""Cross-validate ResearchOS power approximations against SciPy/statsmodels."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


VERSION = "0.1.0"


def validate() -> dict:
    try:
        import scipy
        from scipy.stats import norm
        import statsmodels
        from statsmodels.stats.power import NormalIndPower, TTestIndPower, TTestPower
    except ImportError as exc:
        raise RuntimeError('install validation dependencies with: python -m pip install -e ".[validation]"') from exc

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import power_analysis as local

    cases = []
    n_errors, power_errors = [], []
    models = {
        "t_ind": TTestIndPower(),
        "t_one": TTestPower(),
        "t_paired": TTestPower(),
        "two_prop": NormalIndPower(),
    }
    for test, model in models.items():
        n_from_d, power_from, _ = local.formulas(test)
        for effect in (0.2, 0.5, 0.8):
            for alpha in (0.01, 0.05):
                for target in (0.8, 0.9):
                    local_n = n_from_d(effect, alpha, target, 2)
                    solve_kwargs = {"effect_size": effect, "alpha": alpha, "power": target, "alternative": "two-sided"}
                    solve_kwargs["nobs1" if test in ("t_ind", "two_prop") else "nobs"] = None
                    reference_n = float(model.solve_power(**solve_kwargs))
                    n_error = abs(local_n - math.ceil(reference_n))
                    local_power = power_from(effect, max(local_n, 30), alpha, 2)
                    power_kwargs = {"effect_size": effect, "alpha": alpha, "alternative": "two-sided"}
                    power_kwargs["nobs1" if test in ("t_ind", "two_prop") else "nobs"] = max(local_n, 30)
                    reference_power = float(model.power(**power_kwargs))
                    power_error = abs(local_power - reference_power)
                    n_errors.append(n_error)
                    power_errors.append(power_error)
                    cases.append({
                        "test": test, "effect_size": effect, "alpha": alpha,
                        "target_power": target, "local_n": local_n,
                        "reference_n_ceiling": math.ceil(reference_n),
                        "absolute_n_error": n_error,
                        "absolute_power_error": power_error,
                    })
    z_errors = []
    for alpha in (0.001, 0.01, 0.05, 0.1):
        for sides in (1, 2):
            z_errors.append(abs(local.zcrit(alpha, sides) - float(norm.ppf(1 - alpha / sides))))
    thresholds = {"max_absolute_n_error": 4, "max_absolute_power_error": 0.04, "max_absolute_z_error": 1e-12}
    maxima = {
        "max_absolute_n_error": max(n_errors),
        "max_absolute_power_error": max(power_errors),
        "max_absolute_z_error": max(z_errors),
    }
    passed = all(maxima[key] <= value for key, value in thresholds.items())
    return {
        "status": "pass" if passed else "fail",
        "local_version": VERSION,
        "references": {"scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
        "scope": "normal-approximation superiority calculations only",
        "thresholds": thresholds,
        "maxima": maxima,
        "case_count": len(cases),
        "cases": cases,
        "limitations": [
            "statsmodels t-test calculations use the noncentral t distribution, while the local CLI intentionally uses a documented normal approximation",
            "noninferiority, equivalence, cluster, longitudinal, and survival extensions require separate design-specific validation",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--out", type=Path, help="write JSON report instead of stdout")
    parser.add_argument("--force", action="store_true", help="replace an existing --out file")
    args = parser.parse_args(argv)
    if args.out and args.out.exists() and not args.force:
        parser.error(f"output exists: {args.out}; use --force to replace it")
    try:
        report = validate()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
