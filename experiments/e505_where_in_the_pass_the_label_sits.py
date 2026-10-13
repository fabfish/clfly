"""E505 -- where in the pass the label sits: whether the placement's own order is the axis the label-first clause names.

`e495` moved the cue the label names from the episode's last trial to its first and the pass came back at **0.8299**,
**0.8139** and **0.8267**; `e497` put a second distractor in the same window and it stayed a family (**0.8538**,
**0.8392** and **0.8580**). Both measured a **pair** of placements -- the label's cue at the episode's **first** trial
or at its **last** -- and every unit since named the interior placements as a unit whose placement and window cannot
be separated by moving the one flag. **This unit measures the axis**: the same pass, the same read, the same world
and the same boundary channel with the label at trial **0**, **1** and **2** of a three-trial pass, so the label's
window is eleven, seven and three drive steps to the read.

Three runs and one instrument:

  * `e505 ... label_at1` -- `e497`'s own command with `--loop-label-at 1` in place of `--loop-label-first`, so the
    label is at the pass's second trial and its window is seven drive steps (new);
  * `e505 ... label_at2` -- the same command with `--loop-label-at 2`, the label at the pass's last trial, three
    drive steps (new);
  * `e497 ... episode3_labelfirst` -- the same command with `--loop-label-first`, the label at trial 0, eleven drive
    steps, which is the placement the other two move.

Three claims, registered before either new run's reading was opened.

- **VA1 -- the flag moves the placement and nothing else.** Against `e497`'s own run each new run's recorded `config`
  agrees on every field except the placement, the output path and the saved weights; its draw differs in the
  placement field only; and each run carries **twenty** replicates. **Falsifier**: any other config field differing,
  a draw field added or missing beyond the placement, or a replicate count other than twenty.
- **VA2 -- the placement orders the pass.** On **at least two of the three arms** the accuracy diagonal is
  non-increasing from the label at trial **0** to trial **1** to trial **2**, and on **at least two of the three
  arms** the end-to-end move, trial **0** less trial **2**, is positive and resolved at **two** sigma.
  **Falsifier**: fewer than two arms non-increasing, or fewer than two arms whose end-to-end move resolves. *It can
  fire: the label last is the placement every run before `e495` carried, and at three trials it leaves the label
  three drive steps -- the shortest window the pass has.*
- **VA3 -- the label's window is what orders it.** Measured at the card's body with deterministic cues and the
  episode's other symbols held fixed, the label's own part of the read at the last step falls as the placement moves
  later. **Falsifier**: a share that does not fall.

**What it can do beyond that.** It reads the clause `e495`, `e496` and `e497` each wrote as a **pair** and says
whether the axis the pair sits on is a **graded** one: if the pass falls as the label moves later, the clause's
mechanism is the label's window and the pair's two points are its ends; if it does not, the axis is the two
placements and the pair is the whole of it. Either way the placement is read with the pass's length, read, world and
boundary channel held fixed.

**What it cannot do.** *Three placements are not a curve's shape*: trials 0, 1 and 2 are three points, and a knee
between them, or a placement beyond them at a longer pass, is not in it. *And one episode length*: a three-trial pass
of four steps, so the four- and six-trial splits and the placement beyond the pass's own three trials are not
separated here -- the placement and the pass's length still move together. *And one read and one body*: the model's
own thirty-two columns, which `e493` showed is the better of the corpus's two, at a body that has never been
trained, so a share is where that body puts the label and the trained arms are the measurement. *And the payout is
not on these runs*: the three commands carry no `--loop-reward`, so nothing here is read against the world's
currency. *And one world, budget and seed stream*: the card's own setting with `--seed0 0`, so a second world and a
second stream are not in it.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments import e489_the_benchmark_has_an_episode as e489

#: the two new placements and the run they are read against -- `e497`'s own three-trial label-first run
ZERO = Path("runs/e497_earned_label_episode3_labelfirst_20reps.json")
ONE = Path("runs/e505_label_at1_episode3_20reps.json")
TWO = Path("runs/e505_label_at2_episode3_20reps.json")
ARMS = e489.ARMS
#: the placement, as the 0-based trial index of the pass whose cue is the label's, per run label
PLACE = {"at0": 0, "at1": 1, "at2": 2}
#: the fields the flag moves in the config and in the draw, and the run's own bookkeeping
MOVED = ("loop_label_first", "loop_label_at")
DRAW_MOVED = ("label_first", "label_at")
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = e489.EPISODE
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
SYMBOLS = 4
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
ARMS_NEEDED = 2
PLACES = 4
#: the drive steps each placement leaves between the label's cue and the read at the pass's last step: the trial
#: length is ``tau // episode`` and the read is at ``tau - 1``, so trial ``at`` leaves ``tau - 1 - at * trial_len``
WINDOW = {at: (TAU - 1) - at * (TAU // EPISODE) for at in PLACE.values()}
CLAIMS = (
    ("VA1", "the flag moves the placement and nothing else",
     "Against e497's own run each new run's recorded config agrees on every field except the placement, the output "
     "path and the saved weights; its draw differs in the placement field only; and each run carries twenty "
     "replicates",
     "falsifier: any other config field differing, a draw field added or missing beyond the placement, or a "
     "replicate count other than twenty"),
    ("VA2", f"the placement orders the pass, on {ARMS_NEEDED} arms at {SIGMA:.0f} sigma",
     "On at least two of the three arms the accuracy diagonal is non-increasing from the label at trial 0 to trial 1 "
     "to trial 2, and on at least two arms the end-to-end move, trial 0 less trial 2, is positive and resolved at "
     "two sigma",
     "falsifier: fewer than two arms non-increasing, or fewer than two arms whose end-to-end move resolves"),
    ("VA3", "the label's window is what orders it",
     "Measured at the card's body with deterministic cues and the episode's other symbols held fixed, the label's own "
     "part of the read at the last step falls as the placement moves later",
     "falsifier: a share that does not fall"),
)


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in BOOKKEEPING:
        return True
    if {old, new} == {None, False}:
        return True
    return False


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


def _roll(path: Path, other: dict | None) -> dict | None:
    """One run's per-arm reading, with its config and draw against ``other``'s (the base run's).

    The config's one comparison and the draw's one are the flag's own: the placement is a pair of fields, so what
    the comparison is asked is whether every field **outside** that pair agrees and whether the pair itself moved the
    way the flag says. A run without a replicate, or without its base to compare against, is unreadable.
    """
    doc = load(path)
    if not doc or other is None:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                    "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps]}
    cfg = doc.get("config") or {}
    their_cfg = other.get("config") or {}
    same, inert, differ = {}, {}, {}
    for k in sorted(set(cfg) | set(their_cfg)):
        old, new = their_cfg.get(k), cfg.get(k)
        if old == new:
            same[k] = new
        elif _inert(k, old, new):
            inert[k] = [old, new]
        else:
            differ[k] = [old, new]
    mine, theirs = doc.get("env_draw") or {}, other.get("env_draw") or {}
    agree = {k: theirs.get(k) == mine.get(k) for k in theirs}
    return {"artifact": path.name, "arms": got,
            "config": {"same": len(same), "inert": sorted(inert), "differ": differ,
                       "moved": {k: cfg.get(k) for k in MOVED}},
            "draw": {"agree": agree, "differ": sorted(k for k, ok in agree.items() if not ok),
                     "added": sorted(set(mine) - set(theirs)), "missing": sorted(set(theirs) - set(mine))}}


def read_share(circ, net) -> dict:
    """The label's own part of the read at the last step, at the three placements.

    The cues are deterministic and the episode's other symbols are held fixed across the examples, so one symbol is
    one trajectory and what varies from one symbol to the next is the label. What is reported for each placement is
    the across-symbol spread as a share of that read's own scale, **one width, one read, one world, three
    placements** -- and, beside each, the window in drive steps the placement leaves between the label's cue and the
    read.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    n = SYMBOLS * 12
    y = np.arange(n) % SYMBOLS
    other = np.tile(np.arange(1, EPISODE, dtype=np.int64), (n, 1)) % SYMBOLS
    got = {}
    for label, at in PLACE.items():
        env = fly_env.build(circ, readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0,
                            noise=0.0, world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0,
                            boundary=True, episode=EPISODE, label_at=at)
        u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=other), dtype=np.float32))
        fn = env.feedback()
        with torch.no_grad():
            traj = net(u, feedback=fn)
        w = traj[:, -1, :][:, rs].detach()
        means = [w[y == s].mean(dim=0) for s in range(SYMBOLS)]
        across = max(float((means[i] - means[j]).norm()) for i in range(SYMBOLS) for j in range(i + 1, SYMBOLS))
        within = statistics.fmean([float((w[y == s] - means[s]).norm(dim=1).mean()) for s in range(SYMBOLS)])
        scale = float(w.norm(dim=1).mean())
        got[label] = {"at": at, "trials": EPISODE, "window": WINDOW[at], "across": across, "within": within,
                      "scale": scale, "share": (across / scale) if scale else 0.0, "width": int(w.shape[1])}
    return got


