"""E371 -- the game the agent can play: the closed loop trained at the first step, where the channel is live.

The line has spent five units on a cell that turns out to be **empty**: the world whose drive reads the agent's own
action population, with the cue one step from the read-out, is at rest (`e367`, `e368`), because two steps of the
trial are not enough for the cue to reach that population (`e369`) and because that is what the wiring says
(`e370`). `e363`'s frozen grid also holds the other end of the same row: with the cue at the **first** step the same
world reads **0.6602**, above chance by **0.4102** on a state with spread **0.2029**, so the agent's own action does
carry the cue to the world once the trial has the room for it. **That cell has never been trained.**

**This unit trains it.** It is the first closed loop in this repository where the thing the agent must solve is
carried by the agent's own action and the world has the time to receive it: the cue arrives at step 0, the world's
drive reads the action population, the world's final state is the read-out, and the suite is the runner's own three
tasks trained in sequence. One run at `e367`'s flags with the cue at the first step, `--methods naive,replay`,
`--repeats 20`, paired against that unit's run at step 10 -- the empty cell -- and against `e363`'s frozen cell for
this configuration.

Five claims, registered before the new run's reading was opened.

- **G1 -- one configuration except the cue's step.** The two action-source runs agree on the circuit, the
  populations, the world, the coupling fingerprint, the drive map, the basis, the tasks and their widths, the
  read-out, the replicate count, the seed stream and every other recorded field, differing in the cue's step.
  **Falsifier**: any other field differing.
- **G2 -- and the channel is live here, as `e363` recorded.** That unit's frozen cell for the action source at
  `cue@0` is at least **0.10** above chance. **Falsifier**: within **0.05** of chance, which would say the world is
  at rest at the first step too and this cell is empty as well. **REFUSED** when that artifact is absent. *This is
  the licence the unit rests on.*
- **G3 -- and the game is learnable.** The trained `naive` diagonal is at least **0.10** above chance.
  **Falsifier**: within **0.05** of chance, which would say a body free to shape its own action population cannot
  route a cue it is given eleven steps of room to route. **Null**: between. *This is the claim the unit exists for.*
- **G4 -- and the answer is earned through the agent's own action.** Both arms' paired channel readings are at least
  **0.10** and positive at **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved. Without
  this the run could be reading the cue's own echo through the network rather than anything the loop built.
- **G5 -- and the buffer helps in this substrate.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least
  **0.05**, paired over the twenty replicates. **Falsifier**: `replay` forgetting more by **0.05** or more.
  **Null**: between. This is `e276`'s question asked on a substrate that did not exist when it was asked.

**What it can do beyond that.** The empty cell's trained number, `e367`'s **0.2361**, is reported beside this one
and not claimed against it, because the two runs are at different steps by construction and the difference between
them is the thing `e369` and `e370` already explain from the wiring. What is new here is that the same instrument,
the same suite and the same twenty seeds now have a cell where the loop carries the answer.

**What it cannot do.** *One cell at one drive source*: the cue-source game at the same step is `e363`'s frozen
**0.7891** and has no trained run, so this unit does not price what it costs the agent to act rather than to be
listened to; that is a second run and a unit of its own. *One world and one coupling*: eight dimensions at
`leak = 0.35` with `e359`'s matrix, and the action source's own draw, which `e370` says is a **one-hop** draw only
by luck -- at `seed0 = 0` the distance is **2** and the window is one step shorter, which this cell sits inside
either way and a cell one step later would not. *And "learnable" is a diagonal above chance*: the corpus's
significance convention is a paired channel at 2 sigma and its floor is the test set's own noise, so a resolved G3
is a statement that the suite trains, not that it trains well.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import (
    FOLLOWS_FROM_THE_SOURCE,
    SHARED,
    _facts,
)

#: the run this unit made: the closed loop, the world's drive on the action population, the cue at the first step
PLAYED = Path("runs/e371_earned_label_cue0_actionsource_20reps.json")
#: `e367`'s run at the step the world cannot see, and `e363`'s frozen grid
EMPTY = Path("runs/e367_earned_label_cue10_actionsource_20reps.json")
FROZEN = Path("runs/e363_where_the_cue_can_reach_the_world.json")
FROZEN_SOURCE, FROZEN_STEP = "action", 0
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COUPLING_SHA1 = "5326f4a0edb4"
REPLICATES = 20
CUE_STEP = 0
EMPTY_STEP = 10
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
CARRIES = 0.10
FORGETS = 0.05
CLAIMS = (
    ("G1", "one configuration except the cue's step",
     "The two action-source runs agree on the populations, the world, the coupling fingerprint, the drive map, the "
     "basis, the tasks, the sizes, the replicate count, the seed stream and the cue's step alone differing",
     "falsifier: any other field differing"),
    ("G2", f"and the channel is live here, {LEARNS:.2f} over chance",
     f"`e363`'s frozen cell for `{FROZEN_SOURCE}@{FROZEN_STEP}` is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance; refused when that artifact is absent"),
    ("G3", f"and the game is learnable, {LEARNS:.2f} over chance",
     "The trained `naive` diagonal is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance; null: between {FLAT:.2f} and {LEARNS:.2f}"),
    ("G4", f"and the answer is earned through the agent's own action, {CARRIES:.2f} at {SIGMA:.0f} sigma",
     "Both arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
    ("G5", f"and the buffer helps in this substrate, by {FORGETS:.2f}",
     "`replay`'s `mean_forgetting` is lower than `naive`'s by at least 0.05, paired over the replicates",
     f"falsifier: `replay` forgets more by {FORGETS:.2f} or more"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None, "vals": diffs}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf"),
            "vals": diffs}


def _sg(sigma) -> str:
    return "inf" if sigma is None else f"{sigma:.2f}"


def arm_reading(run: dict | None, arm: str) -> dict:
    if not run:
        return {"arm": arm, "ok": False}
    method = (run.get("methods") or {}).get(arm)
    if not isinstance(method, dict) or not method.get("replicates"):
        return {"arm": arm, "ok": False, "why": "no replicates"}
    reps = method["replicates"]
    channel, forgetting, diagonal, final = [], [], [], []
    for r in reps:
        entries = r.get("paired_channel")
        if not isinstance(entries, list) or not entries:
            return {"arm": arm, "ok": False, "why": "no paired record"}
        channel.append(statistics.fmean([e["with_loop"] - e["without_loop"] for e in entries]))
        forgetting.append(float(r["mean_forgetting"]))
        diagonal.append(float(statistics.fmean(r["learned"])))
        final.append(float(r["final_accuracy"]))
    n_classes = int((run.get("tasks") or [{}])[0].get("n_classes") or 2)
    return {"arm": arm, "ok": True, "n": len(reps), "chance": 1.0 / n_classes, "forgetting": forgetting,
            "diagonal": diagonal, "final": final, "mean_forgetting": statistics.fmean(forgetting),
            "mean_diagonal": statistics.fmean(diagonal), "mean_final": statistics.fmean(final),
            "paired": paired(channel, [0.0] * len(channel)),
            "retention": [[None if x is None else float(x) for x in row] for row in (reps[0].get("retention") or [])]}


def frozen_cell(path: Path = FROZEN, source: str = FROZEN_SOURCE, step: int = FROZEN_STEP):
    doc = load(path)
    if not doc:
        return None
    for c in doc.get("cells") or []:
        if c.get("source") == source and c.get("cue_at") == step:
            return {"accuracy": float(c["accuracy"]), "chance": float(c["chance"]), "world_sd": float(c["world_sd"]),
                    "artifact": Path(path).name}
    return None


def reading(played_path: Path = PLAYED, empty_path: Path = EMPTY, frozen_path: Path = FROZEN) -> dict:
    played, empty = load(played_path), load(empty_path)
    out = {"rows": {**{f"played_{a}": arm_reading(played, a) for a in ARMS},
                    **{f"empty_{a}": arm_reading(empty, a) for a in ARMS}},
           "facts": {"played": _facts(played), "empty": _facts(empty)},
           "runs": {"played": Path(played_path).name, "empty": Path(empty_path).name},
           "present": {"played": played is not None, "empty": empty is not None},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES, "expected_cue_step": CUE_STEP,
           "frozen": frozen_cell(frozen_path), "empty_gap": None, "buffer": None}
    out["ok"] = {"played": played is not None and all(out["rows"][f"played_{a}"].get("ok") for a in ARMS),
                 "empty": empty is not None and all(out["rows"][f"empty_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["played"]:
        out["buffer"] = paired(out["rows"][f"played_{REPLAY}"]["forgetting"],
                               out["rows"][f"played_{NAIVE}"]["forgetting"])
        if out["ok"]["empty"]:
            out["empty_gap"] = (out["rows"][f"played_{NAIVE}"]["mean_diagonal"]
                                - out["rows"][f"empty_{NAIVE}"]["mean_diagonal"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("played"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the first-step run is not on disk"}
                for c in CLAIMS]

    fa, fe = r["facts"]["played"], r["facts"]["empty"]
    if not (r.get("present") or {}).get("empty"):
        j1 = {"id": "G1", "measured": f"the read-step run is absent, so the pair {r['runs']['empty']} is not there "
                                      f"to compare against",
              "verdict": "REFUSED -- the run this unit pairs against is absent"}
    else:
        differ = {k: [fa.get(k), fe.get(k)] for k in SHARED + FOLLOWS_FROM_THE_SOURCE if fa.get(k) != fe.get(k)}
        good = (not differ and fa.get("loop_cue_at") == CUE_STEP and fe.get("loop_cue_at") == EMPTY_STEP
                and fa.get("world_coupling_sha1") == COUPLING_SHA1 and fa.get("repeats") == REPLICATES
                and rows[f"played_{NAIVE}"]["n"] == REPLICATES and rows[f"played_{REPLAY}"]["n"] == REPLICATES)
        j1 = {"id": "G1", "measured": f"`{r['runs']['played']}` against `{r['runs']['empty']}`: cue steps "
                                      f"{[fe.get('loop_cue_at'), fa.get('loop_cue_at')]}, differing {differ}, "
                                      f"circuit {fa['circuit_size']}, tasks {fa['task_names']} at read-out widths "
                                      f"{fa['task_readout_widths']}, {fa['repeats']} replicates at seed0 "
                                      f"{fa['seed0']}, basis {fa['basis']}, coupling {fa['world_coupling_sha1']}",
              "verdict": "MET -- one configuration except the cue's step" if good else
              f"FALSIFIER FIRED -- fields differ beyond the cue's step: {differ}"}

    fz = r.get("frozen")
    if not fz:
        j2 = {"id": "G2", "measured": "the frozen cell is not on disk",
              "verdict": "REFUSED -- the licence this unit rests on is absent"}
    else:
        above = fz["accuracy"] - fz["chance"]
        j2 = {"id": "G2", "measured": f"`{fz['artifact']}` records `{FROZEN_SOURCE}@{FROZEN_STEP}` at "
                                      f"{fz['accuracy']:.4f} against a chance of {fz['chance']:.2f}, {above:+.4f} "
                                      f"above it, on a world with spread {fz['world_sd']:.4f}",
              "verdict": f"MET -- the channel is live at the first step, {above:+.4f} over chance" if above >= LEARNS
              else f"FALSIFIER FIRED -- only {above:+.4f} over chance: this cell is at rest too" if above < FLAT else
              f"NULL -- {above:+.4f}, between {FLAT:.2f} and {LEARNS:.2f}"}

    naive = rows[f"played_{NAIVE}"]
    learned = naive["mean_diagonal"] - naive["chance"]
    j3 = {"id": "G3", "measured": f"the game cell's `{NAIVE}` diagonal is {naive['mean_diagonal']:.4f} against a "
                                  f"chance of {naive['chance']:.2f}, {learned:+.4f} above it, over {naive['n']} "
                                  f"replicates"
                                  + (f", against the empty cell's {rows[f'empty_{NAIVE}']['mean_diagonal']:.4f} "
                                     f"(reported, not claimed)" if ok.get("empty") else ""),
          "verdict": f"MET -- the game is learnable, {learned:+.4f} above chance" if learned >= LEARNS else
          f"FALSIFIER FIRED -- only {learned:+.4f} above chance: the agent cannot route a cue it has eleven steps "
          f"to route" if learned < FLAT else
          f"NULL -- {learned:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'played_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'played_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"played_{a}"]["paired"]["delta"] is not None
                                    and rows[f"played_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"played_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j4 = {"id": "G4", "measured": f"the game cell's paired channel readings over {naive['n']} replicates: {detail}",
          "verdict": "MET -- the answer is earned through the agent's own action, in both arms" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}

    buf = r.get("buffer") or {"delta": None}
    if buf.get("delta") is None:
        j5 = {"id": "G5", "measured": "the buffer value was not computable",
              "verdict": "REFUSED -- the buffer value was not computable"}
    else:
        j5 = {"id": "G5", "measured": f"`{REPLAY}` forgets {rows[f'played_{REPLAY}']['mean_forgetting']:.4f} "
                                      f"against `{NAIVE}`'s {naive['mean_forgetting']:.4f}, so the buffer changes "
                                      f"it by {buf['delta']:+.4f} on a sem of {buf['sem']:.4f} "
                                      f"({_sg(buf['sigma'])} sigma) over {buf['n']} paired replicates",
              "verdict": f"MET -- the buffer helps here by {abs(buf['delta']):.4f}" if buf["delta"] <= -FORGETS else
              f"FALSIFIER FIRED -- it makes forgetting worse by {buf['delta']:.4f}" if buf["delta"] >= FORGETS else
              f"NULL -- {buf['delta']:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not (r.get("ok") or {}).get("played"):
        print("== the game the agent can play ==\n   REFUSED -- the first-step run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the game the agent can play ==")
    print(f"   `{r['runs']['played']}` at the cue's first step against `{r['runs']['empty']}` at the step the")
    print("   world cannot see; the world's drive reads the agent's own action population in both")
    print(f"\n   {'cell':>7} {'cue at':>7} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} "
          f"{'sigma':>6}")
    for key, row in r["rows"].items():
        cell = key.split("_", 1)[0]
        when = (r["facts"]["played"] if cell == "played" else r["facts"]["empty"]).get("loop_cue_at")
        print(f"   {cell:>7} {str(when):>7} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")
    if r.get("frozen"):
        print(f"   the frozen cell for this configuration in `{r['frozen']['artifact']}` reads "
              f"{r['frozen']['accuracy']:.4f} on a world with spread {r['frozen']['world_sd']:.4f}")
    if r.get("empty_gap") is not None:
        print(f"   the game cell reads {r['empty_gap']:+.4f} against the empty cell's trained diagonal "
              f"(reported, not claimed)")

    print("\n== the registered claims, G1-G5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e367` trained the cell the wiring leaves at rest and read 0.2361; `e370` says the distance from")
    print("    the cue to the population the world reads is what sets that boundary, and this trains the cell on")
    print("    the other side of it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--played", type=Path, default=PLAYED)
    ap.add_argument("--empty", type=Path, default=EMPTY)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(played_path=args.played, empty_path=args.empty, frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
