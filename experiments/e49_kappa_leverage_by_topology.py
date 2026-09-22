"""E49 — an intervention must be shown to *have leverage* where it is applied.

The `e36` mechanism was: `swap2`'s excess tracks the rank collapse of its task precision. The test
was `e5`'s concentration knob, applied at `swap2`, and `e37` ran it. This script reads the result and
asks the prior question first: **does the knob move the proposed carrier at all, at each
configuration?**

It does not, at `swap2` and cs = 800. Across `kappa` 0 -> 4 the knob moves `flattening` by
**0.68-0.73** at `real` and by **0.004-0.008** at `swap2` — a factor of ~90 — because `swap2`'s task
precision is *already* rank-collapsed there (`effective_rank` starts at 1.70 against `real`'s 55).
So a correlation between `gap_EWC` and `flattening` computed at `swap2`/cs = 800 is a correlation
over a flattening range barely wider than the seed-to-seed spread, and its sign means nothing either
way.

That is the resolution of the tension three findings have been circling: the mechanism's own premise
(the collapse) is what pins the carrier at the configuration that motivated it, so the intervention
is **inert exactly where the mechanism was proposed and testable only where the collapse has not
happened** — and the one such place (cs = 300, `effective_rank` 15.4) gave the opposite sign of the
mechanism.

    python -m experiments.e49_kappa_leverage_by_topology
    python -m experiments.e49_kappa_leverage_by_topology --log /tmp/e37.log

Per-seed only: plan rule 17 forbids a pooled statistic from a run whose last seed is still being
written, and this script reports the per-seed values with their `n` rather than pooling across an
inhomogeneous set.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

JSON_CANDIDATES = [
    "runs/e37_kappa_real_cs800.json",
    "runs/e37_kappa_real_cs300.json",
    "runs/e37_kappa_swap2_cs800.json",
    "runs/e37_kappa_swap2_cs300.json",
    "runs/e5_anisotropy.json",
    "runs/e42_e5_reseed.json",
]

LINE = re.compile(
    r"seed (\d+) kappa=(\S+)\s+flatten=([\d.]+) effrank=\s*([\d.]+)"
    r".*offdiag=([\d.]+).*gap_ewc=([+-][\d.]+)")
SECTION = re.compile(r"^===\s*(.+?)\s*===\s*$")

#: A knob whose travel is smaller than this multiple of the across-seed spread at the knob's own
#: starting point is reported as inert: the correlation is over noise, whatever its sign.
LEVERAGE_FLOOR = 10.0


def from_jsons(paths) -> list[dict]:
    out = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        c = d["config"]
        rows = []
        for pt in d["points"]:
            orc = pt.get("oracle_final")
            rows.append({
                "seed": pt["seed"], "kappa": float(pt["kappa"]),
                "flatten": pt["flattening"], "effrank": pt["effective_rank"],
                "offdiag": pt.get("press_mean_discarded", float("nan")),
                "gap": pt["gap_ewc"],
                "excess": pt.get("excess_ewc",
                                 pt["gap_ewc"] * orc if orc else float("nan"))})
        out.append({"label": f"{Path(path).name} ({c.get('topology', 'real')},"
                             f" cs={c['circuit_size']})", "rows": rows})
    return out


def from_log(path: str) -> list[dict]:
    out, cur, label = [], [], None
    for line in Path(path).read_text(errors="replace").splitlines():
        m = SECTION.match(line.strip())
        if m:
            if label and cur:
                out.append({"label": label, "rows": cur})
            label, cur = m.group(1), []
            continue
        m = LINE.search(line)
        if m and label:
            cur.append({"seed": int(m.group(1)), "kappa": float(m.group(2)),
                        "flatten": float(m.group(3)), "effrank": float(m.group(4)),
                        "offdiag": float(m.group(5)), "gap": float(m.group(6)),
                        "excess": float("nan")})
    if label and cur:
        out.append({"label": label, "rows": cur})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", default=None)
    ap.add_argument("--json-out", default="runs/e49_kappa_leverage.json")
    args = ap.parse_args()

    sections = from_jsons(JSON_CANDIDATES)
    if args.log:
        sections += from_log(args.log)
    if not sections:
        print("no e5-family output found; pass --log for an in-flight run")
        return

    print("=" * 104)
    print("1. DOES THE CONCENTRATION KNOB MOVE THE PROPOSED CARRIER?")
    print("=" * 104)
    print("   `flattening` = effective rank / rank, the carrier the e36 mechanism named.  The knob is")
    print("   `kappa`; its travel across the sweep is compared with the across-seed spread at the")
    print("   sweep's own starting point (`kappa` = 0), which is the noise the correlation sits on.\n")
    print(f"   {'section':<34}{'seed':>5}{'n':>3}{'flat k=0':>10}{'flat travel':>12}"
          f"{'seed sd at k=0':>16}{'travel/sd':>11}{'effrank k0->kmax':>19}")
    out: dict = {"sections": []}
    for sec in sections:
        rec = {"label": sec["label"], "per_seed": {}}
        rows = sec["rows"]
        for s in sorted({r["seed"] for r in rows}):
            mine = sorted((r for r in rows if r["seed"] == s), key=lambda r: r["kappa"])
            f = np.array([r["flatten"] for r in mine])
            e = np.array([r["effrank"] for r in mine])
            travel = float(f.max() - f.min())
            rec["per_seed"][str(s)] = {"n": len(mine), "flat_k0": float(f[0]),
                                       "flat_travel": travel,
                                       "effrank_k0": float(e[0]), "effrank_kmax": float(e[-1])}
        # the across-seed spread of flattening at kappa = 0, which is the noise floor for the knob
        k0 = [r["flatten"] for r in rows if r["kappa"] == 0.0]
        sd0 = float(np.std(k0, ddof=1)) if len(k0) > 1 else float("nan")
        rec["seed_sd_at_k0"] = sd0
        for s, v in rec["per_seed"].items():
            ratio = v["flat_travel"] / sd0 if sd0 and np.isfinite(sd0) else float("nan")
            v["travel_over_seed_sd"] = ratio
            verdict = "" if not np.isfinite(ratio) else (
                "INERT" if ratio < LEVERAGE_FLOOR else "has leverage")
            print(f"   {sec['label'][:33]:<34}{s:>5}{v['n']:>3}{v['flat_k0']:>10.4f}"
                  f"{v['flat_travel']:>+12.4f}{sd0:>16.5f}{ratio:>11.1f}"
                  f"{v['effrank_k0']:>10.2f} ->{v['effrank_kmax']:>6.2f}   {verdict}")
        out["sections"].append(rec)

    print()
    print("=" * 104)
    print("2. THE CORRELATION, PER SEED ONLY (rule 17: no pooling across an incomplete run)")
    print("=" * 104)
    print(f"   {'section':<34}{'seed':>5}{'n':>3}{'rho(gap, flat)':>17}{'p':>9}"
          f"{'rho(excess, flat)':>20}{'informative?':>15}")
    for sec in sections:
        rows = sec["rows"]
        for s in sorted({r["seed"] for r in rows}):
            mine = sorted((r for r in rows if r["seed"] == s), key=lambda r: r["kappa"])
            f = np.array([r["flatten"] for r in mine])
            g = np.array([r["gap"] for r in mine])
            x = np.array([r["excess"] for r in mine])
            complete = len(mine) == 7
            if len(mine) < 3 or np.ptp(f) == 0:
                continue
            rg, pg = spearmanr(f, g)
            rx = spearmanr(f, x)[0] if np.ptp(x) and np.all(np.isfinite(x)) else float("nan")
            sd0 = next(r["seed_sd_at_k0"] for r in out["sections"] if r["label"] == sec["label"])
            inert = np.isfinite(sd0) and (np.ptp(f) / sd0) < LEVERAGE_FLOOR
            tag = "over noise" if inert else ("yes" if complete else "partial")
            print(f"   {sec['label'][:33]:<34}{s:>5}{len(mine):>3}{rg:>+17.3f}{pg:>9.4f}"
                  f"{rx:>+20.3f}{tag:>15}")
            for r in out["sections"]:
                if r["label"] == sec["label"]:
                    r["per_seed"][str(s)]["rho_gap_flat"] = float(rg)
                    r["per_seed"][str(s)]["p_gap_flat"] = float(pg)
                    r["per_seed"][str(s)]["rho_excess_flat"] = float(rx)
                    r["per_seed"][str(s)]["informative"] = not inert and complete

    print()
    print("=" * 104)
    print("3. THE VERDICT THIS SUPPORTS")
    print("=" * 104)
    inert_secs = [r["label"] for r in out["sections"]
                  if any(not v.get("informative", False) and v.get("travel_over_seed_sd", 9e9)
                         < LEVERAGE_FLOOR for v in r["per_seed"].values())]
    for lab in sorted(set(inert_secs)):
        print(f"   {lab}: the knob is INERT here, so no correlation computed on it can test the")
        print(f"     mechanism in either direction.  Report it as untested, not as null.")
    print("\n   the structural point, which is the generalisable one: the mechanism was stated in")
    print("   terms of the rank collapse, and the rank collapse is what pins the carrier at the")
    print("   configuration that motivated it.  Check an intervention's travel on its own target")
    print("   variable *before* interpreting its result, and report where it is inert.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