def reading(zero: Path = ZERO, one: Path = ONE, two: Path = TWO) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    base = load(zero)
    if base is None:
        return {**out, "ok": False, "reason": "the label-at-0 run is absent"}
    got = {"at0": _roll(zero, base), "at1": _roll(one, base), "at2": _roll(two, base)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"the label-at-{PLACE[label]} run is absent"}
    out["runs"] = got
    try:
        import torch

        from clfly.connectome import annotate, circuits, graph
        from clfly.network.model import RateConfig, build_net

        torch.manual_seed(0)
        conn, ann = graph.build(), annotate.load_annotations()
        circ = circuits.extract(conn, ann, hops=0, max_neurons=SIZE)
        net = build_net(circ, RateConfig(tau=TAU)).torch_model()
        out["share"] = read_share(circ, net)
    except (ImportError, OSError, ValueError) as exc:
        return {**out, "ok": False, "reason": f"the connectome could not be built: {exc}"}
    #: the paired contrasts over the replicate seeds: one step at a time (trial 0 to 1, 1 to 2) and end to end
    out["recovery"] = {
        "end_to_end": {a: _paired(got["at0"]["arms"][a]["accuracy_diagonal"],
                                  got["at2"]["arms"][a]["accuracy_diagonal"]) for a in ARMS},
        "step_01": {a: _paired(got["at0"]["arms"][a]["accuracy_diagonal"],
                               got["at1"]["arms"][a]["accuracy_diagonal"]) for a in ARMS},
        "step_12": {a: _paired(got["at1"]["arms"][a]["accuracy_diagonal"],
                               got["at2"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "placements": dict(PLACE), "windows": dict(WINDOW),
        "episode": EPISODE, "trial_len": TAU // EPISODE, "chance": CHANCE, "sigma": SIGMA,
        "arms_needed": ARMS_NEEDED,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        #: the config and the draw are carried **inside the spans**, as every unit's reading is: a top-level
        #: `config` would be counted as a run's own configuration by the corpus's own census
        "config": {label: got[label]["config"] for label in got},
        "draw": {label: got[label]["draw"] for label in got},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), PLACES)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), PLACES)
                                  for a in ARMS} for label in got},
        "share": {label: round(out["share"][label]["share"], PLACES) for label in got},
    }
    return out


