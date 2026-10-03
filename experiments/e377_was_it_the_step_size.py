"""E377 -- was it the step size: the plastic body at the tight step with the head's step size ten times larger.

`e374` trained both drive sources at `cue@8` -- the last step `e368`'s curve says both channels are alive on this
draw -- and the action source read **0.2333**, chance, where the frozen probe reads **0.7617**. `e375` froze the
recurrent weights and recovered **0.2156 at 229.59 sigma**, and reported that the body's own training is what loses
the reading. `e376` then moved the head's step size on the **frozen** body by ten and found **+0.1965 at 64.92
sigma**, leaving the plastic-body claim with a hole it named: *"`e374`'s plastic body at `cue@8` trained to 0.2333
with the corpus's `lr = 3e-3`, and this unit shows that at this step that step size leaves a head 0.1965 short of
what a slightly larger one reaches. So part of what `e374` read as the body's training losing the reading may also
be the step size."*

**This unit runs the run that separates them**: the plastic body, the same cell, the same step size `e376` used. If
it learns, `e374`'s failure was at least partly where the steps were and this window's tight end is playable after
all; if it stays at chance, the loss is where `e375` put it and the body's plasticity is what costs.

Five claims, registered before the new run's reading was opened.

- **W1 -- and the run is one configuration on two pairs.** Against `e374`'s plastic run the new run differs in `lr`
  alone; against `e376`'s frozen-body stepped run it differs in `frozen_body` alone. Everything else -- circuit, tasks
  and widths, basis, read-out, replicate count, seed stream, iteration budget, batch, the world's dimension, leak,
  coupling and mode, the cue's step, the drive's source and its seven fields -- agrees in all three. **Falsifier**:
  any other field differing on either pair.
- **W2 -- and the licence: the world is live at this step.** `e368`'s curve reads the frozen action source at
  `cue@8` at least **0.10** above chance with a world spread above zero. **Falsifier**: within **0.05** of chance or
  a world at rest. **REFUSED** when that artifact is absent.
- **W3 -- and the step size was what `e374` was short of.** The new run's `naive` diagonal exceeds that unit's
  **0.2333** by at least **0.10**, paired over the twenty shared seeds. **Falsifier**: within **0.02**, which would
  say the step size is not what the plastic body was short of and `e374`'s failure is the body's own. **Null**:
  between. *This is the claim the unit exists for.*
- **W4 -- and the body's plasticity still costs something.** `e376`'s frozen-body stepped diagonal (**0.6455**)
  exceeds the new plastic one by at least **0.05**, paired. **Falsifier**: within **0.02**, which would say that
  with a step size that fits, a plastic body reaches a frozen one and `e375`'s **+0.2156** was a step-size effect.
  **Null**: between. W3 and W4 bracket the outcome: the first says the failure was the steps, the second says the
  body still loses something anyway, and both can hold at once.
- **W5 -- and the answer is earned.** Both arms' paired channel readings are at least **0.10** and positive at
  **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved.

**What it can do beyond that.** The four runs -- plastic at `3e-3`, plastic at `0.03`, frozen at `3e-3`, frozen at
`0.03` -- are a two-by-two on this cell, so what the body's plasticity costs and what the head's step size costs are
read off one table instead of across three units with three different comparisons in them.

**What it cannot do.** *One lever at one value*: ten times the default is a direction and not a dose, so where the
step size stops mattering is not measured, and a plastic run at chance here would not rule out a larger one
learning -- it would bound the effect between these two values. *One cell and one draw*: `cue@8` on this draw, whose
small world is what the account turns on, since the same default reaches above the probe at `cue@0` where the world
is four times larger. *And a plastic body at a larger step is a different training problem*: the gradient now flows
into the recurrent weights through a head building larger logits, so a resolved W3 is a statement about this pair of
settings and not a decomposition of the body's loss into independent parts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e371_the_game_the_agent_can_play import _sg, arm_reading, paired
from experiments.e376_the_heads_own_fitting import probe_cell

#: the run this unit made: the plastic body at the tight step with the head's step size at `e376`'s
STEPPED = Path("runs/e377_earned_label_lr03_cue8_actionsource_20reps.json")
#: the two runs it is a cell of: the same body at the corpus's step size, and the frozen body at this one
PLASTIC_BASE = Path("runs/e374_earned_label_cue8_actionsource_20reps.json")
FROZEN_STEPPED = Path("runs/e376_earned_label_frozenbody_lr03_cue8_actionsource_20reps.json")
CURVE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
SOURCE, STEP = "action", 8
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COUPLING_SHA1 = "5326f4a0edb4"
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
STEPS_UP = 0.10
SAME = 0.02
STILL_COSTS = 0.05
CLAIMS = (
    ("W1", "and the run is one configuration on two pairs",
     "Against `e374`'s plastic run the new run differs in `lr` alone, and against `e376`'s frozen-body run in "
     "`frozen_body` alone, with every other field agreeing across all three",
     "falsifier: any other field differing on either pair"),
    ("W2", f"and the world is live at this step, {LEARNS:.2f} over chance",
     "`e368`'s curve reads the frozen action source at cue@8 at least 0.10 above chance with a world spread above "
     "zero",
     "falsifier: within 0.05 of chance or a world at rest; refused when that artifact is absent"),
    ("W3", f"and the step size was what `e374` was short of, by {STEPS_UP:.2f}",
     "The new `naive` diagonal exceeds `e374`'s 0.2333 by at least 0.10, paired over the shared seeds",
     f"falsifier: within {SAME:.2f}; null: between {SAME:.2f} and {STEPS_UP:.2f}"),
    ("W4", f"and the body's plasticity still costs something, by {STILL_COSTS:.2f}",
     "`e376`'s frozen-body stepped diagonal exceeds the new plastic one by at least 0.05, paired",
     f"falsifier: within {SAME:.2f}, which would make `e375`'s 0.2156 a step-size effect; null: between "
     f"{SAME:.2f} and {STILL_COSTS:.2f}"),
    ("W5", f"and the answer is earned, {LEARNS:.2f} at {SIGMA:.0f} sigma",
     "Both arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def facts_with_knobs(run: dict | None) -> dict | None:
    if not run:
        return None
    out = dict(_facts(run))
    cfg = run.get("config") or {}
    out["lr"] = cfg.get("lr")
    out["batch"] = cfg.get("batch")
    out["frozen_body"] = bool(cfg.get("frozen_body"))
    out["frozen_bias"] = bool(cfg.get("frozen_bias"))
    return out


def reading(stepped_path: Path = STEPPED, plastic_path: Path = PLASTIC_BASE,
            frozen_path: Path = FROZEN_STEPPED, curve: Path = CURVE) -> dict:
    stepped, plastic, frozen = load(stepped_path), load(plastic_path), load(frozen_path)
    runs = {"stepped": stepped, "plastic": plastic, "frozen": frozen}
    out = {"rows": {f"{k}_{a}": arm_reading(v, a) for k, v in runs.items() for a in ARMS},
           "facts": {k: facts_with_knobs(v) for k, v in runs.items()},
           "runs": {"stepped": Path(stepped_path).name, "plastic": Path(plastic_path).name,
                    "frozen": Path(frozen_path).name},
           "present": {k: v is not None for k, v in runs.items()},
           "ok": {k: v is not None and all(arm_reading(v, a).get("ok") for a in ARMS) for k, v in runs.items()},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES,
           "probe": probe_cell(curve, SOURCE, STEP), "over_steps": None, "body_cost": None}
    if out["ok"]["stepped"] and out["ok"]["plastic"]:
        out["over_steps"] = paired(out["rows"][f"stepped_{NAIVE}"]["diagonal"],
                                   out["rows"][f"plastic_{NAIVE}"]["diagonal"])
    if out["ok"]["stepped"] and out["ok"]["frozen"]:
        out["body_cost"] = paired(out["rows"][f"frozen_{NAIVE}"]["diagonal"],
                                  out["rows"][f"stepped_{NAIVE}"]["diagonal"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok, present = r.get("rows") or {}, r.get("ok") or {}, r.get("present") or {}
    if not ok.get("stepped"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the stepped plastic run is not on disk"}
                for c in CLAIMS]

    fs, fp, ff = r["facts"]["stepped"], r["facts"]["plastic"], r["facts"]["frozen"]
    keys = ("lr", "batch", "frozen_body", "frozen_bias") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)

    def _diff(a, b):
        if not a or not b:
            return {"missing": True}
        return {k: [a.get(k), b.get(k)] for k in keys if a.get(k) != b.get(k)}

    if not (present.get("plastic") and present.get("frozen")):
        j1 = {"id": "W1", "measured": f"the runs to compare against are `{r['runs']['plastic']}` "
                                      f"(present {bool(present.get('plastic'))}) and `{r['runs']['frozen']}` "
                                      f"(present {bool(present.get('frozen'))})",
              "verdict": "REFUSED -- a run this unit is a cell of is absent"}
    else:
        vs_plastic = _diff(fs, fp)
        vs_frozen = _diff(fs, ff)
        good = (list(vs_plastic) == ["lr"] and vs_plastic["lr"] == [0.03, 0.003]
                and list(vs_frozen) == ["frozen_body"] and vs_frozen["frozen_body"] == [False, True]
                and fs.get("repeats") == REPLICATES and fs.get("world_coupling_sha1") == COUPLING_SHA1
                and fs.get("loop_cue_at") == STEP
                and rows[f"stepped_{NAIVE}"]["n"] == REPLICATES and rows[f"stepped_{REPLAY}"]["n"] == REPLICATES)
        lrs = [fp and fp.get("lr"), fs.get("lr"), ff and ff.get("lr")]
        frozen_flags = [fp and fp.get("frozen_body"), fs.get("frozen_body"), ff and ff.get("frozen_body")]
        j1 = {"id": "W1", "measured": f"`{r['runs']['stepped']}` against `{r['runs']['plastic']}` differing "
                                      f"{vs_plastic} and against `{r['runs']['frozen']}` differing {vs_frozen}; "
                                      f"learning rates {lrs}, bodies frozen {frozen_flags}, iterations "
                                      f"{fs.get('iters')}, cue step {fs.get('loop_cue_at')}, coupling "
                                      f"{fs.get('world_coupling_sha1')}",
              "verdict": "MET -- one configuration on both pairs" if good else
              f"FALSIFIER FIRED -- against the plastic run {vs_plastic}, against the frozen one {vs_frozen}"}

    pz = r.get("probe")
    if not pz:
        j2 = {"id": "W2", "measured": "the curve has no cell for this step",
              "verdict": "REFUSED -- the artifact this unit's licence comes from is absent"}
    else:
        above = pz["accuracy"] - 0.25
        j2 = {"id": "W2", "measured": f"`{pz['artifact']}` reads {SOURCE}@{STEP} at {pz['accuracy']:.4f}, "
                                      f"{above:+.4f} over a chance of 0.25, on a world with spread "
                                      f"{pz['world_sd']:.4f}",
              "verdict": f"MET -- the world is live at this step, {above:+.4f} over chance" if
              above >= LEARNS and pz["world_sd"] > 0.0 else
              f"FALSIFIER FIRED -- {above:+.4f} over chance on a world with spread {pz['world_sd']:.4f}"}

    naive = rows[f"stepped_{NAIVE}"]
    over = r.get("over_steps") or {"delta": None}
    if over.get("delta") is None:
        j3 = {"id": "W3", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the two runs do not pair"}
    else:
        j3 = {"id": "W3", "measured": f"the plastic body with the step size at {fs.get('lr')} reads "
                                      f"{naive['mean_diagonal']:.4f} against {rows[f'plastic_{NAIVE}']['mean_diagonal']:.4f} "
                                      f"at the corpus's {fp.get('lr')}, so the larger step is worth "
                                      f"{over['delta']:+.4f} on a sem of {over['sem']:.4f} "
                                      f"({_sg(over['sigma'])} sigma) over {over['n']} paired replicates",
              "verdict": f"MET -- the step size was what the plastic body was short of, by {over['delta']:+.4f}" if
              over["delta"] >= STEPS_UP else
              f"FALSIFIER FIRED -- the larger step is worth only {over['delta']:+.4f}: the plastic body's failure is "
              f"its own" if over["delta"] < SAME else
              f"NULL -- {over['delta']:+.4f}, between {SAME:.2f} and {STEPS_UP:.2f}"}

    cost = r.get("body_cost") or {"delta": None}
    if cost.get("delta") is None:
        j4 = {"id": "W4", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the frozen run does not pair with this one"}
    else:
        j4 = {"id": "W4", "measured": f"the frozen body at this step size reads "
                                      f"{rows[f'frozen_{NAIVE}']['mean_diagonal']:.4f} and the plastic one "
                                      f"{naive['mean_diagonal']:.4f}, so the body's plasticity is still worth "
                                      f"{cost['delta']:+.4f} on a sem of {cost['sem']:.4f} "
                                      f"({_sg(cost['sigma'])} sigma) paired",
              "verdict": f"MET -- the body's plasticity still costs {cost['delta']:+.4f}" if
              cost["delta"] >= STILL_COSTS else
              f"FALSIFIER FIRED -- with a step size that fits, the plastic body is within {SAME:.2f} of the frozen "
              f"one, {cost['delta']:+.4f}: `e375`'s cost was a step-size effect" if cost["delta"] < SAME else
              f"NULL -- {cost['delta']:+.4f}, between {SAME:.2f} and {STILL_COSTS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'stepped_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'stepped_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"stepped_{a}"]["paired"]["delta"] is not None
                                    and rows[f"stepped_{a}"]["paired"]["delta"] >= LEARNS
                                    and (rows[f"stepped_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j5 = {"id": "W5", "measured": f"the stepped plastic run's paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- the answer is earned, in both arms" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not (r.get("ok") or {}).get("stepped"):
        print("== was it the step size ==\n   REFUSED -- the stepped plastic run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== was it the step size ==")
    print(f"   the same cell at cue@{STEP} with the drive on the agent's own action, in the corpus's own head at two "
          f"step sizes and a plastic against a frozen body")
    print(f"\n   {'body':>8} {'lr':>6} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} "
          f"{'sigma':>6}")
    for key, row in r["rows"].items():
        which = key.split("_", 1)[0]
        print(f"   {which:>8} {str(r['facts'][which].get('lr')):>6} {row['arm']:>7} {row['mean_final']:8.4f} "
              f"{row['mean_diagonal']:9.4f} {row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} "
              f"{_sg(row['paired']['sigma']):>6}")
    if r.get("probe"):
        print(f"   the closed-form probe on the untrained body in `{r['probe']['artifact']}` reads "
              f"{r['probe']['accuracy']:.4f} on a world with spread {r['probe']['world_sd']:.4f}")

    print("\n== the registered claims, W1-W5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e374` trained this cell at the corpus's step size and read chance; `e375` and `e376` priced the")
    print("    body's training and the head's steps on frozen bodies, and both named this run as the one that")
    print("    separates them)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stepped", type=Path, default=STEPPED)
    ap.add_argument("--plastic", type=Path, default=PLASTIC_BASE)
    ap.add_argument("--frozen", type=Path, default=FROZEN_STEPPED)
    ap.add_argument("--curve", type=Path, default=CURVE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(stepped_path=args.stepped, plastic_path=args.plastic, frozen_path=args.frozen, curve=args.curve)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
