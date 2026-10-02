"""E374 -- the tightest step: what acting costs where both channels are live and the margin is nearly gone.

`e373` priced acting at every step `e363`'s grid holds and drew a line under the table it could not cross: at
`cue@0` both drive sources have a live channel and the price is **0.0708**; at `cue@10` the action source's world is
**at rest** (`e368`) so the 0.5977 frozen gap there is a live channel against a dead one and not a price of acting;
at `cue@11` both are at chance and there is no task. **Nothing in the corpus measured the price at a step where both
channels are live and the margin is short**, and `e373` named it as the unit it was pointing at.

**This unit trains that step.** `e368`'s curve puts the action source's boundary between steps **8** and **9** on
this draw: at `cue@8` its world still reads **0.7617** with a spread of **0.0478**, and at `cue@9` the spread is
exactly **0.0**. So `cue@8` is the last step where both sources have something to read and the cue arrives with the
least room it can have -- two runs, `e371`'s and `e372`'s exact flags with `--loop-cue-at 8`, twenty replicates
each, compared with each other and with the same two sources' runs at `cue@0`.

Five claims, registered before either new run's reading was opened.

- **T1 -- one configuration at both steps.** The two `cue@8` runs agree on every shared field with the drive's
  source and the seven fields that follow from it the only differences, and each agrees with its own source's
  `cue@0` run on every shared field with the cue's step alone differing. Couplings: `1b7d09f2b469` for the cue
  source, `5326f4a0edb4` for the action source. **Falsifier**: any other field differing anywhere in the four.
- **T2 -- and the licence: both channels are live at this step.** `e368`'s curve records the frozen action source at
  `cue@8` at least **0.10** above chance **and** with a world spread above zero, and the frozen cue source at least
  **0.10** above chance. **Falsifier**: either cell at chance, or the action cell's world at rest, which would make
  this step the boundary itself and the price a live-against-dead gap again. **REFUSED** when that artifact is
  absent. *This is what makes the step the one `e373` asked for.*
- **T3 -- and both games are learnable.** Each source's `naive` diagonal is at least **0.10** above chance.
  **Falsifier**: either within **0.05** of chance.
- **T4 -- and the price is larger here than where the window is widest.** The paired cost of acting at `cue@8` --
  this unit's cue-source diagonal minus its action-source one -- exceeds the same quantity at `cue@0` by at least
  **0.05**. **Falsifier**: within **0.02**, which would say the price of acting does not depend on the margin inside
  the window at all. **Null**: between. *This is the claim the unit exists for.*
- **T5 -- and the answer is earned in both sources.** Each source's paired channel reading is at least **0.10** and
  positive at **2 sigma**. **Falsifier**: a source below 0.10, at or below zero, or unresolved. Without this the
  same-step comparison could be two runs that simply train on the suite.

**What it can do beyond that.** The three steps now trained at both sources -- **0**, **8** and **10**, with **11**
at zero margin -- make the price a shape over the whole window rather than two ends and a boundary, and `e368`'s own
curve says where the fourth point falls.

**What it cannot do.** *One draw*: the boundary at 8 is this population draw's, and `e370` showed the distance and
so the boundary move with the draw, so a different draw's last live step is a different cell, and nothing here is a
statement about the modal one. *Two more steps and still not a curve*: with `cue@0` and `cue@8` the window has two
points where both channels live, which is a line and not a curve. *And the price is a diagonal*: both new runs
carry retention matrices, per-task records and channel readings, and this unit reads the level each task reached.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e371_the_game_the_agent_can_play import _sg, arm_reading, paired

#: the two runs this unit made, and the two sources' runs at the widest step they are compared with
CUE_TIGHT = Path("runs/e374_earned_label_cue8_cuesource_20reps.json")
ACTION_TIGHT = Path("runs/e374_earned_label_cue8_actionsource_20reps.json")
CUE_WIDE = Path("runs/e372_earned_label_cue0_cuesource_20reps.json")
ACTION_WIDE = Path("runs/e371_earned_label_cue0_actionsource_20reps.json")
#: `e368`'s curve, which holds the frozen reading at every cue step and so at this one
CURVE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
SOURCES = ("cue", "action")
NAIVE = "naive"
TIGHT_STEP, WIDE_STEP = 8, 0
REPLICATES = 20
CUE_COUPLING = "1b7d09f2b469"
ACTION_COUPLING = "5326f4a0edb4"
LEARNS = 0.10
FLAT = 0.05
GROWS = 0.05
SAME = 0.02
CARRIES = 0.10
SIGMA = 2.0
CLAIMS = (
    ("T1", "one configuration at both steps",
     "The two cue@8 runs agree on every shared field with the drive's source and its seven fields the only "
     "differences, and each agrees with its own source's cue@0 run with the cue's step alone differing",
     "falsifier: any other field differing anywhere in the four"),
    ("T2", f"and both channels are live at this step, {LEARNS:.2f} over chance",
     "`e368`'s curve records the frozen action source at cue@8 at least 0.10 above chance with a world spread above "
     "zero, and the frozen cue source at least 0.10 above chance",
     "falsifier: either cell at chance, or the action cell's world at rest; refused when that artifact is absent"),
    ("T3", f"and both games are learnable, {LEARNS:.2f} over chance",
     "Each source's `naive` diagonal is at least 0.10 above chance",
     f"falsifier: either within {FLAT:.2f} of chance"),
    ("T4", f"and the price is larger here than where the window is widest, by {GROWS:.2f}",
     "The paired cost of acting at cue@8 exceeds the same quantity at cue@0 by at least 0.05",
     f"falsifier: within {SAME:.2f}; null: between {SAME:.2f} and {GROWS:.2f}"),
    ("T5", f"and the answer is earned in both sources, {CARRIES:.2f} at {SIGMA:.0f} sigma",
     "Each source's paired channel reading is at least 0.10 and positive at 2 sigma",
     "falsifier: a source below 0.10, at or below zero, or unresolved"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def curve_cells(path: Path = CURVE) -> dict:
    """`e368`'s per-step cells, keyed `source@step`, which are the frozen readings at every margin."""
    doc = load(path)
    if not doc:
        return {}
    out = {}
    for key, cell in (doc.get("cells") or {}).items():
        source, _, step = key.partition("@")
        out[(source, int(step))] = {"accuracy": float(cell["accuracy"]), "world_sd": float(cell["world_sd"]),
                                    "trial_range": float(cell.get("trial_range", 0.0))}
    return out


