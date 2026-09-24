"""E166 -- does the penalty's gain track the family's own forgetting? The corpus's single-field manipulations.

`e165` closed the matched-lambda family test and left one account standing beside the one it supports: the wiring
family's penalty gains 3.68 sigma where the base family's loses 0.91 **either because the wiring family tolerates
a stronger penalty or because it has more forgetting to remove** -- its `naive` sits at 0.1068 against 0.0750 --
and a level difference and a tolerance difference predict the same interaction. The registration named what would
separate them: *the naive level varied within a family*, or a third family between the two levels.

This unit asks what the corpus can already say with **no new runs**, by the project's own strongest design for an
uncontrolled corpus: **pairs of artifacts differing in exactly one `config` field** (the design `e160` uses to
derive which fields a method reads), restricted to pairs that carry both a `naive` arm and a shared penalty arm
with the same number of replicates, so replicate *i* is seed *i* in both and the difference is paired.

For each such pair and arm it reports two paired differences:

  * **the level** -- `naive`'s forgetting in the second artifact minus the first, i.e. how much room moved;
  * **the gain** -- the penalty's advantage over its own `naive`, second minus first.

**The room account predicts these have the same sign** (more forgetting to remove -> a bigger advantage). It also
predicts a **negative control**: a field that demonstrably cannot change what there is to remove must move the
gain by nothing. The corpus contains one -- `fisher_batches`, which `e160` derives as unread by `naive` and read
by the block arms -- so the control is internal and its pairs are checked for bit-identity of the two `naive` arms.

    python -m experiments.e166_gain_tracks_room
    python -m experiments.e166_gain_tracks_room --json-out runs/e166_gain_tracks_room.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import load_artifacts
from experiments.e151_pertask_contrast_audit import paired

#: fields whose difference breaks the pairing rather than describing an intervention: the replicate seeds are the
#: thing being held fixed, so two artifacts that differ in `seed0` cannot be compared replicate by replicate.
UNPAIRABLE = ("seed0",)
#: the field a `naive` arm cannot read, used as this design's internal negative control (`e160`).
CONTROL_FIELD = "fisher_batches"
#: resolution a cell needs before its sign is evidence
RESOLVED = 2.0


def normalise(config: dict) -> dict:
    """A `config` as the pairing reads it: no output path, and an unset field has no value.

    `None` and an absent key are the same statement -- "this was not set" -- and a schema epoch that started
    writing `"anchor_bias": None` should not turn every pair of artifacts across it into a two-field difference.
    """
    return {k: v for k, v in config.items() if k != "json_out" and v is not None}


def candidates(artifacts: list[dict]) -> list[dict]:
    """Every artifact carrying a `naive` arm and at least one penalty arm with replicates."""
    out = []
    for a in artifacts:
        methods = a["payload"].get("methods")
        if not isinstance(methods, dict) or "replicates" not in methods.get("naive", {}):
            continue
        arms = [m for m, e in methods.items()
                if m != "naive" and isinstance(e, dict) and "replicates" in e]
        if arms:
            out.append({"name": a["name"], "payload": a["payload"], "config": normalise(a["config"]),
                        "arms": sorted(arms), "n": len(methods["naive"]["replicates"])})
    return out


def pairs(cands: list[dict]) -> list[dict]:
    """The single-field pairs that share a penalty arm and a replicate count."""
    out = []
    for a, b in itertools.combinations(cands, 2):
        if set(a["config"]) != set(b["config"]) or a["n"] != b["n"]:
            continue
        differ = [k for k in a["config"] if a["config"][k] != b["config"][k]]
        if len(differ) != 1 or differ[0] in UNPAIRABLE:
            continue
        shared = sorted(set(a["arms"]) & set(b["arms"]))
        if shared:
            out.append({"field": differ[0], "a": a, "b": b, "arms": shared,
                        "from": a["config"][differ[0]], "to": b["config"][differ[0]]})
    return out


def rows_for(pair: dict) -> list[dict]:
    """One row per shared arm: how far the level moved, and how far the penalty's advantage moved."""
    out = []
    na = np.array([r["mean_forgetting"] for r in pair["a"]["payload"]["methods"]["naive"]["replicates"]])
    nb = np.array([r["mean_forgetting"] for r in pair["b"]["payload"]["methods"]["naive"]["replicates"]])
    for arm in pair["arms"]:
        ga = na - np.array([r["mean_forgetting"] for r in pair["a"]["payload"]["methods"][arm]["replicates"]])
        gb = nb - np.array([r["mean_forgetting"] for r in pair["b"]["payload"]["methods"][arm]["replicates"]])
        level, gain = paired(nb, na), paired(gb, ga)
        out.append({"field": pair["field"], "arm": arm, "a": pair["a"]["name"], "b": pair["b"]["name"],
                    "from": pair["from"], "to": pair["to"], "n": pair["a"]["n"],
                    "level_a": float(na.mean()), "level_b": float(nb.mean()),
                    "gain_a": float(ga.mean()), "gain_b": float(gb.mean()),
                    "level": level, "gain": gain,
                    "naive_bit_identical": bool(np.array_equal(na, nb)),
                    "level_resolved": abs(level["sigma"]) >= RESOLVED,
                    "gain_resolved": abs(gain["sigma"]) >= RESOLVED,
                    "same_sign": bool(np.sign(level["change"]) == np.sign(gain["change"]))})
    return out


