"""E497 -- the label first at three trials: whether the working episodic pass survives one more distractor.

`e495` moved the cue the label names from the episode's last trial to its first and the same two-trial pass read
**0.8299**, **0.8139** and **0.8267** where it had been short of the bar on every arm, and `e496` carried that into
the card as the configuration the episode's label has to be in. **What that left unmeasured is crowding**: the
two-trial pass puts **one** distractor after the label, and the pass's own split at three trials puts **two** -- the
label's cue at step **0**, its distractors at steps **4** and **8**, and the read at step **11** just as before. So
the label's window is the same eleven drive steps and what the pass adds is a second cue in it.

One run and one instrument:

  * `e497 ... episode3_labelfirst` -- `e495`'s own command with `--loop-episode 3` instead of 2, so the pass holds
    three trials of four steps with the label first (new);
  * `e495 ... episode2_labelfirst` -- the same read, the same placement, the same world and the same boundary
    channel at two trials of six steps, which is the pass this one adds a cue to.

Three claims, registered before the new run's reading was opened.

- **NB1 -- and the pass's split is the one flag moved.** Against `e495`'s run every recorded config field agrees
  except `loop_episode` (three against two), the output path and the saved weights, and every draw field agrees
  except `episode_len` (three against two), the boundary channel's own three fields being the same channel; each run
  carries twenty replicates. **Falsifier**: any other config field differing, a draw field differing past
  `episode_len`, or a replicate count other than twenty.
- **NB2 -- and the label keeps its place in the read under one more cue.** Measured at the card's own body with
  deterministic cues and the episode's other symbols held fixed, the label's own part of the read at the last step is
  **positive and within a factor of two** of its two-trial value, with both shares and both spreads carried beside
  them. **Falsifier**: a share that is not positive, or one outside the factor of two.
- **NB3 -- and the pass is still learned with two distractors.** On **at least two of the three arms** the new run's
  accuracy diagonal is at least **0.10** above the four-class chance of **0.25** and **within 0.10** of
  `e495`'s own. **Falsifier**: fewer than two arms over the bar, or an arm more than **0.10** under the two-trial
  run's. *It can fire: a second cue in the same window is one more thing the recurrence has to hold while the label
  decays, and the two-trial pass's arms are **0.8139** to **0.8299**.*

**What it can do beyond that.** It says whether the card's new clause is a **configuration** or a coincidence of the
smallest pass: `e495` read the two-trial case and `e496` wrote it down, and this is the first rung of the sweep that
clause's own *cannot do* names. If the pass holds at three trials the episodic mode is a family and not a point; if
it falls, the clause's scope is the two-trial split and the pass's cost is crowding after the label.

**What it cannot do.** *One rung*: three trials against two, with the four- and six-trial splits, and the passes with
the label at an interior trial, not in it. *And the split moves two things*: one more trial is one more **cue** and a
shorter **trial**, and no split of a fixed twelve-step pass separates them -- so a change here is the pass's shape and
not a crowding constant. *And the instrument is at an untrained body*: a share is where a body that has never been
trained puts the label, and the trained arms are the measurement. *And one read*: the model's own thirty-two columns,
which `e493` showed is the better of the corpus's two. *And one budget, one world and one seed stream*: the card's
own setting.
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
from experiments import e495_the_label_first as e495
from experiments.e172_parser_registry import parser_flags

#: the new run and the two-trial pass it is read against
THREE = Path("runs/e497_earned_label_episode3_labelfirst_20reps.json")
TWO = e495.FIRST
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
#: the one field the run moves in the configuration, and the one its draw moves
MOVED = ("loop_episode",)
DRAW_MOVED = ("episode_len",)
BOOKKEEPING = ("json_out", "save_theta")
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
SYMBOLS = e495.SYMBOLS
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
BAR = 0.10
#: how far the label's share may move between the two splits and still be "its place"
FACTOR = 2.0
CLAIMS = (
    ("NB1", "and the pass's split is the one flag moved",
     "Against e495's run every recorded config field agrees except loop_episode, the output path and the saved "
     "weights, and every draw field agrees except episode_len, with twenty replicates each",
     "falsifier: any other config field differing, a draw field differing past episode_len, or a replicate count "
     "other than twenty"),
    ("NB2", f"and the label keeps its place in the read under one more cue, within a factor of {FACTOR:.0f}",
     "Measured at the card's own body with deterministic cues and the episode's other symbols held fixed, the label's "
     "own part of the read at the last step is positive and within a factor of two of its two-trial value",
     "falsifier: a share that is not positive, or one outside the factor of two"),
    ("NB3", f"and the pass is still learned with two distractors, at {BAR:.2f}",
     "On at least two of the three arms the new run's accuracy diagonal is at least 0.10 above the four-class chance "
     "of 0.25 and within 0.10 of e495's own",
     "falsifier: fewer than two arms over the bar, or an arm more than 0.10 under the two-trial run's"),
)


def _defaults() -> dict:
    try:
        return {k: (False if meta.get("store_true") else meta.get("default"))
                for k, meta in parser_flags(RUNNER).items()}
    except (OSError, ValueError):
        return {}


DEFAULTS = _defaults()


def _inert(key: str, old, new) -> bool:
    if key in MOVED or key in DRAW_MOVED or key in BOOKKEEPING:
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


def _roll(path: Path, other: dict | None) -> dict | None:
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
    draw = {k: theirs.get(k) == mine.get(k) for k in sorted(set(mine) | set(theirs)) if k not in DRAW_MOVED}
    return {"artifact": path.name, "arms": got,
            "config": {"same": len(same), "inert": sorted(inert), "differ": differ,
                       "moved": {k: cfg.get(k) for k in MOVED}},
            "draw": {"fields": len(draw), "differ": sorted(k for k, ok in draw.items() if not ok),
                     "moved": {k: [theirs.get(k), mine.get(k)] for k in DRAW_MOVED}}}


def read_share(circ, net) -> dict:
    """The label's own part of the read at the last step, at three trials and at two.

    The cues are deterministic and the episode's other symbols are held fixed across the examples, so one symbol is
    one trajectory and what varies from one symbol to the next is the label. What is reported for each split is the
    across-symbol spread as a share of that read's own scale, **one width, one read, one placement, two splits**.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    n = SYMBOLS * 12
    y = np.arange(n) % SYMBOLS
    got = {}
    for label, trials in (("two", 2), ("three", 3)):
        env = fly_env.build(circ, readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0,
                            noise=0.0, world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0,
                            boundary=True, episode=trials, label_first=True)
        other = np.tile(np.arange(1, trials, dtype=np.int64), (n, 1)) % SYMBOLS
        u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=other), dtype=np.float32))
        fn = env.feedback()
        with torch.no_grad():
            traj = net(u, feedback=fn)
        w = traj[:, -1, :][:, rs].detach()
        means = [w[y == s].mean(dim=0) for s in range(SYMBOLS)]
        across = max(float((means[i] - means[j]).norm()) for i in range(SYMBOLS) for j in range(i + 1, SYMBOLS))
        within = statistics.fmean([float((w[y == s] - means[s]).norm(dim=1).mean()) for s in range(SYMBOLS)])
        scale = float(w.norm(dim=1).mean())
        got[label] = {"trials": trials, "across": across, "within": within, "scale": scale,
                      "share": (across / scale) if scale else 0.0, "width": int(w.shape[1])}
    return got


