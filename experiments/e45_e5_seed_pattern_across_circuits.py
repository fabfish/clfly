"""E45 — `e5`'s association, at two circuit sizes: does the seed pattern repeat, or was cs=800 unlucky?

`e41` found that `e5`'s published association — more anisotropy, larger gap, Spearman -0.75 — is
carried by **one seed of three**: per-seed rho(gap, flattening) at cs = 800 is **-0.964, -0.321,
+0.107**, pooled **-0.282 (p = 0.216)**, and under the absolute metric that the plan's measurement
rule 3 prescribes it is **+0.040 (p = 0.86)**.

That left an obvious escape: perhaps cs = 800's seeds were an unlucky draw, and the association is
fine. The escape is testable, because `e37` ran `e5`'s manipulation at **cs = 300 as well**, with the
same three seeds and the same seven `kappa` values, on a different task draw. Two circuit sizes,
two independent sets of tasks, one manipulation.

    python -m experiments.e45_e5_seed_pattern_across_circuits
    python -m experiments.e45_e5_seed_pattern_across_circuits --log /tmp/e37.log

The JSON route is preferred and sections itself from each file's `config`; the log route exists
because `e37` writes one JSON per (topology, circuit size) only when that section finishes, and the
progress lines already carry `flattening`, `effective_rank` and `gap_ewc`. **The log route cannot
compute the absolute excess** — `oracle_final` is not printed — so on the log path only the relative
`gap_ewc` is reported, and that is stated rather than silently assumed.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

#: e5-family outputs, one section each.  `config` carries `circuit_size` and (for e37's runs)
#: `topology`, which is what the sections are keyed on.
JSON_CANDIDATES = [
    "runs/e5_anisotropy.json",
    "runs/e37_kappa_real_cs800.json",
    "runs/e37_kappa_real_cs300.json",
    "runs/e37_kappa_swap2_cs800.json",
    "runs/e37_kappa_swap2_cs300.json",
    "runs/e42_e5_reseed.json",
]

LINE = re.compile(
    r"seed (\d+) kappa=(\S+)\s+flatten=([\d.]+) effrank=\s*([\d.]+).*gap_ewc=([+-][\d.]+)")
SECTION = re.compile(r"^===\s*(.+?)\s*===\s*$")


def rho(x, y) -> tuple[float, float]:
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return (float("nan"), float("nan"))
    r, p = spearmanr(x, y)
    return (float(r), float(p))


def summarise(label: str, rows: list[dict], key: str, metric: str | None = None) -> dict:
    """Per-seed and pooled Spearman over one section.

    ``rows`` are dicts with ``seed``, ``kappa``, ``flatten`` and the value under ``key``
    (``"gap"`` for the relative excess the script reports, ``"excess"`` for the absolute one rule 3
    prescribes).
    """
    out = {"label": label, "metric": metric or key, "per_seed": {}}
    pf, pv = [], []
    for s in sorted({r["seed"] for r in rows}):
        mine = sorted((r for r in rows if r["seed"] == s), key=lambda r: r["kappa"])
        f = [r["flatten"] for r in mine]
        v = [r[key] for r in mine]
        r_, p_ = rho(f, v)
        out["per_seed"][str(s)] = {"n": len(mine), "rho": r_, "p": p_}
        pf += f
        pv += v
    r_, p_ = rho(pf, pv)
    out["pooled"] = {"n": len(pf), "rho": r_, "p": p_}

    def verdict(v):
        if not np.isfinite(v["rho"]):
            return "incomplete"
        if v["p"] < 0.05:
            return "SIGNIFICANT"
        return "null"

    out["per_seed_verdicts"] = {k: verdict(v) for k, v in out["per_seed"].items()}
    out["pooled_verdict"] = verdict(out["pooled"])
    return out


def from_jsons(paths) -> list[dict]:
    sections = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        cfg = d["config"]
        topo = cfg.get("topology", "real")
        label = f"{p.name} (cs={cfg['circuit_size']}, {topo})"
        rows = []
        for pt in d["points"]:
            orc = pt.get("oracle_final")
            rows.append({"seed": pt["seed"], "kappa": float(pt["kappa"]),
                         "flatten": pt["flattening"], "gap": pt["gap_ewc"],
                         # the absolute excess, PRESENT in `e42` and later (stored directly) and
                         # derivable in older artifacts
                         "excess": pt.get("excess_ewc",
                                          pt["gap_ewc"] * orc if orc else float("nan"))})
        sections.append({"label": label, "rows": rows, "has_absolute": bool(
            all(r["excess"] == r["excess"] for r in rows))})
    return sections


def from_log(path: str) -> list[dict]:
    sections, cur, label = [], [], None
    for line in Path(path).read_text(errors="replace").splitlines():
        m = SECTION.match(line.strip())
        if m:
            if label and cur:
                sections.append({"label": label, "rows": cur, "has_absolute": False})
            label, cur = m.group(1), []
            continue
        m = LINE.search(line)
        if m and label:
            cur.append({"seed": int(m.group(1)), "kappa": float(m.group(2)),
                        "flatten": float(m.group(3)), "gap": float(m.group(5)),
                        "excess": float("nan")})
    if label and cur:
        sections.append({"label": label, "rows": cur, "has_absolute": False})
    return sections


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", default=None)
    ap.add_argument("--json-out", default="runs/e45_e5_seed_pattern.json")
    args = ap.parse_args()

    sections = from_jsons(JSON_CANDIDATES)
    if args.log:
        sections += from_log(args.log)
    if not sections:
        print("no e5-family output found (runs/ is gitignored); pass --log for an in-flight run")
        return

    print("=" * 100)
    print("PER-SEED AND POOLED Spearman(flattening, gap_EWC), BY SECTION")
    print("=" * 100)
    print("   each seed is a complete repeat of the kappa sweep, so it is the honest unit\n")
    print(f"   {'section':<44}{'seed':>5}{'n':>4}{'rho':>9}{'p':>9}  verdict")
    results = []
    for sec in sections:
        s = summarise(sec["label"], sec["rows"], "gap")
        results.append(s)
        for k, v in s["per_seed"].items():
            print(f"   {s['label'][:43]:<44}{k:>5}{v['n']:>4}{v['rho']:>+9.3f}{v['p']:>9.4f}"
                  f"  {s['per_seed_verdicts'][k]}")
        pv = s["pooled"]
        print(f"   {'  pooled':<44}{'all':>5}{pv['n']:>4}{pv['rho']:>+9.3f}{pv['p']:>9.4f}"
              f"  {s['pooled_verdict']}")

    print()
    print("=" * 100)
    print("THE SAME, UNDER THE ABSOLUTE EXCESS THAT MEASUREMENT RULE 3 PRESCRIBES")
    print("=" * 100)
    have = [sec for sec in sections if sec["has_absolute"]]
    if not have:
        print("   no section reaches this script with `oracle_final`/`excess_ewc`: the log route")
        print("   prints neither, so only the relative gap above is available from an in-flight")
        print("   run.  Re-run once the JSONs land.")
    else:
        print(f"   {'section':<44}{'seed':>5}{'n':>4}{'rho':>9}{'p':>9}  verdict")
        for sec in have:
            rows = sec["rows"]
            s = summarise(sec["label"], rows, "excess")
            results.append(s)
            for k, v in s["per_seed"].items():
                print(f"   {s['label'][:43]:<44}{k:>5}{v['n']:>4}{v['rho']:>+9.3f}{v['p']:>9.4f}"
                      f"  {s['per_seed_verdicts'][k]}")
            pv = s["pooled"]
            print(f"   {'  pooled':<44}{'all':>5}{pv['n']:>4}{pv['rho']:>+9.3f}{pv['p']:>9.4f}"
                  f"  {pv and s['pooled_verdict']}")

    print()
    print("=" * 100)
    print("DOES THE PATTERN REPEAT ACROSS CIRCUIT SIZES?")
    print("=" * 100)
    by_label = {}
    for sec, res in zip(sections, results):
        by_label.setdefault(sec["label"], {})[res["metric"]] = res
    sig = [r for r in results if r["pooled_verdict"] == "SIGNIFICANT"]
    null = [r for r in results if r["pooled_verdict"] == "null"]
    # The same draw appears once per route (the published artifact, `e37`'s JSON for that section,
    # and `e37`'s log section), and counting it three times would inflate every tally.  Dedupe on
    # the pooled statistic, which is identical to four decimals for a repeated draw.
    seen, distinct = set(), []
    for r in results:
        if r["metric"] != "gap":
            continue
        if r["pooled_verdict"] == "incomplete":
            continue  # a section still being written has no pooled statistic to compare
        k = (round(r["pooled"]["rho"], 6), round(r["pooled"]["p"], 6), r["pooled"]["n"])
        if k in seen:
            continue
        seen.add(k)
        distinct.append(r)
    dupes = sum(1 for r in results
                if r["metric"] == "gap" and r["pooled_verdict"] != "incomplete") - len(distinct)
    print(f"   {len(distinct)} DISTINCT pooled statistic(s) over {len(sig)+len(null)} sections"
          f" ({dupes} repeat(s) of the same draw via another route,")
    print(f"   plus {sum(1 for r in results if r['pooled_verdict'] == 'incomplete')}"
          f" section(s) still being written and excluded)")
    print(f"   of the distinct ones, {sum(1 for r in distinct if r['pooled_verdict'] == 'SIGNIFICANT')}"
          f" reach p < 0.05\n")
    print("   NOTE: a section read from an in-flight log can have a PARTIAL seed, and a partial seed")
    print("   biases the pool. Prefer the JSON with all 21 points; e45 was first read off a log with")
    print("   seed 2 at 4 of 7 points and it moved cs=300's pooled p from 0.0765 to 0.0319.\n")
    for r in distinct:
        if r["metric"] != "gap":
            continue
        n_strong = sum(1 for k, v in r["per_seed"].items()
                       if np.isfinite(v["rho"]) and v["rho"] < -0.8)
        n_pos = sum(1 for k, v in r["per_seed"].items()
                    if np.isfinite(v["rho"]) and v["rho"] > 0)
        print(f"     {r['label'][:58]:<60} pooled rho {r['pooled']['rho']:+.3f}"
              f" (p {r['pooled']['p']:.4f}) {r['pooled_verdict']:<12}"
              f" | {n_strong} seed(s) rho<-0.8, {n_pos} positive")
    print("\n   what to read from that: if the pooled verdict differs between two circuit sizes of")
    print("   the same manipulation, then the association's SIGNIFICANCE is not a property of the")
    print("   manipulation but of the draw; and if one seed carries it at each size, the failure")
    print("   mode e41 found at cs = 800 is reproduced rather than being a quirk of one artifact.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump({"results": results,
                   "sections": [{"label": s["label"], "has_absolute": s["has_absolute"]}
                                for s in sections]}, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