def _draw_extra(draw: dict) -> list:
    """The draw fields that moved outside the placement: the pair is allowed to move, nothing else is."""
    return [k for k in (draw.get("differ", []) + draw.get("added", []) + draw.get("missing", []))
            if k not in DRAW_MOVED]


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    #: VA1 -- the flag moves the placement and nothing else
    rows, bad = {}, []
    for label in ("at1", "at2"):
        cfg = s["config"][label]
        draw = s["draw"][label]
        extra = _draw_extra(draw)
        rows[label] = {"differ": cfg["differ"], "moved": cfg["moved"], "added": draw["added"],
                       "missing": draw["missing"], "differed": draw["differ"], "extra": extra,
                       "replicates": s["replicates"]}
        if cfg["differ"] or extra or s["replicates"] != [MIN_REPS]:
            bad.append(label)
    j1 = {"id": "VA1",
          "measured": "; ".join(
              f"the label-at-{PLACE[label]} run: **{len(rows[label]['differ'])}** config fields differing past the "
              f"inert rule ({rows[label]['differ']}), the draw adding {rows[label]['added']} and dropping "
              f"{rows[label]['missing']} with **{rows[label]['extra']}** outside the placement; replicates "
              f"{rows[label]['replicates']}" for label in ("at1", "at2")),
          "verdict": "MET -- the flag moves the placement and nothing else: the placement pair is the only field past "
                     "the base run's, and the draw moves the placement and nothing else" if not bad else
                     f"FALSIFIER FIRED -- {bad} over { {label: rows[label] for label in bad} }"}
    #: VA2 -- the placement orders the pass
    diag = s["accuracy_diagonal"]
    rec = r["recovery"]["end_to_end"]
    ordered = [a for a in ARMS if diag["at0"][a] >= diag["at1"][a] >= diag["at2"][a]]
    resolved = [a for a in ARMS if rec[a]["mean"] > 0.0 and rec[a]["sigma"] >= SIGMA]
    j2 = {"id": "VA2",
          "measured": f"the accuracy diagonals at the three placements are trial 0 {diag['at0']}, trial 1 "
                      f"{diag['at1']} and trial 2 {diag['at2']} against a chance of {CHANCE:.2f}, with "
                      f"**{len(ordered)}** of three arms non-increasing ({ordered}); the end-to-end move, trial 0 "
                      f"less trial 2, is { {a: round(rec[a]['mean'], PLACES) for a in ARMS} } at "
                      f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, resolving on **{len(resolved)}** of "
                      f"three arms ({resolved})",
          "verdict": f"MET -- the placement orders the pass: **{len(ordered)}** of three arms fall from trial 0 to "
                     f"trial 2 and **{len(resolved)}** resolve, both at the bar of {ARMS_NEEDED}" if
                     (len(ordered) >= ARMS_NEEDED and len(resolved) >= ARMS_NEEDED) else
                     f"FALSIFIER FIRED -- {len(ordered)} of three arms non-increasing ({ordered}) and "
                     f"{len(resolved)} resolving ({resolved}), needing {ARMS_NEEDED} of each"}
    #: VA3 -- the label's window is what orders it
    sh = r["share"]
    seq = [sh[label]["share"] for label in ("at0", "at1", "at2")]
    falls = seq[0] > seq[1] > seq[2]
    j3 = {"id": "VA3",
          "measured": f"the label's own part of the read at the last step as a share of its scale, at {EPISODE} "
                      f"trials with deterministic cues: the label at trial 0 **{seq[0]:.4f}** (window "
                      f"{sh['at0']['window']} drive steps), trial 1 **{seq[1]:.4f}** ({sh['at1']['window']}) and "
                      f"trial 2 **{seq[2]:.4f}** ({sh['at2']['window']}), over the spreads "
                      f"{ {label: round(sh[label]['across'], PLACES) for label in ('at0', 'at1', 'at2')} }",
          "verdict": f"MET -- the label's share falls as the placement moves later ({seq[0]:.4f} > {seq[1]:.4f} > "
                     f"{seq[2]:.4f})" if falls else
                     f"FALSIFIER FIRED -- the shares do not fall ({seq[0]:.4f}, {seq[1]:.4f}, {seq[2]:.4f})"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== where in the pass the label sits ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e495` and `e497` each read a pair of placements -- the label's cue at the pass's first trial or its")
    print("   last; this moves it across a three-trial pass at trial 0, 1 and 2 and reads the same pass, world and")
    print("   boundary channel")
    print(f"\n   {'arm':<10} {'trial 0':>10} {'trial 1':>10} {'trial 2':>10} {'0-1':>9} {'1-2':>9} {'0-2':>9} "
          f"{'0-2 sig':>8}")
    for a in ARMS:
        s01, s12, e2 = r["recovery"]["step_01"][a], r["recovery"]["step_12"][a], r["recovery"]["end_to_end"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['at0'][a]:>10.4f} "
              f"{r['spans']['accuracy_diagonal']['at1'][a]:>10.4f} "
              f"{r['spans']['accuracy_diagonal']['at2'][a]:>10.4f} {s01['mean']:>+9.4f} {s12['mean']:>+9.4f} "
              f"{e2['mean']:>+9.4f} {e2['sigma']:>8.2f}")
    print(f"\n   the label's share of the read at the last step: trial 0 {r['share']['at0']['share']:.4f} (window "
          f"{r['share']['at0']['window']}), trial 1 {r['share']['at1']['share']:.4f} (window "
          f"{r['share']['at1']['window']}), trial 2 {r['share']['at2']['share']:.4f} (window "
          f"{r['share']['at2']['window']}) drive steps")
    print(f"   the last row: trial 0 {r['spans']['accuracy_last']['at0']}, trial 1 "
          f"{r['spans']['accuracy_last']['at1']}, trial 2 {r['spans']['accuracy_last']['at2']}")
    print(f"   the config: the label-at-1 run differs past the inert rule in "
          f"{r['spans']['config']['at1']['differ']}, the label-at-2 run in "
          f"{r['spans']['config']['at2']['differ']}; the draw: the one adds "
          f"{r['spans']['draw']['at1']['added']} and drops {r['spans']['draw']['at1']['missing']}")
    print("\n== the registered claims, VA1-VA3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e495` and `e497` measured the pair; this is the axis the pair sits on)")
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
