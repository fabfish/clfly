"""E372 -- what acting costs: the same game at the same step, with the world listening to the cue instead.

`e371` trained the closed loop at the cue's first step -- the world's drive reading the agent's **own action
population** -- and found it learns to **0.7691**, above the frozen probe's **0.6602**, with `replay` cutting
forgetting by **0.2844** at **14.37 sigma**. It reported two numbers it could not claim: the trained body beats the
probe it was measured against by **+0.1089**, and it lands **0.0200** from the **other** drive source's frozen
ceiling of **0.7891** at the same step. That second number is a comparison across two artifacts and two drive
sources, and `e371` named what it would take to make it a measurement: *"the run that would pair them is a unit of
its own"*.

**This unit runs it.** One run at `e371`'s exact flags plus `--loop-drive-from-cue`, so the world's drive reads the
neurons the cue is written on and the agent has nothing to build; twenty replicates, the same two arms and the same
three tasks in sequence, compared against `e371`'s action-source run at the same step **paired over the twenty
seeds** and against `e363`'s frozen cells for both sources.

Five claims, registered before the new run's reading was opened.

- **R1 -- one configuration except where the world's drive is read.** The cue-source run agrees with `e371`'s
  action-source run on the circuit, the tasks and their widths, the basis, the read-out, the replicate count, the
  seed stream and the world's dimension, leak and nonlinearity, with the drive's source and the seven fields that
  follow from it -- the source itself, the **action population** it is read from and its width, and the drive map,
  the read map and the coupling matrix after it in the environment's own draw -- the only differences. That set is
  `e364`'s fired T1 and `e367`'s registered one, so it is registered here as expected rather than discovered.
  **Falsifier**: any field differing beyond those, or the two runs' coupling fingerprints not being
  `1b7d09f2b469` and `5326f4a0edb4` respectively.
- **R2 -- and the channel is live for the cue source here, as `e363` recorded.** That unit's frozen cell for the cue
  source at `cue@0` is at least **0.10** above chance. **Falsifier**: within **0.05** of chance, which would say the
  cue-source world is empty at the first step and the pairing has no upper end to compare with. **REFUSED** when
  that artifact is absent.
- **R3 -- and the game is learnable with the channel handed over too.** The cue-source `naive` diagonal is at least
  **0.10** above chance. **Falsifier**: within **0.05** of chance, which would say the easier of the two sources
  does not train. **Null**: between.
- **R4 -- and the answer is earned there.** Both arms' paired channel readings are at least **0.10** and positive at
  **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved. This is what makes the two
  sources comparable quantities rather than two numbers.
- **R5 -- and at this step acting costs nothing measurable.** The cue-source `naive` diagonal exceeds the
  action-source one by **less than 0.05**, paired over the twenty replicates -- the world listening to the agent's
  own action is the same task as the world listening to the cue, at the step where the trial has the room for both.
  **Falsifier**: **0.10** or more apart, which would say building the channel is a real cost and `e371`'s 0.0200 was
  the artifact of comparing two files rather than a measurement. **Null**: between 0.05 and 0.10. *This is the claim
  the unit exists for.*

**What it can do beyond that.** `e371`'s reported +0.1089, the trained body against the probe **for its own source**,
is recomputed here for both sources on the same twenty seeds, so the two gaps sit in one table instead of one in a
finding and one in a row.

**What it cannot do.** *One step*: this is `cue@0`, where `e369`'s window is widest for both sources; at the late
steps the two sources are not the same task at all, because the action source's world is at rest and the cue
source's is not, so nothing here says what acting costs where the window is narrow. *One world and one coupling*:
eight dimensions at `leak = 0.35`, and the two runs carry different coupling matrices because the drive map's width
follows the population it reads, which is the difference R1 registers. *And "costs nothing" is about a diagonal
above chance*: both arms train on three tasks in sequence, so a resolved R5 says the two sources reach the same
level, not that they get there the same way -- the forgetting, the retention matrices and the channel readings are
reported beside it for that reason.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e371_the_game_the_agent_can_play import _sg, arm_reading, paired

#: the run this unit made: the same game at the same step with the world listening to the cue population
OVERHAND = Path("runs/e372_earned_label_cue0_cuesource_20reps.json")
#: `e371`'s run at the same step with the world listening to the agent's own action population
PLAYED = Path("runs/e371_earned_label_cue0_actionsource_20reps.json")
FROZEN = Path("runs/e363_where_the_cue_can_reach_the_world.json")
FROZEN_SOURCE, FROZEN_STEP = "cue", 0
PLAYED_SOURCE = "action"
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
CUE_COUPLING = "1b7d09f2b469"
ACTION_COUPLING = "5326f4a0edb4"
REPLICATES = 20
CUE_STEP = 0
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
SAME = 0.05
FIRES = 0.10
CLAIMS = (
    ("R1", "one configuration except where the world's drive is read",
     "The two runs agree on the circuit, the tasks and their widths, the basis, the read-out, the replicate count, "
     "the seed stream and the world's dimension, leak and nonlinearity, with the drive's source and the seven "
     "fields that follow from it the only differences",
     "falsifier: any field differing beyond those, or the couplings not being 1b7d09f2b469 and 5326f4a0edb4"),
    ("R2", f"and the channel is live for the cue source here, {LEARNS:.2f} over chance",
     f"`e363`'s frozen cell for `{FROZEN_SOURCE}@{FROZEN_STEP}` is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance; refused when that artifact is absent"),
    ("R3", f"and the game is learnable with the channel handed over too, {LEARNS:.2f} over chance",
     "The cue-source `naive` diagonal is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance; null: between {FLAT:.2f} and {LEARNS:.2f}"),
    ("R4", f"and the answer is earned there, {CARRIES:.2f} at {SIGMA:.0f} sigma",
     "Both arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
    ("R5", f"and at this step acting costs nothing measurable, within {SAME:.2f}",
     "The cue-source `naive` diagonal exceeds the action-source one by less than 0.05, paired over the replicates",
     f"falsifier: {FIRES:.2f} or more apart; null: between {SAME:.2f} and {FIRES:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def frozen_cell(path: Path = FROZEN, source: str = FROZEN_SOURCE, step: int = FROZEN_STEP):
    doc = load(path)
    if not doc:
        return None
    for c in doc.get("cells") or []:
        if c.get("source") == source and c.get("cue_at") == step:
            return {"accuracy": float(c["accuracy"]), "chance": float(c["chance"]), "world_sd": float(c["world_sd"]),
                    "artifact": Path(path).name}
    return None


def reading(overhand_path: Path = OVERHAND, played_path: Path = PLAYED, frozen_path: Path = FROZEN) -> dict:
    over, played = load(overhand_path), load(played_path)
    out = {"rows": {**{f"over_{a}": arm_reading(over, a) for a in ARMS},
                    **{f"played_{a}": arm_reading(played, a) for a in ARMS}},
           "facts": {"over": _facts(over), "played": _facts(played)},
           "runs": {"over": Path(overhand_path).name, "played": Path(played_path).name},
           "present": {"over": over is not None, "played": played is not None},
           "frozen": frozen_cell(frozen_path), "frozen_action": frozen_cell(frozen_path, PLAYED_SOURCE, FROZEN_STEP),
           "expected_couplings": [CUE_COUPLING, ACTION_COUPLING], "expected_replicates": REPLICATES,
           "expected_cue_step": CUE_STEP, "cost": None, "probe_gaps": None}
    out["ok"] = {"over": over is not None and all(out["rows"][f"over_{a}"].get("ok") for a in ARMS),
                 "played": played is not None and all(out["rows"][f"played_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["over"] and out["ok"]["played"]:
        out["cost"] = paired(out["rows"][f"over_{NAIVE}"]["diagonal"], out["rows"][f"played_{NAIVE}"]["diagonal"])
        out["probe_gaps"] = {"cue": (out["rows"][f"over_{NAIVE}"]["mean_diagonal"] - out["frozen"]["accuracy"])
                             if out["frozen"] else None,
                             "action": (out["rows"][f"played_{NAIVE}"]["mean_diagonal"]
                                        - out["frozen_action"]["accuracy"]) if out["frozen_action"] else None}
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("over"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the cue-source run is not on disk"} for c in CLAIMS]

    fo, fp = r["facts"]["over"], r["facts"]["played"]
    if not (r.get("present") or {}).get("played"):
        j1 = {"id": "R1", "measured": f"the action-source run is absent, so `{r['runs']['played']}` is not there to "
                                      f"pair against",
              "verdict": "REFUSED -- the run this unit pairs against is absent"}
    else:
        sh = {k: [fo.get(k), fp.get(k)] for k in SHARED if fo.get(k) != fp.get(k)}
        moved = {k: [fo.get(k), fp.get(k)] for k in FOLLOWS_FROM_THE_SOURCE if fo.get(k) != fp.get(k)}
        good = (not sh and len(moved) == len(FOLLOWS_FROM_THE_SOURCE)
                and fo.get("world_coupling_sha1") == CUE_COUPLING and fp.get("world_coupling_sha1") == ACTION_COUPLING
                and fo.get("loop_cue_at") == CUE_STEP and fp.get("loop_cue_at") == CUE_STEP
                and fo.get("repeats") == REPLICATES
                and rows[f"over_{NAIVE}"]["n"] == REPLICATES and rows[f"over_{REPLAY}"]["n"] == REPLICATES)
        j1 = {"id": "R1", "measured": f"`{r['runs']['over']}` against `{r['runs']['played']}`: cue steps "
                                      f"{[fp.get('loop_cue_at'), fo.get('loop_cue_at')]}, shared fields differing "
                                      f"{sh}, the drive's source moving {sorted(moved)}, couplings "
                                      f"{fo.get('world_coupling_sha1')} and {fp.get('world_coupling_sha1')}, "
                                      f"circuit {fo['circuit_size']}, tasks {fo['task_names']} at widths "
                                      f"{fo['task_readout_widths']}, {fo['repeats']} replicates at seed0 "
                                      f"{fo['seed0']}",
              "verdict": "MET -- one configuration, the drive's source the only difference this unit did not "
                         "register as following from it" if good else
              f"FALSIFIER FIRED -- shared fields differ {sh} or the source's own fields did not move: {sorted(moved)}"}

    fz = r.get("frozen")
    if not fz:
        j2 = {"id": "R2", "measured": "the frozen cell is not on disk",
              "verdict": "REFUSED -- the licence this unit rests on is absent"}
    else:
        above = fz["accuracy"] - fz["chance"]
        j2 = {"id": "R2", "measured": f"`{fz['artifact']}` records `{FROZEN_SOURCE}@{FROZEN_STEP}` at "
                                      f"{fz['accuracy']:.4f} against a chance of {fz['chance']:.2f}, {above:+.4f} "
                                      f"above it, on a world with spread {fz['world_sd']:.4f}",
              "verdict": f"MET -- the channel is live for the cue source too, {above:+.4f} over chance" if
              above >= LEARNS else
              f"FALSIFIER FIRED -- only {above:+.4f} over chance: the pairing has no upper end" if above < FLAT else
              f"NULL -- {above:+.4f}, between {FLAT:.2f} and {LEARNS:.2f}"}

    naive = rows[f"over_{NAIVE}"]
    learned = naive["mean_diagonal"] - naive["chance"]
    j3 = {"id": "R3", "measured": f"the cue-source `{NAIVE}` diagonal is {naive['mean_diagonal']:.4f} against a "
                                  f"chance of {naive['chance']:.2f}, {learned:+.4f} above it, over {naive['n']} "
                                  f"replicates",
          "verdict": f"MET -- the handed-over game is learnable too, {learned:+.4f} over chance" if learned >= LEARNS
          else f"FALSIFIER FIRED -- only {learned:+.4f} above chance: the easier source does not train" if
          learned < FLAT else f"NULL -- {learned:+.4f}, between {FLAT:.2f} and {LEARNS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'over_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'over_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"over_{a}"]["paired"]["delta"] is not None
                                    and rows[f"over_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"over_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j4 = {"id": "R4", "measured": f"the cue-source game's paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- the answer is earned in both arms" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}

    cost = r.get("cost") or {"delta": None}
    if cost.get("delta") is None:
        j5 = {"id": "R5", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the two runs do not pair"}
    else:
        j5 = {"id": "R5", "measured": f"the cue source reads {rows[f'over_{NAIVE}']['mean_diagonal']:.4f} and the "
                                      f"action source {rows[f'played_{NAIVE}']['mean_diagonal']:.4f}, so being "
                                      f"handed the channel is worth {cost['delta']:+.4f} on a sem of "
                                      f"{cost['sem']:.4f} ({_sg(cost['sigma'])} sigma) over {cost['n']} paired "
                                      f"replicates",
              "verdict": f"MET -- acting costs nothing measurable at this step, {cost['delta']:+.4f}" if
              abs(cost["delta"]) < SAME else
              f"FALSIFIER FIRED -- {cost['delta']:+.4f} apart: building the channel is a real cost" if
              abs(cost["delta"]) >= FIRES else
              f"NULL -- {cost['delta']:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not (r.get("ok") or {}).get("over"):
        print("== what acting costs ==\n   REFUSED -- the cue-source run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== what acting costs ==")
    print(f"   `{r['runs']['over']}` against `{r['runs']['played']}`, the same game at cue step "
          f"{CUE_STEP} with the world listening to the cue and to the agent's own action")
    print(f"\n   {'source':>7} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        print(f"   {key.split('_', 1)[0]:>7} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")
    for name, cell in (("cue", r.get("frozen")), ("action", r.get("frozen_action"))):
        if cell:
            print(f"   the frozen {name} cell at step {FROZEN_STEP} in `{cell['artifact']}` reads "
                  f"{cell['accuracy']:.4f} on a world with spread {cell['world_sd']:.4f}")
    if r.get("probe_gaps"):
        print(f"   the trained body against its own source's probe: cue "
              f"{r['probe_gaps']['cue']:+.4f}, action {r['probe_gaps']['action']:+.4f} (both reported)")

    print("\n== the registered claims, R1-R5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e371` trained the world that listens to the agent and beat its probe; this trains the same game")
    print("    with the channel handed over, so the difference between them is a measurement and not two files)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--over", type=Path, default=OVERHAND)
    ap.add_argument("--played", type=Path, default=PLAYED)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(overhand_path=args.over, played_path=args.played, frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