def _pair(cue: dict | None, action: dict | None) -> dict | None:
    if cue is None or action is None:
        return None
    return paired(arm_reading(cue, NAIVE)["diagonal"], arm_reading(action, NAIVE)["diagonal"])


def reading(tight=(CUE_TIGHT, ACTION_TIGHT), wide=(CUE_WIDE, ACTION_WIDE), curve: Path = CURVE) -> dict:
    runs = {("cue", TIGHT_STEP): load(tight[0]), ("action", TIGHT_STEP): load(tight[1]),
            ("cue", WIDE_STEP): load(wide[0]), ("action", WIDE_STEP): load(wide[1])}
    out = {"runs": {f"{s}@{t}": (runs[(s, t)].get("config", {}).get("json_out") or None) if runs[(s, t)] else None
                    for s in SOURCES for t in (TIGHT_STEP, WIDE_STEP)},
           "present": {f"{s}@{t}": runs[(s, t)] is not None for s in SOURCES for t in (TIGHT_STEP, WIDE_STEP)},
           "arms": {f"{s}@{t}": arm_reading(runs[(s, t)], NAIVE) for s in SOURCES for t in (TIGHT_STEP, WIDE_STEP)},
           "facts": {f"{s}@{t}": _facts(runs[(s, t)]) if runs[(s, t)] else None
                     for s in SOURCES for t in (TIGHT_STEP, WIDE_STEP)},
           "cost": {TIGHT_STEP: _pair(runs[("cue", TIGHT_STEP)], runs[("action", TIGHT_STEP)]),
                    WIDE_STEP: _pair(runs[("cue", WIDE_STEP)], runs[("action", WIDE_STEP)])},
           "frozen": {f"{s}@{TIGHT_STEP}": curve_cells(curve).get((s, TIGHT_STEP)) for s in SOURCES},
           "chance": 1.0 / (int((runs[("cue", WIDE_STEP)].get("tasks") or [{}])[0].get("n_classes") or 4)
                            if runs[("cue", WIDE_STEP)] else 4),
           "steps": [WIDE_STEP, TIGHT_STEP], "replicates": REPLICATES}
    return out