def reading(three: Path = THREE, two: Path = TWO) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    other = load(two)
    got = {"three": _roll(three, other), "two": _roll(two, other)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"{label} is absent"}
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
    out["recovery"] = {a: _paired(got["three"]["arms"][a]["accuracy_diagonal"],
                                  got["two"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "chance": CHANCE, "factor": FACTOR,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "config": {label: got[label]["config"] for label in got},
        "draw": {label: got[label]["draw"] for label in got},
        "accuracy_diagonal": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_diagonal"]), 4)
                                      for a in ARMS} for label in got},
        "accuracy_last": {label: {a: round(statistics.fmean(got[label]["arms"][a]["accuracy_last"]), 4)
                                  for a in ARMS} for label in got},
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": f"REFUSED -- {r.get('reason', 'a run is absent')}"}
                for c in CLAIMS]
    s = r["spans"]
    moved = s["config"]["three"]["moved"]
    differ = s["config"]["three"]["differ"]
    draw = s["draw"]["three"]
    j1 = {"id": "NB1",
          "measured": f"the config: **{len(differ)}** differing past the inert rule ({differ}), the field moved "
                      f"{moved}; the draw: {draw['fields']} fields compared with **{draw['differ']}** differing, "
                      f"`episode_len` moving {draw['moved'].get('episode_len')}; replicates {s['replicates']}",
          "verdict": "MET -- the pass's split is the one flag moved, and the boundary channel is the same channel" if
                     (not differ and moved.get("loop_episode") == 3 and not draw["differ"]
                      and draw["moved"].get("episode_len") == [2, 3] and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- differing {differ}, moved {moved}, draw {draw}, replicates "
                     f"{s['replicates']}"}
    share = r["share"]
    two, three = share["two"], share["three"]
    inside = two["share"] / FACTOR <= three["share"] <= two["share"] * FACTOR
    j2 = {"id": "NB2",
          "measured": f"the label's own part of the read at the last step as a share of its scale, the label first: "
                      f"at two trials **{two['share']:.4f}** (spread {two['across']:.4f} against a scale of "
                      f"{two['scale']:.4f}) against three trials **{three['share']:.4f}** (spread "
                      f"{three['across']:.4f}, scale {three['scale']:.4f}), a factor of "
                      f"{three['share'] / two['share'] if two['share'] else 0.0:.4f}",
          "verdict": "MET -- the label keeps its place in the read with one more cue in the pass" if
                     (three["share"] > 0.0 and inside) else
                     f"FALSIFIER FIRED -- three-trial share {three['share']:.4f} against two trials' "
                     f"{two['share']:.4f}, inside the factor {inside}"}
    rec = r["recovery"]
    diag = s["accuracy_diagonal"]["three"]
    base = s["accuracy_diagonal"]["two"]
    up = [a for a in ARMS if diag[a] >= CHANCE + BAR and diag[a] >= base[a] - BAR]
    thin = [a for a in ARMS if diag[a] < CHANCE + 0.05]
    j3 = {"id": "NB3",
          "measured": f"the three-trial run's accuracy diagonals are {diag} against a chance of {CHANCE:.2f}, and "
                      f"against the two-trial run's {base} they change by "
                      f"{ {a: round(rec[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, with {len(up)} of three arms over "
                      f"the bar and within {BAR:.2f} of the two-trial run, and {len(thin)} within 0.05 of chance",
          "verdict": f"MET -- the pass is still learned with two distractors, on **{len(up)}** of three arms ({up})"
                     if (len(up) >= 2 and not thin) else
                     f"FALSIFIER FIRED -- {len(up)} of three arms over the bar and within {BAR:.2f} ({up}), thin "
                     f"{thin}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the label first at three trials ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e495` and `e496` read and recorded the two-trial pass with the label first -- one distractor after")
    print("   it; this is the same read, placement and world with a second distractor in the same window")
    print(f"\n   {'arm':<10} {'three trials':>12} {'two trials':>11} {'change':>9} {'sigma':>7} {'three last':>11} "
          f"{'two last':>10}")
    for a in ARMS:
        c = r["recovery"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['three'][a]:>12.4f} "
              f"{r['spans']['accuracy_diagonal']['two'][a]:>11.4f} {c['mean']:>+9.4f} {c['sigma']:>7.2f} "
              f"{r['spans']['accuracy_last']['three'][a]:>11.4f} "
              f"{r['spans']['accuracy_last']['two'][a]:>10.4f}")
    print(f"\n   the label's share of the read, the label first: two trials {r['share']['two']['share']:.4f} against "
          f"three {r['share']['three']['share']:.4f} (spreads {r['share']['two']['across']:.4f} and "
          f"{r['share']['three']['across']:.4f})")
    print(f"   the config: {len(r['spans']['config']['three']['differ'])} differing past the inert rule; the draw: "
          f"differing {r['spans']['draw']['three']['differ']} with `episode_len` moving "
          f"{r['spans']['draw']['three']['moved'].get('episode_len')}")
    print("\n== the registered claims, NB1-NB3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e495` read the smallest pass with the label first; this is the rung above it)")
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
