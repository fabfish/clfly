"""E427 -- most of the aid needs a plastic bias: one flag apart, the buffer keeps a quarter of what it was worth.

`e417` read the corpus's frozen-**body** cells and found the buffer worth nothing when the recurrent weights never
move. The corpus carries the finer control too: one configuration rolled twice at forty replicates with
`config.frozen_bias` the only field that differs, so the head's bias is the one thing that may or may not move. Two
more suites were rolled under the frozen bias at the same depth.

**This unit reads all four.** The plastic/frozen-bias pair and the two extra frozen-bias suites, each arm against its
own roll's `naive`: what the buffer's accuracy gain and forgetting cut are worth when the bias cannot move, and what
happens to the arm that does nothing. No training, no probe. Five claims, registered before this unit's pass over the
runs.

- **BC1 -- and the ledger is carried.** One configuration rolled twice with `frozen_bias` alone differing, at **40**
  replicates with `naive`, `replay` and the three penalties, plus at least two more frozen-bias suites at the same
  depth. **Falsifier**: any other field differing, a missing arm, or fewer replicates.
- **BC2 -- and the freeze takes most of the buffer's accuracy gain.** The frozen pair's `replay` gain over its own
  `naive` is at most **half** the plastic pair's. **Falsifier**: above **0.7**; **null**: between.
- **BC3 -- and most of its forgetting cut too.** The frozen pair's cut is at most **half** the plastic pair's.
  **Falsifier**: above **0.7**; **null**: between. *BC2 and BC3 are the unit's own prediction: `e417` found the aid
  needing a movable body, and the bias is the smallest movable part of it.*
- **BC4 -- and the freeze changes the arm that does nothing.** The frozen pair's `naive` arm forgets **less** than the
  plastic one's. **Falsifier**: the frozen `naive` forgetting at or above the plastic one's.
- **BC5 -- and the frozen buffer's small gain is a constant of the suite.** Over the three frozen-bias suites the
  `replay` gain spans at most **0.01**. **Falsifier**: any suite's gain at or above the plastic pair's, or a span
  above **0.03**.

**What it can do beyond that.** It says which part of the aid is plastic: with one flag, the buffer's accuracy gain
falls from **+0.0484** to **+0.0130** and its forgetting cut from **0.0784** to **0.0208** -- a quarter of each --
while the arm that does nothing has its own forgetting fall from **0.0750** to **0.0227**. So the bias is where the
corpus's drift lives as well as most of the buffer's worth, and the frozen-bias gain is a constant of the suite
(**+0.0130**, **+0.0145**, **+0.0158** over three).

**What it cannot do.** *One configuration pair and three suites*: the plastic side of the comparison is a single
configuration at overlap 0.0, so nothing here says how the frozen-bias result moves with the overlap or the circuit
size. *And one control*: `frozen_bias` is the corpus's own flag; nothing here freezes the head's weights but not its
bias, or the bias but not the body, beyond what the corpus ran. *And the suites are the overlap family*: all four are
the class-incremental line at `circuit_size` 800, so the earned-label world's frozen-bias behaviour is not in this
reading. *And the metric is the corpus's*: `mean_forgetting` is the diagonal minus the last row, which `e305` showed
cannot see the part an arm never learned. *And a ledger is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the one configuration rolled both ways, and the two further suites rolled under the frozen bias
PAIR = (Path("runs/e140_r32_methods_frozenbias_40reps.json"), Path("runs/e140_r32_methods_plastic_40reps.json"))
SUITES = {"suite600": Path("runs/e275_frozenbias_suite600_40reps.json"),
          "suite1440": Path("runs/e287_frozenbias_suite1440_40reps.json")}
FROZEN_FLAG = "frozen_bias"
RUN_FIELDS = ("json_out", "save_theta")
BASELINE = "naive"
BUFFER = "replay"
MIN_ARMS = 4
MIN_REPS = 40
MIN_SUITES = 2
HALF = 0.5
HALF_FIRES = 0.7
SPAN = 0.01
SPAN_FIRES = 0.03
CLAIMS = (
    ("BC1", f"and the ledger is carried, over {MIN_ARMS} arms at {MIN_REPS} replicates",
     "One configuration rolled twice with frozen_bias alone differing, at forty replicates with naive, replay and the "
     "three penalties, plus at least two more frozen-bias suites at the same depth",
     "falsifier: any other field differing, a missing arm, or fewer replicates"),
    ("BC2", f"and the freeze takes most of the buffer's accuracy gain, to {HALF:.0%}",
     "The frozen pair's replay gain over its own naive is at most half the plastic pair's",
     f"falsifier: above {HALF_FIRES:.1f}; null: between"),
    ("BC3", f"and most of its forgetting cut too, to {HALF:.0%}",
     "The frozen pair's cut is at most half the plastic pair's",
     f"falsifier: above {HALF_FIRES:.1f}; null: between"),
    ("BC4", "and the freeze changes the arm that does nothing",
     "The frozen pair's naive arm forgets less than the plastic one's",
     "falsifier: the frozen naive forgetting at or above the plastic one's"),
    ("BC5", f"and the frozen buffer's small gain is a constant of the suite, within {SPAN:.2f}",
     "Over the three frozen-bias suites the replay gain spans at most 0.01",
     f"falsifier: any suite's gain at or above the plastic pair's, or a span above {SPAN_FIRES:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    if BASELINE not in methods:
        return None
    reps = (methods.get(BASELINE) or {}).get("replicates") or []
    if not reps:
        return None
    base_acc = statistics.fmean([r["final_accuracy"] for r in reps])
    base_mf = statistics.fmean([r["mean_forgetting"] for r in reps])
    arms = {}
    for arm in sorted(methods):
        got = (methods.get(arm) or {}).get("replicates") or []
        if not got:
            continue
        arms[arm] = {"replicates": len(got),
                     "accuracy": statistics.fmean([r["final_accuracy"] for r in got]),
                     "mean_forgetting": statistics.fmean([r["mean_forgetting"] for r in got])}
        arms[arm]["gain"] = arms[arm]["accuracy"] - base_acc
        arms[arm]["cut"] = base_mf - arms[arm]["mean_forgetting"]
    return {"artifact": path.name, "naive": {"accuracy": base_acc, "mean_forgetting": base_mf}, "arms": arms,
            "frozen_bias": bool((doc.get("config") or {}).get(FROZEN_FLAG)), "doc": doc}


def reading(pair=PAIR, suites: dict = SUITES) -> dict:
    out = {"ok": True, "reason": None, "pair": {}, "suites": {}}
    frozen, plastic = _roll(pair[0]), _roll(pair[1])
    if frozen is None:
        return {**out, "ok": False, "reason": f"{pair[0]} is absent or carries no naive arm"}
    if plastic is None:
        return {**out, "ok": False, "reason": f"{pair[1]} is absent or carries no naive arm"}
    ca, cb = (frozen["doc"].get("config") or {}), (plastic["doc"].get("config") or {})
    differing = sorted(k for k in set(ca) | set(cb) if k not in RUN_FIELDS and ca.get(k) != cb.get(k))
    out["pair"] = {"frozen": frozen, "plastic": plastic, "differing_config": differing,
                   "same_draws": all(json.dumps(frozen["doc"].get(k), sort_keys=True)
                                     == json.dumps(plastic["doc"].get(k), sort_keys=True)
                                     for k in ("circuit", "readout", "tasks", "env_draw"))}
    for name, path in (suites or {}).items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"suite {name}: {path} is absent or carries no naive arm"}
        if not got["frozen_bias"]:
            return {**out, "ok": False, "reason": f"suite {name}: {path} does not record a frozen bias"}
        out["suites"][name] = got
    rolls = [out["pair"]["frozen"]] + list(out["suites"].values())
    buffer_gains = [r["arms"][BUFFER]["gain"] for r in rolls if BUFFER in r["arms"]]
    out["spans"] = {"pair_replicates": sorted({frozen["arms"][BUFFER]["replicates"],
                                               plastic["arms"][BUFFER]["replicates"]}),
                    "frozen_suites": len(out["suites"]),
                    "arms": sorted(frozen["arms"]),
                    "frozen_gain": frozen["arms"][BUFFER]["gain"], "plastic_gain": plastic["arms"][BUFFER]["gain"],
                    "frozen_cut": frozen["arms"][BUFFER]["cut"], "plastic_cut": plastic["arms"][BUFFER]["cut"],
                    "frozen_naive_mf": frozen["naive"]["mean_forgetting"],
                    "plastic_naive_mf": plastic["naive"]["mean_forgetting"],
                    "gain_ratio": (frozen["arms"][BUFFER]["gain"] / plastic["arms"][BUFFER]["gain"])
                    if plastic["arms"][BUFFER]["gain"] else None,
                    "cut_ratio": (frozen["arms"][BUFFER]["cut"] / plastic["arms"][BUFFER]["cut"])
                    if plastic["arms"][BUFFER]["cut"] else None,
                    "suite_gain_span": (max(buffer_gains) - min(buffer_gains)) if buffer_gains else None}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no naive arm"}
                for c in CLAIMS]
    pair, s = r["pair"], r["spans"]
    broken = pair["differing_config"] != [FROZEN_FLAG] or not pair["same_draws"]
    thin = {k: v for k, v in (("frozen", pair["frozen"]), ("plastic", pair["plastic"]))
            if any(a["replicates"] < MIN_REPS for a in v["arms"].values())}
    j1 = {"id": "BC1",
          "measured": f"the pair rolled at {s['pair_replicates']} replicates with `config` differing in "
                      f"{pair['differing_config']} alone and the draws identical, beside {s['frozen_suites']} "
                      f"further frozen-bias suites; the arms are {s['arms']}",
          "verdict": f"MET -- the ledger is carried over {len(s['arms'])} arms at {MIN_REPS} replicates and "
                     f"{s['frozen_suites'] + 1} frozen-bias rolls" if
                     (not broken and not thin and len(s["arms"]) >= MIN_ARMS and s["frozen_suites"] >= MIN_SUITES)
                     else f"FALSIFIER FIRED -- {broken or thin or s['frozen_suites']}"}
    ratio = s["gain_ratio"]
    j2 = {"id": "BC2",
          "measured": f"the buffer's accuracy gain is {s['frozen_gain']:+.4f} under the frozen bias against "
                      f"{s['plastic_gain']:+.4f} under the plastic one, {ratio:.2f} of it" if ratio is not None else
                      "the plastic pair's gain is zero, so the ratio is undefined",
          "verdict": f"MET -- the freeze takes the buffer's accuracy gain to {ratio:.2f} of the plastic one" if
                     (ratio is not None and ratio <= HALF) else
                     f"FALSIFIER FIRED -- {ratio} is over the bar" if (ratio is None or ratio > HALF_FIRES) else
                     f"NULL -- {ratio:.2f}, between {HALF:.2f} and {HALF_FIRES:.2f}"}
    cratio = s["cut_ratio"]
    j3 = {"id": "BC3",
          "measured": f"its forgetting cut is {s['frozen_cut']:+.4f} under the frozen bias against "
                      f"{s['plastic_cut']:+.4f} under the plastic one, {cratio:.2f} of it" if cratio is not None else
                      "the plastic pair's cut is zero, so the ratio is undefined",
          "verdict": f"MET -- the freeze takes the buffer's forgetting cut to {cratio:.2f} of the plastic one" if
                     (cratio is not None and cratio <= HALF) else
                     f"FALSIFIER FIRED -- {cratio} is over the bar" if (cratio is None or cratio > HALF_FIRES) else
                     f"NULL -- {cratio:.2f}, between {HALF:.2f} and {HALF_FIRES:.2f}"}
    j4 = {"id": "BC4",
          "measured": f"the naive arm's own mean forgetting is {s['frozen_naive_mf']:.4f} under the frozen bias "
                      f"against {s['plastic_naive_mf']:.4f} under the plastic one",
          "verdict": f"MET -- the freeze changes the arm that does nothing: its forgetting falls by "
                     f"{s['plastic_naive_mf'] - s['frozen_naive_mf']:+.4f}" if
                     s["frozen_naive_mf"] < s["plastic_naive_mf"] else
                     f"FALSIFIER FIRED -- {s['frozen_naive_mf']:.4f} is not below {s['plastic_naive_mf']:.4f}"}
    suite_gains = {n: round(v["arms"][BUFFER]["gain"], 4) for n, v in r["suites"].items()}
    above = {n: g for n, g in suite_gains.items() if g >= s["plastic_gain"]}
    j5 = {"id": "BC5",
          "measured": f"the frozen-bias suites' buffer gains are { {n: round(v['arms'][BUFFER]['gain'], 4) for n, v in r['suites'].items()} } beside the pair's "
                      f"{s['frozen_gain']:+.4f}, spanning {s['suite_gain_span']:.4f}",
          "verdict": f"MET -- the frozen buffer's gain spans {s['suite_gain_span']:.4f} over the suites and stays "
                     f"under the plastic gain" if (not above and s["suite_gain_span"] <= SPAN) else
                     f"FALSIFIER FIRED -- {above or s['suite_gain_span']}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== most of the aid needs a plastic bias ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"   `{r['pair']['frozen']['artifact']}` against `{r['pair']['plastic']['artifact']}`, `config` differing "
          f"in {r['pair']['differing_config']} alone")
    print(f"\n   {'roll':>26} {'naive acc':>10} {'naive mf':>9} {'buffer gain':>12} {'buffer cut':>11} {'arms':>5}")
    for label, roll in [("pair/frozen", r["pair"]["frozen"]), ("pair/plastic", r["pair"]["plastic"])] + \
            [(f"suite/{n}", v) for n, v in r["suites"].items()]:
        print(f"   {label:>26} {roll['naive']['accuracy']:10.4f} {roll['naive']['mean_forgetting']:9.4f} "
              f"{roll['arms'][BUFFER]['gain']:+12.4f} {roll['arms'][BUFFER]['cut']:+11.4f} {len(roll['arms']):5d}")
    s = r["spans"]
    print(f"\n   the freeze takes the buffer's gain to {s['gain_ratio']:.2f} of the plastic one and its cut to "
          f"{s['cut_ratio']:.2f}; the naive arm's own forgetting falls {s['plastic_naive_mf'] - s['frozen_naive_mf']:+.4f}")
    print("\n== the registered claims, BC1-BC5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e417` found the buffer worth nothing when the recurrent body never moves; this asks the same of the")
    print("    head's bias alone, on one configuration rolled both ways)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
