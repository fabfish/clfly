"""E500 -- the pass plays for the payout: the paid, label-first episodic pass with the map trained by the world's currency.

`e498` made the environment's target follow **the cue the label names**, so the runner stopped refusing
`--loop-label-first` with `--loop-reward` and the episodic pass could be **paid** -- and its own *cannot do* says the
payout is a **meter** there: the paid episodic pass was run without `--loop-earn`, so nothing had measured whether an
agent can **play for** the world's payout inside an episode. `e488` gave the loop's map an optimizer of its own and
ascended the world's payout into it, and that was at **one trial per pass**.

**This unit plays for it.** One run: `e498`'s own paid command with **`--loop-policy --loop-earn`** added -- one
world, one pass, one read, one label-first placement and one payout, with the map the agent acts through taken out of
the body's optimizer and trained by ascent on the world's payout -- read against `e498`'s paid meter run and against
`e488`'s own earn run, which is where **the map's distance from the identity** was first measured.

Two flags and not one: `--loop-earn` needs `--loop-policy` for the map and `--loop-reward` for the payout, and a
third is what this unit adds to `e498`'s own roll -- so the pair is the whole question. The runner's checks are
built inside its own `main` and cannot be called without training, so its **refusal messages** are read from the
source: none of them may name the ascent beside the episode or the placement.

Three claims, registered before the new run's reading was opened.

- **QA1 -- and the pair runs and is two flags apart.** Against `e498`'s paid meter run every recorded `config` field
  agrees except `loop_policy`, `loop_earn`, the output path and the saved weights; every field of the environment's
  draw agrees, with none added and none missing; each run carries **twenty** replicates; and none of the runner's own
  refusal messages names the ascent beside the episode or the placement. **Falsifier**: any other config field
  differing, a draw field differing, a replicate count other than twenty, or the runner refusing the pair.
- **QA2 -- and the payout reaches the map.** On the new run the map's distance from the identity is **above zero on
  every replicate of every arm**, read beside `e488`'s own earn run; and on **each of the three arms** the reward's
  diagonal is **above** the meter run's, paired over the twenty replicate seeds, at **two** sigma. **Falsifier**: a
  replicate whose map distance is zero or negative, or a reward contrast that does not resolve or is negative. *It
  can fire: `e498`'s own currency inside the pass is **flat** -- **+0.0104**, **-0.0123** and **+0.0547** at
  **+0.27**, **-0.31** and **+1.78** sigma against the diagonal's last row -- so whether a map paid inside the pass
  moves the level at all is this claim, and a map that moves while the payout does not is the outcome `e498`'s own
  meter cannot see.*
- **QA3 -- and the pass is still learned while the map is trained by the payout.** On **at least two of the three
  arms** the new run's accuracy diagonal is at least **0.10** above the four-class chance of **0.25** and not more
  than **0.10** below the meter run's on that arm. **Falsifier**: fewer than two arms over the bar, or an arm more
  than **0.10** under the meter run's. *It can fire: `e488` found the paid map's accuracy **below** the task-loss
  map's on every arm, by **0.0285** to **0.0410**, so a paid map inside the episode can cost the pass as well.*

**What it can do beyond that.** It closes the hole `e498`'s own *cannot do* left open: the episodic pass was **paid**
and the map that drives the world was not **paid for**, and the line `e483`..`e499` built one flag at a time -- the
payout, the episode, the label first and the map the payout can train -- now has all of them on in one run. Read with
`e488` it is the other trial length of the same question: there the map was paid at one trial per pass, here inside a
two-trial episode whose target follows the label.

**What it cannot do.** *One episode length and one placement*: two trials of six steps with the label first, the
three- and four-trial passes and the interior placements not in it. *And one map and one payout*: a linear map over
one population, covered by no penalty, and the environment's own target rule with the payout a linear read of the
cue. *And the payout is read on the map and not on the action*: what is ascended is the world's own currency, scored
against the target the cue sets, so a reward on the action or sparse in time is a different unit. *And one world, one
budget and one seed stream*: the card's own setting, so what a second world or a second learning rate does with the
earning is not in the unit.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e488_the_reward_trains_the_agent as e488
from experiments import e489_the_benchmark_has_an_episode as e489
from experiments import e495_the_label_first as e495
from experiments.e172_parser_registry import parser_flags

#: the new run, the paid meter run it is read against, and `e488`'s own earn run -- the map instrument's reference
NEW = Path("runs/e500_earned_label_episode2_labelfirst_reward_earn_20reps.json")
METER = Path("runs/e498_earned_label_episode2_labelfirst_reward_20reps.json")
EARN = e488.PAID
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
#: the two fields the pair moves, and the run's own bookkeeping
MOVED = ("loop_policy", "loop_earn")
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = e495.EPISODE
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
#: the bar an arm's accuracy has to clear over chance, and how far under the meter run's it may sit
BAR = 0.10
TOL = 0.10
ARMS_NEEDED = 2
PLACES = 4
CLAIMS = (
    ("QA1", "and the pair runs and is two flags apart",
     "Against e498's paid meter run every recorded config field agrees except loop_policy, loop_earn, the output path "
     "and the saved weights; every field of the environment's draw agrees, with none added and none missing; each run "
     "carries twenty replicates; and none of the runner's own refusal messages names the ascent beside the episode or "
     "the placement",
     "falsifier: any other config field differing, a draw field differing, a replicate count other than twenty, or "
     "the runner refusing the pair"),
    ("QA2", f"and the payout reaches the map, at {SIGMA:.0f} sigma on every arm",
     "On the new run the map's distance from the identity is above zero on every replicate of every arm, read beside "
     "e488's own earn run, and on each of the three arms the reward's diagonal is above the meter run's, paired over "
     "the twenty replicate seeds, at two sigma",
     "falsifier: a replicate whose map distance is zero or negative, or a reward contrast that does not resolve or is "
     "negative"),
    ("QA3", f"and the pass is still learned while the map is trained by the payout, on {ARMS_NEEDED} arms",
     "On at least two of the three arms the new run's accuracy diagonal is at least 0.10 above the four-class chance "
     "of 0.25 and not more than 0.10 below the meter run's on that arm",
     "falsifier: fewer than two arms over the bar, or an arm more than 0.10 under the meter run's"),
)


def _defaults() -> dict:
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return old is None and key in DEFAULTS and new == DEFAULTS[key]


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def refusals(runner: Path = RUNNER) -> dict | None:
    """The runner's own refusals, read from its source: is the pair refused the way a flag pair can be?

    The checks are built inside the runner's `main`, so calling them would train a model; what is read instead is
    every `raise SystemExit` in the file and the message it carries. A message that names the ascent
    (`--loop-earn`, `--loop-policy`) beside the episode (`--loop-episode`) or the placement (`--loop-label-first`)
    is a refusal of the pair, and `e498` removed exactly one such refusal from this line.
    """
    p = Path(runner)
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None
    messages = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Raise) or node.exc is None:
            continue
        call = node.exc
        if not (isinstance(call, ast.Call) and getattr(call.func, "id", None) == "SystemExit"):
            continue
        parts = []
        for arg in call.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                parts.append(arg.value)
            elif isinstance(arg, ast.JoinedStr):
                parts.append("".join(v.value for v in arg.values
                                     if isinstance(v, ast.Constant) and isinstance(v.value, str)))
        messages.append("".join(parts))
    ascent = [m for m in messages if "loop-earn" in m or "loop-policy" in m]
    pair = [m for m in ascent if "loop-episode" in m or "loop-label-first" in m]
    return {"messages": len(messages), "naming_the_ascent": ascent, "naming_the_pair": pair,
            "pair_refused": bool(pair)}


def _roll(path: Path) -> dict | None:
    """One run's per-arm reading: both currencies' diagonals and last rows, the map's movement, config and draw."""
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        entry = {"replicates": len(reps),
                 "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                 "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps],
                 "policy_move": [None if r.get("policy_move") is None else float(r["policy_move"]) for r in reps]}
        rw = [r.get("reward_retention") for r in reps]
        #: a run without the payout records the field with a matrix of `None`s, so the cell's presence is not the
        #: payout's: what is checked is the matrix's own corner
        if any(x is None or x[0][0] is None for x in rw):
            entry["reward_diagonal"] = None
            entry["reward_last"] = None
        else:
            entry["reward_diagonal"] = [statistics.fmean([x[k][k] for k in range(3)]) for x in rw]
            entry["reward_last"] = [statistics.fmean([x[2][j] for j in range(3)]) for x in rw]
        got[arm] = entry
    return {"artifact": path.name, "arms": got, "config": doc.get("config") or {},
            "env_draw": doc.get("env_draw") or {}}


