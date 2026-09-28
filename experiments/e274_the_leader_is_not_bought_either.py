"""E274 -- the one bit is not bought either: the leader of the three pairs needs 232 to 297 replicates, not ten.

`e272` priced the ordering claim and concluded that the register should state **one bit** -- which pair leads -- because
the three-way form needs 6,446 replicates while "the highest-against-lowest gap is 0.877, which needs 10 replicates and
is already resolved within the 144 the corpus has". **That is the wrong gap.** Which pair leads is decided by the gap
between the **top two**, not by the span from the top to the bottom -- and the span is large only because the *lowest*
pair is far below, which says nothing about the leader.

The two `e266` runs are the counter-example that exposes it: at sixteen replicates they have **different leaders**, so
the bit is not resolved at that budget, and the corpus's best-powered matrix at the same cell resolves its own leader
at **1.57σ** -- under the bar. So `e272`'s reassurance is corrected here, with the budget the leader actually needs.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **Y1 -- the two matched runs disagree about the leader.** At `seed0` 0 the top pair is `naive` against
  `ewc-block-rand` on **both** metrics (0.596 and 0.562); at `seed0` 100 it is the basis pair (0.589 and 0.573).
  **Falsifier**: the same leader in both.
- **Y2 -- and the corpus's best-powered matrix does not resolve it either.** At 144 replicates the basis pair leads by
  **0.177** on accuracy and **0.158** on forgetting, which is **1.57σ** and **1.39σ** against the gap's own standard
  error -- under the 2σ bar the rest of the register uses. **Falsifier**: 2σ or more on either metric.
- **Y3 -- so the budget is 232 to 297 replicates, not ten.** Those are the replicates at which the two metrics' top-two
  gaps reach 2σ, i.e. **about 12 to 15 hours** at the cell's measured rate -- more than the corpus's largest single run
  and 1.6 to 2 times the 144 it has. **Falsifier**: under 144 replicates needed.
- **Y4 -- and the gap `e272` used is the span, not the leader's.** The top-to-bottom span needs 10 replicates and the
  top-two gap needs 232, a factor of **23** -- so the two quantities are different questions and `e272`'s W3 conflated
  them. **Falsifier**: a factor under 5.

**What it cannot do**: the two metrics give different requirements (232 and 297), and nothing here says which is
binding for the register's practice; the top-two gap is measured in three matrices at one cell, so the required budget
is that cell's and not the corpus's; a leader established at 2σ is a leader at 95% and not a settled fact, and the
register's other claims use the same bar; the rate is a wall-clock average of three- and four-arm runs on one machine;
and no run is made, so the requirement is arithmetic and not a measurement.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json
from experiments.e272_the_budget_the_ordering_needs import PAIRS, n_for_gap, se_fisher

#: The reader's artifact carries both matched runs and the same cell's 144-replicate matrix.
READER = "runs/e266_matched_settings_read.json"
ACROSS = "runs/e178_rung_side_cs300_144reps.json"
METRICS = ("final_accuracy", "mean_forgetting")
CLAIMS = (
    ("Y1", "the two matched runs disagree about the leader",
     "The top pair at one seed is not the top pair at the other, on both metrics",
     "falsifier: the same leader in both runs"),
    ("Y2", "and the corpus's best-powered matrix does not resolve it either",
     "The top-two gap of the 144-replicate matrix is under two sigma on both metrics",
     "falsifier: two sigma or more"),
    ("Y3", "so the budget is 232 to 297 replicates, not ten",
     "The replicates at which the top-two gap reaches two sigma run from above 144 to under 1000",
     "falsifier: under 144 replicates needed"),
    ("Y4", "and the gap the earlier unit used is the span and not the leader's",
     "The top-to-bottom span needs at least five times fewer replicates than the top-two gap",
     "falsifier: a factor under five"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def matrices() -> dict:
    """Each matrix at the cell, with its three contrast pairs, and the clock per replicate."""
    d = load(READER)
    if d is None:
        return {}
    out = {}
    for name, by_metric in (d.get("readings") or {}).items():
        for metric, m in by_metric.items():
            corr = {tuple(k.split("/")): v for k, v in (m.get("corr") or {}).items()}
            c = {p: v for p, v in corr.items() if p in PAIRS}
            if len(c) < 3 or not m.get("n"):
                continue
            out[f"{name}/{metric}"] = {"n": m["n"], "corr": c}
    a = load(ACROSS)
    if a is not None and duration_seconds(a):
        out["_rate"] = duration_seconds(a) / len(a["methods"]["ewc-block"]["replicates"])
    return out


def leader(m: dict):
    """The top pair, its gap over the second, the sigma of that gap, and the replicates it needs at two sigma."""
    order = sorted(m["corr"], key=lambda p: -m["corr"][p])
    gap = m["corr"][order[0]] - m["corr"][order[1]]
    mid = (m["corr"][order[0]] + m["corr"][order[1]]) / 2.0
    sigma = gap / (math.sqrt(2.0) * se_fisher(mid, m["n"])) if gap > 0 else float("nan")
    return {"leader": order[0], "second": order[1], "gap": gap, "sigma": sigma,
            "needs": n_for_gap(gap, mid, m["n"]), "mid": mid}


def judge(rows: dict) -> list[dict]:
    out: list[dict] = []
    if len(rows) < 3:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the matrices are not on disk"} for c in CLAIMS]
    runs = {n: r for n, r in rows.items() if not n.startswith("_") and r["n"] <= 16}
    across = {n: r for n, r in rows.items() if not n.startswith("_") and r["n"] > 16}
    leaders = {n: leader(r) for n, r in runs.items()}

    disagree = []
    for metric in METRICS:
        got = {n: leaders[n]["leader"] for n in leaders if n.endswith(metric)}
        if len(got) >= 2 and len(set(got.values())) > 1:
            disagree.append((metric, got))
    out.append({"id": "Y1", "measured": "; ".join(f"{m}: " + ", ".join(f"{n.split('/')[0][-12:]} leads "
                                                                        f"{'/'.join(v)}" for n, v in got.items())
                                                  for m, got in disagree)
                if disagree else "the two runs agree about the leader",
                "verdict": "MET -- one configuration, two seeds, two leaders" if disagree else
                           "FALSIFIER FIRED -- the same leader in both runs"})

    if not across:
        out.append({"id": "Y2", "measured": "no powered matrix", "verdict": "REFUSED -- nothing above sixteen"})
        out.append({"id": "Y3", "measured": "", "verdict": "REFUSED -- nothing to price"})
        out.append({"id": "Y4", "measured": "", "verdict": "REFUSED -- nothing to compare"})
        return out
    big = {n: leader(r) for n, r in across.items()}
    under = [f"{n.split('/')[-1][:3]}: gap {v['gap']:.3f} at {v['sigma']:.2f} sigma" for n, v in big.items()]
    ok2 = all(v["sigma"] < 2.0 for v in big.values())
    out.append({"id": "Y2", "measured": "; ".join(under),
                "verdict": "MET -- the best-powered matrix's own leader is under two sigma" if ok2 else
                           "FALSIFIER FIRED -- a metric resolves its leader at two sigma"})

    needs = sorted(v["needs"] for v in big.values())
    ok3 = all(144 <= x < 1000 for x in needs)
    per = rows.get("_rate") or float("nan")
    out.append({"id": "Y3", "measured": f"the top-two gap needs {needs[0]:.0f} to {needs[-1]:.0f} replicates, "
                                        f"i.e. {needs[0] * per / 3600:.1f} to {needs[-1] * per / 3600:.1f} hours at "
                                        f"the measured {per:.0f} s per replicate, against the 144 the corpus has",
                "verdict": "MET -- the leader costs hundreds of replicates" if ok3 else
                           f"FALSIFIER FIRED -- {needs}"})

    spans = []
    for n, r in list(runs.items()) + list(across.items()):
        vals = sorted(r["corr"].values())
        spans.append(n_for_gap(vals[-1] - vals[0], (vals[-1] + vals[0]) / 2.0, r["n"]))
    factor = min(needs) / max(min(spans), 1e-9)
    out.append({"id": "Y4", "measured": f"the span needs as few as {min(spans):.0f} replicates where the top-two gap "
                                        f"needs {needs[0]:.0f} -- a factor of {factor:.0f}",
                "verdict": "MET -- the two quantities are different questions" if factor >= 5 else
                           f"FALSIFIER FIRED -- a factor of {factor:.1f}"})
    return out


def report(rows: dict) -> int:
    print("== each matrix at the cell, its leader and what that leader costs ==")
    per = rows.get("_rate")
    print(f"   the clock is {per:.1f} s per replicate\n" if per else "")
    print(f"   {'matrix':56} {'n':>4} {'leader':30} {'gap':>7} {'sigma':>7} {'needs':>7}")
    for name in sorted(n for n in rows if not n.startswith("_")):
        m, L = rows[name], leader(rows[name])
        print(f"   {name:56} {m['n']:4d} {'/'.join(L['leader']):30} {L['gap']:7.3f} {L['sigma']:7.2f} "
              f"{L['needs']:7.0f}")

    print("\n== the registered claims, Y1-Y4 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (which pair leads is decided by the gap between the TOP TWO, not by the span from the top to the")
    print("    bottom -- and e272's reassurance used the span, which is large only because the lowest pair is far")
    print("    below)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = matrices()
    if len([k for k in rows if not k.startswith("_")]) < 3:
        raise SystemExit(f"need {READER} -- it carries the two matched runs and the across-budget matrix")
    if args.json_out:
        write_json(args.json_out, {"reader": READER, "across": ACROSS,
                                   "matrices": {n: {"n": r["n"], "corr": {"/".join(k): v for k, v in r["corr"].items()}}
                                                for n, r in rows.items() if not n.startswith("_")},
                                   "seconds_per_replicate": rows.get("_rate"),
                                   "leaders": {n: leader(r) for n, r in rows.items() if not n.startswith("_")},
                                   "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