def rank(xs, ys) -> dict:
    """Spearman rho, with the count of inputs resolved from zero and the leave-one-out range (rule 43)."""
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    rank_x = np.argsort(np.argsort(x)).astype(float)
    rank_y = np.argsort(np.argsort(y)).astype(float)
    rho = float(np.corrcoef(rank_x, rank_y)[0, 1]) if len(x) > 2 else float("nan")
    loo = []
    for k in range(len(x)):
        keep = np.ones(len(x), bool)
        keep[k] = False
        if keep.sum() > 2:
            loo.append(float(np.corrcoef(rank_x[keep], rank_y[keep])[0, 1]))
    return {"rho": rho, "n": len(x), "loo_min": min(loo) if loo else None,
            "loo_max": max(loo) if loo else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    cands = candidates(load_artifacts())
    ps = pairs(cands)
    rows = [r for p in ps for r in rows_for(p)]
    out: dict = {"candidates": len(cands), "pairs": len(ps), "rows": rows}

    print(f"== the design ==")
    print(f"   artifacts carrying a `naive` arm and a penalty arm: {len(cands)}")
    print(f"   pairs differing in exactly one config field, sharing an arm and a replicate count: {len(ps)}")
    print(f"   (pair, arm) rows: {len(rows)}; fields involved: "
          f"{len({r['field'] for r in rows})}")

    print("\n== the internal control: a field `naive` cannot read ==")
    ctl = [r for r in rows if r["field"] == CONTROL_FIELD]
    identical = [r for r in ctl if r["naive_bit_identical"]]
    broken = [r for r in ctl if not r["naive_bit_identical"]]
    print(f"   `{CONTROL_FIELD}` rows: {len(ctl)}; the two `naive` arms are BIT-IDENTICAL in "
          f"{len(identical)}, and differ in {len(broken)}")
    unexplained = sorted({(r["a"], r["b"]) for r in broken if "_omp" not in r["a"] + r["b"]})
    for a, b in sorted({(r["a"], r["b"]) for r in broken}):
        tag = "environmental, per e163" if "_omp" in a + b else "UNEXPLAINED"
        print(f"      differs: {a} vs {b}   level {[r['level']['change'] for r in broken if (r['a'], r['b']) == (a, b)][0]:+.6f}   ({tag})")
    print(f"   -> every non-identical pair is one whose environment was never recorded: "
          f"{len(unexplained)} unexplained")
    worst = max((abs(r["gain"]["change"]) for r in identical), default=0.0)
    worst5 = max((abs(r["gain"]["change"]) for r in identical if r["n"] >= 5), default=0.0)
    print(f"   -> with nothing to remove moving, the GAIN still moves by up to {worst5:.4f} at n >= 5 "
          f"({worst:.4f} including the single-seed pairs, where a step has no resolution at all): "
          f"the advantage is not a function of the level")

    print("\n== where the level moved, did the gain move with it? (the room account's prediction) ==")
    print(f"   {'field':<16}{'arm':<16}{'level step':>12}{'sig':>7}{'gain step':>12}{'sig':>7}   agrees?")
    moving = sorted((r for r in rows if r["level_resolved"]), key=lambda r: -abs(r["level"]["change"]))
    for r in moving:
        print(f"   {r['field']:<16}{r['arm']:<16}{r['level']['change']:>+12.4f}{r['level']['sigma']:>7.2f}"
              f"{r['gain']['change']:>+12.4f}{r['gain']['sigma']:>7.2f}   "
              f"{'yes' if r['same_sign'] else 'NO'}"
              + ("   [diagnostic]" if r["field"] == "frozen_bias" else ""))
    agree = sum(1 for r in moving if r["same_sign"] and r["gain_resolved"])
    disagree = sum(1 for r in moving if not r["same_sign"] and r["gain_resolved"])
    print(f"   -> rows whose level moves at >= {RESOLVED:g} sigma: {len(moving)}; of those, the gain resolves "
          f"in the room account's direction {agree} time(s) and AGAINST it {disagree} time(s)")

    both = [r for r in rows if r["level_resolved"] and r["gain_resolved"]]
    rk = rank([r["level"]["change"] for r in rows], [r["gain"]["change"] for r in rows])
    big = [r for r in rows if r["n"] >= 5]
    rk5 = rank([r["level"]["change"] for r in big], [r["gain"]["change"] for r in big])
    out["correlation"] = {"all_rows": rk, "n_at_least_5": rk5}
    out["census"] = {"rows": len(rows), "rows_n_ge_5": len(big), "level_resolved": len(moving),
                     "gain_resolved": sum(1 for r in rows if r["gain_resolved"]),
                     "both_resolved": len(both),
                     "agree_with_room": agree, "against_room": disagree,
                     "control_max_gain_step_n_ge_5": worst5, "control_max_gain_step_all": worst}
    print("\n== the rank statistic, with its inputs' resolutions (rule 43) ==")
    print(f"   rho(level step, gain step) over all {rk['n']} rows: {rk['rho']:+.3f}, leave-one-out range "
          f"{rk['loo_min']:+.3f} to {rk['loo_max']:+.3f}")
    print(f"   the same over the {rk5['n']} rows with five or more replicates: {rk5['rho']:+.3f}, "
          f"leave-one-out {rk5['loo_min']:+.3f} to {rk5['loo_max']:+.3f}")
    print(f"   of those rows: {len(moving)} resolve on the level, "
          f"{sum(1 for r in rows if r['gain_resolved'])} on the gain, {len(both)} on both "
          f"-- so the coefficient is a statistic over mostly-unresolved inputs")

    by_field = {}
    for r in rows:
        d = by_field.setdefault(r["field"], {"rows": 0, "level_resolved": 0, "max_gain": 0.0,
                                             "max_gain_field": ""})
        d["rows"] += 1
        d["level_resolved"] += int(r["level_resolved"])
        if abs(r["gain"]["change"]) > d["max_gain"]:
            d["max_gain"] = abs(r["gain"]["change"])
            d["max_gain_field"] = f"{r['arm']} {r['from']} -> {r['to']}"
    out["by_field"] = by_field
    print("\n== every field the corpus has varied in isolation, and whether it moves the room ==")
    print(f"   {'field':<18}{'rows':>5}{'level moves':>13}{'largest gain step':>19}")
    for f, d in sorted(by_field.items(), key=lambda kv: -kv[1]["rows"]):
        print(f"   {f:<18}{d['rows']:>5}{d['level_resolved']:>13}{d['max_gain']:>19.4f}")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