def _against(mine: dict, theirs: dict) -> dict:
    """One run's config and draw against another's, the inert rule applied to the config."""
    cfg, other_cfg = mine["config"], theirs["config"]
    same, inert, differ = {}, {}, {}
    for k in sorted(set(cfg) | set(other_cfg)):
        old, new = other_cfg.get(k), cfg.get(k)
        if old == new:
            same[k] = new
        elif _inert(k, old, new):
            inert[k] = [old, new]
        else:
            differ[k] = [old, new]
    agree = {k: theirs["env_draw"].get(k) == mine["env_draw"].get(k) for k in theirs["env_draw"]}
    return {"same": len(same), "inert": sorted(inert), "differ": differ,
            "moved": {k: cfg.get(k) for k in MOVED},
            "draw": {"agree": agree, "differ": sorted(k for k, ok in agree.items() if not ok),
                     "added": sorted(set(mine["env_draw"]) - set(theirs["env_draw"])),
                     "missing": sorted(set(theirs["env_draw"]) - set(mine["env_draw"]))}}


def _map(roll: dict | None) -> dict | None:
    """The map's distance from the identity, per arm, or `None` where the run records no movement."""
    if roll is None:
        return None
    out = {}
    for arm in ARMS:
        moves = roll["arms"][arm]["policy_move"]
        if not moves or any(m is None for m in moves):
            return None
        out[arm] = {"replicates": len(moves), "above_zero": sum(1 for m in moves if m > 0.0),
                    "smallest": min(moves), "mean": statistics.fmean(moves)}
    return out