def _facts_ok(a: dict | None, b: dict | None, shared_only: bool = False) -> dict:
    """The shared fields that differ between two runs, or all of them when `shared_only` is off."""
    if not a or not b:
        return {"missing": True}
    keys = SHARED if shared_only else SHARED + FOLLOWS_FROM_THE_SOURCE
    return {k: [a.get(k), b.get(k)] for k in keys if a.get(k) != b.get(k)}


def judge(r: dict) -> list[dict]:
    present, facts, arms = r.get("present") or {}, r.get("facts") or {}, r.get("arms") or {}
    #: an artifact on disk carries JSON's string keys where the in-memory reading carries the steps themselves,
    #: so both forms are normalized here rather than at every use
    cost = {int(k): v for k, v in (r.get("cost") or {}).items()}
    if not present.get(f"cue@{TIGHT_STEP}") or not present.get(f"action@{TIGHT_STEP}"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the tight-step pair is not on disk"}
                for c in CLAIMS]

    fc, fa = facts.get(f"cue@{TIGHT_STEP}"), facts.get(f"action@{TIGHT_STEP}")
    wc, wa = facts.get(f"cue@{WIDE_STEP}"), facts.get(f"action@{WIDE_STEP}")
    pair_diff = _facts_ok(fc, fa, shared_only=True)
    moved = [k for k in FOLLOWS_FROM_THE_SOURCE if fc.get(k) != fa.get(k)]
    step_cue = _facts_ok(fc, wc, shared_only=True)
    step_action = _facts_ok(fa, wa, shared_only=True)
    good = (not pair_diff and len(moved) == len(FOLLOWS_FROM_THE_SOURCE)
            and (wc is None or not step_cue) and (wa is None or not step_action)
            and fc.get("world_coupling_sha1") == CUE_COUPLING and fa.get("world_coupling_sha1") == ACTION_COUPLING
            and fc.get("loop_cue_at") == TIGHT_STEP and fa.get("loop_cue_at") == TIGHT_STEP
            and fc.get("repeats") == REPLICATES and fa.get("repeats") == REPLICATES
            and arms[f"cue@{TIGHT_STEP}"]["n"] == REPLICATES and arms[f"action@{TIGHT_STEP}"]["n"] == REPLICATES)
    j1 = {"id": "T1", "measured": f"the two cue@{TIGHT_STEP} runs differing {pair_diff}, the drive's source moving "
                                  f"{sorted(moved)}; against the cue@{WIDE_STEP} run {step_cue} and the "
                                  f"action@{WIDE_STEP} run {step_action}; couplings "
                                  f"{fc.get('world_coupling_sha1')} and {fa.get('world_coupling_sha1')}",
          "verdict": "MET -- one configuration at both steps" if good else
          f"FALSIFIER FIRED -- the pair differs {pair_diff}, the cue source's steps differ {step_cue}, the action "
          f"source's steps differ {step_action}"}

    fz = (r.get("frozen") or {})
    fzc, fza = fz.get(f"cue@{TIGHT_STEP}"), fz.get(f"action@{TIGHT_STEP}")
    chance = r.get("chance", 0.25)
    if not fzc or not fza:
        j2 = {"id": "T2", "measured": "the curve has no cell for this step",
              "verdict": "REFUSED -- the artifact this unit's licence comes from is absent"}
    else:
        above = {"cue": fzc["accuracy"] - chance, "action": fza["accuracy"] - chance}
        rest = [s for s in SOURCES if fz[f"{s}@{TIGHT_STEP}"]["world_sd"] <= 0.0]
        j2 = {"id": "T2", "measured": f"the frozen curve reads the cue source at {fzc['accuracy']:.4f} "
                                      f"({above['cue']:+.4f} over chance) with spread {fzc['world_sd']:.4f} and the "
                                      f"action source at {fza['accuracy']:.4f} ({above['action']:+.4f}) with spread "
                                      f"{fza['world_sd']:.4f}",
              "verdict": "MET -- both channels are live at this step" if min(above.values()) >= LEARNS and not rest
              else f"FALSIFIER FIRED -- {rest} is a world at rest at this step, so the price here would be a "
                   f"live-against-dead gap" if rest else
              f"FALSIFIER FIRED -- a cell within {LEARNS:.2f} of chance: {above}"}

    learn = {s: arms[f"{s}@{TIGHT_STEP}"]["mean_diagonal"] - chance for s in SOURCES}
    weak = [s for s in SOURCES if learn[s] < LEARNS]
    j3 = {"id": "T3", "measured": f"at cue@{TIGHT_STEP} the diagonals are "
                                  f"{ {s: round(arms[f'{s}@{TIGHT_STEP}']['mean_diagonal'], 4) for s in SOURCES} } "
                                  f"against a chance of {chance:.2f}, so "
                                  f"{ {s: round(v, 4) for s, v in learn.items()} } above it",
          "verdict": "MET -- both games are learnable at this step" if not weak else
          f"FALSIFIER FIRED -- {weak} within {LEARNS:.2f} of chance"}

    c8, c0 = cost.get(TIGHT_STEP), cost.get(WIDE_STEP)
    if not c8 or not c0:
        j4 = {"id": "T4", "measured": "one of the two costs is not computable",
              "verdict": "REFUSED -- the two costs this claim compares are not both available"}
    else:
        grow = c8["delta"] - c0["delta"]
        j4 = {"id": "T4", "measured": f"the cost is {c0['delta']:+.4f} at cue@{WIDE_STEP} and {c8['delta']:+.4f} "
                                      f"at cue@{TIGHT_STEP} on a sem of {c8['sem']:.4f}, so it grows by "
                                      f"{grow:+.4f} as the margin shrinks from {WIDE_STEP} to {TIGHT_STEP}",
              "verdict": f"MET -- the price is larger where the margin is tighter, by {grow:+.4f}" if grow >= GROWS
              else f"FALSIFIER FIRED -- the price does not depend on the margin inside the window: {grow:+.4f}" if
              grow < SAME else f"NULL -- {grow:+.4f}, between {SAME:.2f} and {GROWS:.2f}"}

    detail = "; ".join(f"`{s}@{TIGHT_STEP}` {arms[f'{s}@{TIGHT_STEP}']['paired']['delta']:+.4f} at "
                       f"{_sg(arms[f'{s}@{TIGHT_STEP}']['paired']['sigma'])} sigma" for s in SOURCES)
    unearned = [s for s in SOURCES if not (arms[f"{s}@{TIGHT_STEP}"]["paired"]["delta"] is not None
                                           and arms[f"{s}@{TIGHT_STEP}"]["paired"]["delta"] >= CARRIES
                                           and (arms[f"{s}@{TIGHT_STEP}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j5 = {"id": "T5", "measured": f"the paired channel readings at cue@{TIGHT_STEP}: {detail}",
          "verdict": "MET -- the answer is earned in both sources at this step" if not unearned else
          f"FALSIFIER FIRED -- the answer is not earned in {unearned}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not (r.get("present") or {}).get(f"cue@{TIGHT_STEP}") or not (r.get("present") or {}).get(f"action@{TIGHT_STEP}"):
        print("== the tightest step ==\n   REFUSED -- the tight-step pair is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the tightest step ==")
    print(f"   `e368`'s curve puts the action source's boundary between cue@{TIGHT_STEP} and cue@{TIGHT_STEP + 1} on "
          f"this draw, so cue@{TIGHT_STEP} is the last step where both channels are live")
    print(f"\n   {'cue at':>7} {'source':>7} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6} "
          f"{'frozen':>8} {'frozen sd':>10}")
    for step in (WIDE_STEP, TIGHT_STEP):
        for source in SOURCES:
            arm = r["arms"][f"{source}@{step}"]
            fz = (r.get("frozen") or {}).get(f"{source}@{step}") if step == TIGHT_STEP else None
            print(f"   {step:>7} {source:>7} {arm['mean_diagonal']:9.4f} {arm['mean_forgetting']:8.4f} "
                  f"{arm['paired']['delta']:+9.4f} {_sg(arm['paired']['sigma']):>6} "
                  f"{(fz['accuracy'] if fz else float('nan')):8.4f} {(fz['world_sd'] if fz else float('nan')):10.4f}")
    print(f"\n   {'cue at':>7} {'cost':>9} {'sem':>8} {'sigma':>7}")
    cost = {int(k): v for k, v in (r.get("cost") or {}).items()}
    for step in (WIDE_STEP, TIGHT_STEP):
        c = cost.get(step)
        if c:
            print(f"   {step:>7} {c['delta']:9.4f} {c['sem']:8.4f} {_sg(c['sigma']):>7}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e373` priced acting at the widest step and at the boundary and could not price it in between;")
    print("    this trains the last step where both channels are still alive, which is where the margin is thin)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--curve", type=Path, default=CURVE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(curve=args.curve)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
