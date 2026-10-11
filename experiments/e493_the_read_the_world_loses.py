"""E493 -- the read: the world's eight numbers against the model's own thirty-two, inside the episode.

`e489` and `e492` took the pass's splits apart and found the label's path to the read collapsing at the first trial:
at the card's body the label's own part of the **world's** state at the read step is **0.9144** when the pass is one
trial, **0.0377** at two and **0.0001** at three, and every arm sits at the four-class chance at two and three. So
the last thing `e492` named is the **read** itself: eight world numbers and a linear head, and a residue of **5.7%**
of the state at two trials. **This unit changes the read and nothing else.** The corpus already holds the two
one-trial readings of the same world -- `e438` at the world's eight numbers (**0.7691**, **0.7073**, **0.7389** across
the three arms) and `e455` at the model's own thirty-two (**0.8642**, **0.8559**, **0.8503**), so at one trial the
model's own state is the **better** read -- and what has never been read is the model's own columns **inside the
episode**.

One run and one instrument:

  * `e493 ... episode2_modelread` -- `e492`'s own command with `--readout-from-world` **off**, so the head reads the
    thirty-two model neurons of `--readout-size` at the last step instead of the world's eight (new);
  * `e492 ... episode2_boundary` -- the same pass, the same world and the same boundary channel with the world's
    eight numbers, which is the read this one replaces;
  * `e455 ... neurons` at one trial is carried beside both, since it is the same read at the corpus's own pass.

Three claims, registered before the new run's reading was opened.

- **JB1 -- and the read is the one flag moved.** Against `e492`'s boundary run every recorded config field agrees
  except `readout_from_world`, the output path and the saved weights, and the environment's draw agrees on **every**
  field -- the same world, the same two trials, the same boundary channel -- with the read-out's own draw the same
  subset of the same seed and each run carrying twenty replicates. **Falsifier**: any other config field differing, a
  draw field differing, or a replicate count other than twenty.
- **JB2 -- and the label is in the model's own columns.** Measured at the card's own body with deterministic cues and
  the earlier trials held fixed, the label's own part of the read at the last step -- the across-symbol spread as a
  share of the read's own scale -- is **larger from the model's thirty-two columns than from the world's eight** at
  two trials, with the one-trial pair and the world's share inside the episode carried beside it. **Falsifier**: the
  model's share at or below the world's at two trials, or a share that is not positive on either.
- **JB3 -- and the label comes back when the head reads the model.** On **at least two of the three arms** the new
  run's accuracy diagonal is at least **0.10** above the four-class chance of **0.25** and above `e492`'s own at
  **two** sigma. **Falsifier**: fewer than two arms, or an arm within **0.05** of chance. *It can fire: what the
  episode does to the model's recurrent state is not something any unit in this line has measured, and a read that
  carries the label may still be a read whose label is the past's.*

**What it can do beyond that.** It separates the two things `e492` left joined -- the **pass** and the **read** -- and
it is the corpus's own experiment: the model's own state against the world's numbers, which `e455` and `e458` ran at
one trial and which the episode has never been asked. If the label comes back the episode is usable and the world's
eight numbers are what the card's read-out is paying for; if it does not, the episode costs the model's own state too
and the split, the carry and the read are all excluded together.

**What it cannot do.** *One episode length and one read*: two trials against the corpus's one, and thirty-two model
neurons against eight world numbers, with the widths fixed by the corpus's own flags. *And two things change with the
read*: its **source** -- the world's state or the model's -- and its **width**, and no flag separates them; `e458`'s
eight model neurons are the same source at the world's width and are one trial's. *And the instrument compares two
reads of different widths*: the share is scale-free and not dimension-free, so the comparison ranks the reads and
does not measure a quantity they share. *And one budget, one world and one seed stream*: the card's own setting.
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
from experiments import e492_the_episode_at_two_trials as e492
from experiments.e172_parser_registry import parser_flags

#: the new run and the two it is read against
MODEL = Path("runs/e493_earned_label_episode2_modelread_20reps.json")
WORLD = e492.TWO
ONE_TRIAL = Path("runs/e455_earned_label_neurons_20reps.json")
RUNNER = Path("experiments/e8_rate_network.py")
ARMS = e489.ARMS
MOVED = ("readout_from_world",)
BOOKKEEPING = ("json_out", "save_theta")
EPISODE = 2
TAU = e489.TAU
SIZE = e489.SIZE
READOUT_SIZE = e489.READOUT_SIZE
N_SYMBOLS = e489.N_SYMBOLS
SYMBOLS = e492.SYMBOLS
CHANCE = e489.CHANCE
MIN_REPS = 20
SIGMA = 2.0
BAR = 0.10
CLAIMS = (
    ("JB1", "and the read is the one flag moved",
     "Against e492's boundary run every recorded config field agrees except readout_from_world, the output path and "
     "the saved weights, and the environment's draw agrees on every field, with twenty replicates each",
     "falsifier: any other config field differing, a draw field differing, or a replicate count other than twenty"),
    ("JB2", "and the label is in the model's own columns",
     "Measured at the card's own body with deterministic cues and the earlier trials held fixed, the label's own part "
     "of the read at the last step is larger from the model's thirty-two columns than from the world's eight at two "
     "trials, with the one-trial pair beside them",
     "falsifier: the model's share at or below the world's at two trials, or a share that is not positive on either"),
    ("JB3", f"and the label comes back when the head reads the model, at {BAR:.2f} and {SIGMA:.0f} sigma",
     "On at least two of the three arms the new run's accuracy diagonal is at least 0.10 above the four-class chance "
     "of 0.25 and above e492's own at two sigma",
     "falsifier: fewer than two arms, or an arm within 0.05 of chance"),
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
    draw = {k: theirs.get(k) == mine.get(k) for k in sorted(set(mine) | set(theirs))}
    return {"artifact": path.name, "arms": got,
            "config": {"same": len(same), "inert": sorted(inert), "differ": differ,
                       "moved": {k: cfg.get(k) for k in MOVED}},
            "readout": doc.get("readout") or {},
            "draw": {"fields": len(draw), "differ": sorted(k for k, ok in draw.items() if not ok)}}


def read_share(circ, net) -> dict:
    """The label's own part of the read at the last step, from the world's columns and from the model's own.

    The cues are deterministic and the earlier trials are held fixed across the examples, so one symbol is one
    trajectory and what varies from one symbol to the next is the label. What is reported for each read is the
    across-symbol spread as a share of that read's own scale -- the quantity `e492` measured for the world's eight
    numbers -- at the two trials this unit runs and at one trial beside it.
    """
    import torch
    from clfly.network import env as fly_env

    rs = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=READOUT_SIZE, replace=False))
    common = dict(readout_subset=rs, seed=0, n_symbols=N_SYMBOLS, tau=TAU, scale=1.0, gain=1.0, noise=0.0,
                  world_modes=0, world_leak=0.35, world_dims=8, world_coupled=True, cue_at=0, boundary=True)
    n = SYMBOLS * 12
    y = np.arange(n) % SYMBOLS
    got = {}
    for k in sorted({EPISODE, 1}):
        env = fly_env.build(circ, **{**common, "episode": k})
        earlier = (np.tile(np.arange(1, k, dtype=np.int64), (n, 1)) % SYMBOLS if k > 1 else None)
        u = torch.from_numpy(np.asarray(env.cue_input(y, episode_symbols=earlier), dtype=np.float32))
        fn = env.feedback()
        with torch.no_grad():
            traj = net(u, feedback=fn)
        reads = {"world8": fn.last_world.detach(), "model32": traj[:, -1, :][:, rs].detach()}
        got[k] = {}
        for name, w in reads.items():
            means = [w[y == s].mean(dim=0) for s in range(SYMBOLS)]
            across = max(float((means[i] - means[j]).norm()) for i in range(SYMBOLS) for j in range(i + 1, SYMBOLS))
            within = statistics.fmean([float((w[y == s] - means[s]).norm(dim=1).mean()) for s in range(SYMBOLS)])
            scale = float(w.norm(dim=1).mean())
            got[k][name] = {"across": across, "within": within, "scale": scale,
                            "share": (across / scale) if scale else 0.0, "width": int(w.shape[1])}
    return got


def reading(model: Path = MODEL, world: Path = WORLD) -> dict:
    out = {"ok": True, "reason": None, "runs": {}, "share": {}, "recovery": {}, "one_trial": {}, "spans": {}}
    other = load(world)
    got = {"model": _roll(model, other), "world": _roll(world, other)}
    for label, value in got.items():
        if value is None:
            return {**out, "ok": False, "reason": f"{label} is absent"}
    out["runs"] = got
    one = load(ONE_TRIAL)
    if one:
        diag = {}
        for arm in ARMS:
            reps = ((one.get("methods") or {}).get(arm) or {}).get("replicates") or []
            if reps:
                diag[arm] = statistics.fmean([statistics.fmean(r["learned"]) for r in reps])
        out["one_trial"] = {"artifact": ONE_TRIAL.name, "accuracy_diagonal": {a: diag.get(a) for a in ARMS}}
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
    out["recovery"] = {a: _paired(got["model"]["arms"][a]["accuracy_diagonal"],
                                  got["world"]["arms"][a]["accuracy_diagonal"]) for a in ARMS}
    out["spans"] = {
        "arms": list(ARMS), "runs": list(got), "episode": EPISODE, "chance": CHANCE,
        "replicates": sorted({v["replicates"] for roll in got.values() for v in roll["arms"].values()}),
        "config": {label: got[label]["config"] for label in got},
        "draw": {label: got[label]["draw"] for label in got},
        "readout": {label: got[label]["readout"] for label in got},
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
    moved = s["config"]["model"]["moved"]
    differ = s["config"]["model"]["differ"]
    draw = s["draw"]["model"]
    j1 = {"id": "JB1",
          "measured": f"the config: **{len(differ)}** differing past the inert rule ({differ}), the field moved "
                      f"{moved}; the draw: {draw['fields']} fields of the world read's with **{len(draw['differ'])}** "
                      f"differing ({draw['differ']}); the read-out {s['readout']['model']} against "
                      f"{s['readout']['world']}; replicates {s['replicates']}",
          "verdict": "MET -- the read is the one flag moved, over one world and one boundary channel" if
                     (not differ and moved.get("readout_from_world") in (None, False) and not draw["differ"]
                      and s["replicates"] == [MIN_REPS]) else
                     f"FALSIFIER FIRED -- differing {differ}, moved {moved}, draw {draw}, replicates "
                     f"{s['replicates']}"}
    share = {int(k): v for k, v in r["share"].items()}
    two, one = share[EPISODE], share[1]
    j2 = {"id": "JB2",
          "measured": f"the label's own part of the read as a share of the read's scale, at two trials: the world's "
                      f"{two['world8']['width']} numbers **{two['world8']['share']:.4f}** against the model's "
                      f"{two['model32']['width']} columns **{two['model32']['share']:.4f}**; at one trial "
                      f"**{one['world8']['share']:.4f}** against **{one['model32']['share']:.4f}**",
          "verdict": "MET -- the label is in the model's own columns where the world's eight lose it" if
                     (two["model32"]["share"] > two["world8"]["share"] and two["model32"]["share"] > 0.0
                      and two["world8"]["share"] >= 0.0) else
                     f"FALSIFIER FIRED -- at two trials the world's share is {two['world8']['share']:.4f} and the "
                     f"model's {two['model32']['share']:.4f}"}
    rec = r["recovery"]
    diag = s["accuracy_diagonal"]["model"]
    up = [a for a in ARMS if diag[a] >= CHANCE + BAR and rec[a]["mean"] > 0.0 and rec[a]["sigma"] >= SIGMA]
    thin = [a for a in ARMS if diag[a] < CHANCE + 0.05]
    j3 = {"id": "JB3",
          "measured": f"the model-read run's accuracy diagonals are {diag} against a chance of {CHANCE:.2f}, and "
                      f"against the world-read run's {s['accuracy_diagonal']['world']} they change by "
                      f"{ {a: round(rec[a]['mean'], 4) for a in ARMS} } at "
                      f"{ {a: round(rec[a]['sigma'], 2) for a in ARMS} } sigma, with {len(up)} of three arms over "
                      f"the bar and {len(thin)} within 0.05 of chance",
          "verdict": f"MET -- the label comes back when the head reads the model, on **{len(up)}** of three arms "
                     f"({up})" if (len(up) >= 2 and not thin) else
                     f"FALSIFIER FIRED -- {len(up)} of three arms over the bar and two sigma ({up}), thin {thin}"}
    return [j1, j2, j3]


def report(r: dict) -> int:
    print("== the read: the world's eight against the model's own ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e492` left the read as the last candidate: eight world numbers and a linear head at a residue of")
    print("   5.7% of the state, where `e455` reads the model's own thirty-two at one trial and beats the world's")
    print(f"\n   {'arm':<10} {'model read':>11} {'world read':>11} {'change':>9} {'sigma':>7} {'model last':>11} "
          f"{'world last':>11}")
    for a in ARMS:
        c = r["recovery"][a]
        print(f"   {a:<10} {r['spans']['accuracy_diagonal']['model'][a]:>11.4f} "
              f"{r['spans']['accuracy_diagonal']['world'][a]:>11.4f} {c['mean']:>+9.4f} {c['sigma']:>7.2f} "
              f"{r['spans']['accuracy_last']['model'][a]:>11.4f} "
              f"{r['spans']['accuracy_last']['world'][a]:>11.4f}")
    share = {int(k): v for k, v in r["share"].items()}
    print(f"\n   the label's share of the read: at {EPISODE} trials the world's {share[EPISODE]['world8']['share']:.4f} "
          f"against the model's {share[EPISODE]['model32']['share']:.4f} (spreads "
          f"{share[EPISODE]['world8']['across']:.4f} and {share[EPISODE]['model32']['across']:.4f}); at one trial "
          f"{share[1]['world8']['share']:.4f} and {share[1]['model32']['share']:.4f}")
    if r.get("one_trial"):
        print(f"   the corpus's own one-trial run at the model's own read: "
              f"{r['one_trial']['accuracy_diagonal']}")
    print(f"   the config: {len(r['spans']['config']['model']['differ'])} differing past the inert rule; the draw: "
          f"differing {r['spans']['draw']['model']['differ']}")
    print("\n== the registered claims, JB1-JB3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e492` named the read and the corpus's own `e455` reads the model at one trial; this is the read)")
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