def _reward_missing(roll: dict) -> bool:
    return any(roll["arms"][a]["reward_diagonal"] is None for a in ARMS)


def reading(new: Path = NEW, meter: Path = METER, earn: Path = EARN, runner: Path = RUNNER) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "map": {}, "reward": {}, "accuracy": {}, "refusals": None,
           "spans": {}}
    base = _roll(meter)
    got = {"earned": _roll(new), "meter": base}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"the {label} run is absent, or carries no replicate to read"}
    if _reward_missing(got["earned"]) or _reward_missing(got["meter"]):
        return {**out, "ok": False, "reason": "a run carries no reward matrix, so the payout's two levels are not "
                                             "readable"}
    out["runs"] = got
    against = {"earned": _against(got["earned"], got["meter"]), "meter": _against(base, base)}
    out["map"] = {"earned": _map(got["earned"]), "one_trial": _map(_roll(earn))}
    out["refusals"] = refusals(runner)
    out["reward"] = {a: _paired(got["earned"]["arms"][a]["reward_diagonal"],
                                got["meter"]["arms"][a]["reward_diagonal"]) for a in ARMS}
    out["accuracy"] = {a: _paired(got["earned"]["arms"][a]["accuracy_diagonal"],
                                  got["meter"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "episode": EPISODE, "chance": CHANCE,
        "bar": BAR, "tol": TOL, "sigma": SIGMA, "arms_needed": ARMS_NEEDED,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "config": against,
        "draw": {label: against[label]["draw"] for label in against},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), PLACES)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), PLACES)
                                  for a in ARMS} for label in got},
        "reward_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["reward_diagonal"]), PLACES)
                                    for a in ARMS} for label in got},
        "reward_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["reward_last"]), PLACES)
                                for a in ARMS} for label in got},
        "map_move": {"earned": (None if out["map"]["earned"] is None else
                                {a: {"mean": round(out["map"]["earned"][a]["mean"], PLACES),
                                     "smallest": round(out["map"]["earned"][a]["smallest"], PLACES)}
                                 for a in ARMS}),
                     "one_trial": (None if out["map"]["one_trial"] is None else
                                   {a: {"mean": round(out["map"]["one_trial"][a]["mean"], PLACES)}
                                    for a in ARMS})},
        "refusals": out["refusals"],
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    cfg = s["config"]["earned"]
    draw = s["draw"]["earned"]
    moved = cfg["moved"]
    mine_moved = {k: moved.get(k) for k in MOVED}
    theirs_moved = {k: s["config"]["meter"]["moved"].get(k) for k in MOVED}
    moved_ok = all(mine_moved[k] is True for k in MOVED) and all(theirs_moved[k] in (None, False) for k in MOVED)
    draw_ok = not draw["added"] and not draw["differ"] and not draw["missing"]
    ref = s["refusals"]
    if ref is None:
        j1 = {"id": "QA1",
              "measured": "the runner's source could not be read, so its own refusal messages are not compared",
              "verdict": "REFUSED -- the runner is absent, so whether it refuses the pair is not computed"}
    else:
        j1 = {"id": "QA1",
              "measured": f"the config: **{len(cfg['differ'])}** differing past the inert rule ({cfg['differ']}) over "
                          f"**{cfg['same'] + len(cfg['inert'])}** fields, the fields moved {mine_moved} against the "
                          f"meter run's {theirs_moved}; the draw: **{len(draw['agree'])}** fields with "
                          f"**{len(draw['differ'])}** differing, **{len(draw['added'])}** added and "
                          f"**{len(draw['missing'])}** missing; replicates {s['replicates']}; the runner's "
                          f"**{ref['messages']}** refusal messages with **{len(ref['naming_the_ascent'])}** naming "
                          f"the ascent and **{len(ref['naming_the_pair'])}** naming the pair",
              "verdict": "MET -- the paid episodic pass runs with the map earned, one world and one payout, two flags "
                         "from the paid meter run" if (not cfg["differ"] and moved_ok and draw_ok
                                                       and s["replicates"] == [MIN_REPS]
                                                       and not ref["pair_refused"]) else
                         f"FALSIFIER FIRED -- differing {cfg['differ']}, moved {mine_moved} against "
                         f"{theirs_moved}, draw {draw}, replicates {s['replicates']}, refused "
                         f"{ref['pair_refused']} ({ref['naming_the_pair']})"}
    mv, one = r["map"]["earned"], r["map"]["one_trial"]
    if one is None:
        j2 = {"id": "QA2", "measured": "the map's distance from the identity on the new run has no instrument beside "
                                        "it",
              "verdict": f"REFUSED -- {EARN.name} is absent, so the instrument's own movement is not beside it"}
    else:
        thin = ([] if mv is None else
                [a for a in ARMS if mv[a]["above_zero"] != mv[a]["replicates"] or mv[a]["smallest"] <= 0.0])
        up = [a for a in ARMS if r["reward"][a]["mean"] > 0.0 and r["reward"][a]["sigma"] >= SIGMA]
        j2 = {"id": "QA2",
              "measured": (f"the map's distance from the identity is **{mv}** on the new run against "
                           f"**{ {a: round(one[a]['mean'], PLACES) for a in ARMS} }** on `e488`'s own earn run; the "
                           f"reward's diagonal less the meter run's, paired over the replicates: "
                           f"**{ {a: round(r['reward'][a]['mean'], PLACES) for a in ARMS} }** at "
                           f"**{ {a: round(r['reward'][a]['sigma'], 2) for a in ARMS} }** sigma, from "
                           f"**{s['reward_diagonal']['earned']}** against "
                           f"**{s['reward_diagonal']['meter']}**"
                           if mv is not None else "the new run records no policy movement on any replicate"),
              "verdict": f"MET -- the payout reaches the map on every replicate and lifts the reward's diagonal "
                         f"above the meter run's on **{len(up)}** of three arms ({up})" if (mv is not None
                                                                                             and not thin
                                                                                             and len(up) == len(ARMS))
                         else f"FALSIFIER FIRED -- thin {thin}, {len(up)} of three arms lifting at two sigma "
                              f"({up}), moved {mv is not None}"}
    diag = s["accuracy_diagonal"]
    under = [a for a in ARMS if diag["earned"][a] < diag["meter"][a] - TOL]
    over = [a for a in ARMS if diag["earned"][a] >= CHANCE + BAR]
    j3 = {"id": "QA3",
          "measured": f"the new run's accuracy diagonals **{diag['earned']}** against the meter run's "
                      f"**{diag['meter']}**, all **{len(over)}** of three arms at least {BAR:.2f} above the chance "
                      f"of {CHANCE:.2f} and **{len(under)}** more than {TOL:.2f} under the meter run's "
                      f"({under}), for changes of "
                      f"**{ {a: round(r['accuracy'][a]['mean'], PLACES) for a in ARMS} }** at "
                      f"**{ {a: round(r['accuracy'][a]['sigma'], 2) for a in ARMS} }** sigma",
          "verdict": f"MET -- the pass is still learned with the map paid: **{len(over)}** of three arms over the bar "
                     f"({over}) and none more than {TOL:.2f} under the meter run's"
                     if (len(over) >= ARMS_NEEDED and not under) else
                     f"FALSIFIER FIRED -- {len(over)} of three arms over the bar ({over}), under the meter run's by "
                     f"more than {TOL:.2f}: {under}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the pass plays for the payout ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e498` made the episodic pass payable and left the payout a meter; this gives the map the agent")
    print("   acts through the payout's own optimizer and reads the same pass again")
    print(f"\n   {'arm':<10} {'reward earn':>12} {'reward meter':>13} {'payout gain':>12} {'sigma':>7} "
          f"{'acc earn':>9} {'acc meter':>10} {'d acc':>8} {'map move':>9}")
    for a in ARMS:
        g, c = r["reward"][a], r["accuracy"][a]
        moved = (0.0 if r["map"]["earned"] is None else r["map"]["earned"][a]["mean"])
        print(f"   {a:<10} {r['spans']['reward_diagonal']['earned'][a]:>12.4f} "
              f"{r['spans']['reward_diagonal']['meter'][a]:>13.4f} {g['mean']:>+12.4f} {g['sigma']:>7.2f} "
              f"{r['spans']['accuracy_diagonal']['earned'][a]:>9.4f} "
              f"{r['spans']['accuracy_diagonal']['meter'][a]:>10.4f} {c['mean']:>+8.4f} {moved:>9.4f}")
    cfg, draw = r["spans"]["config"]["earned"], r["spans"]["draw"]["earned"]
    print(f"\n   the config: {len(cfg['differ'])} differing past the inert rule {cfg['differ']}; "
          f"the fields moved {cfg['moved']}")
    print(f"   the draw: {len(draw['agree'])} fields with {len(draw['differ'])} differing, {len(draw['added'])} added "
          f"and {len(draw['missing'])} missing")
    ref = r["spans"]["refusals"]
    print(f"   the runner's refusals: {0 if ref is None else ref['messages']} messages, "
          f"{0 if ref is None else len(ref['naming_the_pair'])} naming the pair")
    print("\n== the registered claims, QA1-QA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e488` earned at one trial per pass; `e498` paid the episodic pass; this is the pass played for)")
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
