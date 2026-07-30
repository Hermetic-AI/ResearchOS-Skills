#!/usr/bin/env python3
"""Weighted triage scoring for a set of papers.

Purpose
    Rank a batch of candidate papers by user-supplied weighted dimensions
    (default: relevance / novelty / quality / reproducibility). Input is a
    JSON file of per-paper dimension scores; output is a ranked list with
    weighted totals, tie-breaking, and an optional fixed-seed shuffle for
    jittering exact ties.

Dependencies
    None. Python 3.8+ standard library only (json, sys, argparse, random).

CLI usage
    python3 triage_score.py <scores.json> [--weights w.json] [--top N]
                            [--seed 42] [--format json|markdown] [--pretty]

    <scores.json>  UTF-8 JSON file:
                     {"papers": [{"id": "...", "title": "...",
                                  "scores": {"relevance": 4, "novelty": 3, ...}},
                                 ...]}
                   Scores are 1-5. Missing dimensions count as 0 and are
                   flagged in warnings.
    --weights      JSON object mapping dimension -> weight, e.g.
                   '{"relevance": 0.4, "novelty": 0.2, "quality": 0.2,
                     "reproducibility": 0.2}'
                   Weights are normalized to sum to 1. Default: equal weights
                   over all dimensions present in the input.
    --top N        Keep only the top N papers in the output.
    --seed         Integer seed used ONLY to break exact-total ties
                   deterministically (random jitter of 1e-6 scale). Omit for
                   stable input-order tie-breaking.
    --format       json (default) or markdown table.
    --pretty       Pretty-print JSON output.

Output format (JSON to stdout)
    {
      "weights": {"relevance": 0.25, ...},   # normalized
      "paper_count": <int>,
      "ranked": [
        {
          "rank": <int>,
          "id": "...", "title": "...",
          "total": <float, 3 decimals>,
          "scores": {"relevance": 4, ...},
          "verdict": "keep" | "skim-later" | "drop"
        }, ...
      ],
      "warnings": ["<missing dimension, bad score, ...>", ...]
    }

    Verdict thresholds on the weighted total (1-5 scale):
    keep >= 3.5, skim-later >= 2.5, drop < 2.5.

Notes
    - Deterministic: identical input and seed give identical output.
    - The script only computes; the scores themselves are the reader's
      judgment (see references/reading-workflows.md triage section).
"""

import argparse
import json
import random
import sys

VERDICTS = ((3.5, "keep"), (2.5, "skim-later"), (0.0, "drop"))
DEFAULT_DIMENSIONS = ("relevance", "novelty", "quality", "reproducibility")


def verdict(total):
    for threshold, name in VERDICTS:
        if total >= threshold:
            return name
    return "drop"


def load_json(path, what):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "cannot read %s: %s" % (what, exc)}), file=sys.stderr)
        sys.exit(2)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Weighted triage ranking of papers from dimension scores (zero dependencies)."
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("input", help="JSON file: {\"papers\": [{id, title, scores}, ...]}")
    parser.add_argument("--weights", help="JSON string or path to JSON file mapping dimension -> weight")
    parser.add_argument("--top", type=int, default=None, help="keep only top N papers")
    parser.add_argument("--seed", type=int, default=None, help="seed for deterministic tie-breaking")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    data = load_json(args.input, "input")
    papers = data.get("papers")
    if not isinstance(papers, list) or not papers:
        print(json.dumps({"error": "input must contain a non-empty 'papers' list"}), file=sys.stderr)
        return 2

    warnings = []
    # Collect the dimension set: input order, defaults first when present.
    seen = []
    for p in papers:
        for dim in (p.get("scores") or {}):
            if dim not in seen:
                seen.append(dim)
    dimensions = [d for d in DEFAULT_DIMENSIONS if d in seen] + [d for d in seen if d not in DEFAULT_DIMENSIONS]
    if not dimensions:
        print(json.dumps({"error": "no dimension scores found in any paper"}), file=sys.stderr)
        return 2

    if args.weights:
        try:
            raw_weights = json.loads(args.weights)
        except ValueError:
            raw_weights = load_json(args.weights, "weights")
        unknown = [d for d in raw_weights if d not in dimensions]
        if unknown:
            warnings.append("weight dimensions not present in scores, ignored: %s" % ", ".join(sorted(unknown)))
        weights = {d: float(raw_weights.get(d, 0.0)) for d in dimensions}
    else:
        weights = {d: 1.0 for d in dimensions}
    total_w = sum(weights.values())
    if total_w <= 0:
        print(json.dumps({"error": "weights sum to zero"}), file=sys.stderr)
        return 2
    weights = {d: w / total_w for d, w in weights.items()}

    rng = random.Random(args.seed) if args.seed is not None else None
    ranked = []
    for i, p in enumerate(papers):
        scores = p.get("scores") or {}
        clean = {}
        for d in dimensions:
            v = scores.get(d)
            if v is None:
                warnings.append("paper %s (%s): missing score for '%s', counted as 0"
                                % (p.get("id", i), p.get("title", "?"), d))
                v = 0.0
            else:
                try:
                    v = float(v)
                except (TypeError, ValueError):
                    warnings.append("paper %s (%s): score %r for '%s' not numeric, counted as 0"
                                    % (p.get("id", i), p.get("title", "?"), v, d))
                    v = 0.0
            if not 0.0 <= v <= 5.0:
                warnings.append("paper %s: score %s for '%s' outside 0-5, clamped"
                                % (p.get("id", i), v, d))
                v = min(5.0, max(0.0, v))
            clean[d] = v
        total = sum(clean[d] * weights[d] for d in dimensions)
        jitter = rng.random() * 1e-6 if rng else i * 1e-9
        ranked.append({
            "rank": 0,
            "id": p.get("id", "paper-%d" % i),
            "title": p.get("title", ""),
            "total": round(total, 3),
            "scores": clean,
            "verdict": verdict(total),
            "_sort": -(total + jitter),
        })

    ranked.sort(key=lambda r: r["_sort"])
    if args.top is not None:
        ranked = ranked[: max(0, args.top)]
    for rank, r in enumerate(ranked, 1):
        r["rank"] = rank
        del r["_sort"]

    result = {"weights": {d: round(w, 4) for d, w in weights.items()},
              "paper_count": len(ranked), "ranked": ranked, "warnings": warnings}

    if args.format == "markdown":
        dims = dimensions
        header = "| Rank | ID | Title | Total | Verdict | " + " | ".join(dims) + " |"
        sep = "|" + "---|" * (5 + len(dims))
        rows = ["| %d | %s | %s | %.3f | %s | %s |" % (
            r["rank"], r["id"], (r["title"] or "")[:60].replace("|", "\\|"),
            r["total"], r["verdict"],
            " | ".join("%.1f" % r["scores"][d] for d in dims)) for r in ranked]
        sys.stderr.write("".join("warning: %s\n" % w for w in warnings))
        print("\n".join([header, sep] + rows))
        return 0

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
