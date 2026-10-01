"""E342 -- the channel rewrites the state and not the answer, at every strength.

`e341` closed the loop's retention question on the clean stream: over **forty** replicates the world's channel moved
`replay`'s forgetting by **-0.0013 at 0.14 sigma**, where the design had the power to see `e333`'s 0.0375 at 4.0.
And `e338` had already shown the sharper form of the same thing: on **one trained body**, read once through the loop
and once with it unwired, the difference is **0.0000** on a sem of 0.0022 -- and three of its five replicates are
exactly zero, the other two differing by one held-out decision in 144.

**Both of those are at one channel strength.** `e325` measured the channel's effect on the **state** at scale 1.0 and
found it large -- closed and open trajectories diverging by 52% of the peak, and 12.48% of it on the decoder's own
32 neurons. So there is a dissociation on the record at one point: the channel rewrites the state and leaves the
answer alone. **This unit asks whether the dissociation holds across strengths**, which is what separates "the
channel does nothing" from "the channel does a great deal that the read-out cannot see".

Four runs of the **paired** design -- `e338`'s reading on a fixed body -- at feedback strength `scale` = **0.5, 1.0,
2.0 and 4.0**, with the same seeds, the same read-out draw, the same three populations and the same world, and a
**frozen** control measured on the environment itself: the closed-versus-open trajectory divergence at each strength.

Four claims, registered before these runs' readings.

- **T1 -- four strengths, one configuration.** Same circuit, read-out fingerprint, task names, replicate count, cue
  symbols, cue noise, world and seeds, the four runs differing only in `loop_scale`. **Falsifier**: any other field
  differing.
- **T2 -- and the answer does not move at any of them.** Every strength's paired difference, averaged over the three
  tasks within a replicate and then over replicates, is **within 2 sigma of zero**. **Falsifier**: one strength
  resolved away from zero. This is `e338`'s nil asked four times instead of once.
- **T3 -- and it does not grow with the strength.** The paired magnitude at `scale = 4.0` is within **0.02** of the
  magnitude at `scale = 0.5`. **Falsifier**: a growth of **0.05** or more, which would say the channel does reach the
  answer once it is strong enough and `e341`'s nil is a weak-channel result. **Null**: between.
- **T4 -- and the state does move, more with the strength.** The **frozen** closed-versus-open divergence at
  `scale = 4.0` exceeds the one at `scale = 0.5` by at least **10%** of the peak state. **Falsifier**: below **2%**,
  which would say the strength barely reaches the dynamics either and the dissociation is not there to explain.
  **Null**: between.

**What it cannot do.** *Four strengths and one world*: only `leak = 0.35` is used, and `scale` is a scalar multiplier
on one feedback pattern rather than a family of channels. *The frozen control is the connectome initialisation*, so
its divergence is the substrate's response to the channel and not a trained model's. *The paired reading is
accuracy*, while the quantity `e333` measured was `mean_forgetting` -- a body that lost task 0 would show it, and the
decomposition into a learning term and a retention term is not computed. *Three tasks and five replicates*: fifteen
paired numbers that are not independent, three tasks sharing a body and a head. *And these runs' bodies were trained
at each strength*, so the cross-strength comparison is between four sets of models and not between four readings of
one: what is paired is the channel **within** a replicate, and what is compared **across** strengths is not.
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

RUNS = Path("runs")
#: the four strengths, in the order the claims are stated over
#: the tags are the launch arithmetic (`tr -d "."` on the scale), so the names identify the runs that wrote them
SCALES = (("05", 0.5), ("10", 1.0), ("20", 2.0), ("40", 4.0))
PATHS = {tag: RUNS / f"e342_paired_scale_{tag}.json" for tag, _ in SCALES}
ARM = "replay"
SIGMA = 2.0
SAME = 0.02
GREW = 0.05
DIVERGED = 0.10
FLAT = 0.02
#: the frozen control's settings: the corpus's circuit and read-out draw, and the two strengths it compares
FROZEN = {"size": 300, "readout_size": 32, "seed": 0, "weak": 0.5, "strong": 4.0}
CLAIMS = (
    ("T1", "four strengths, one configuration",
     "Same circuit, read-out fingerprint, task names, replicate count, cue symbols, cue noise, world and seeds, the "
     "four runs differing only in `loop_scale`",
     "falsifier: any other field differing"),
    ("T2", f"and the answer does not move at any of them, within {SIGMA:.0f} sigma of zero",
     "Every strength's paired difference is within 2 sigma of zero",
     "falsifier: one strength resolved away from zero"),
    ("T3", f"and it does not grow with the strength, within {SAME:.2f}",
     f"The paired magnitude at {SCALES[-1][1]} is within {SAME:.2f} of the magnitude at {SCALES[0][1]}",
     f"falsifier: a growth of {GREW:.2f} or more"),
    ("T4", f"and the state does move, more with the strength, by {DIVERGED:.0%} of the peak",
     f"The frozen closed-versus-open divergence at {FROZEN['strong']} exceeds the one at {FROZEN['weak']} by at "
     f"least {DIVERGED:.0%} of the peak state",
     f"falsifier: below {FLAT:.0%}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(run: dict | None, arm: str = ARM) -> list[dict]:
    if not run:
        return []
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def run_reading(run: dict | None, tag: str) -> dict:
    if not run:
        return {"tag": tag, "ok": False}
    reps = replicates(run)
    rows = []
    for r in reps:
        entries = r.get("paired_channel")
        if not isinstance(entries, list) or not entries:
            return {"tag": tag, "ok": False, "why": "no paired record"}
        deltas = [e["with_loop"] - e["without_loop"] for e in entries]
        rows.append({"tasks": [e.get("task") for e in entries], "deltas": deltas,
                     "mean": statistics.fmean(deltas),
                     "with_loop": [e["with_loop"] for e in entries],
                     "without_loop": [e["without_loop"] for e in entries]})
    ca = run.get("config", {})
    ea = run.get("env_draw") or {}
    return {
        "tag": tag, "ok": True,
        "scale": ca.get("loop_scale"),
        "circuit": run.get("circuit"),
        "readout": run.get("readout", {}).get("subset_sha1"),
        "task_names": [t.get("name") for t in run.get("tasks", [])],
        "n": len(rows),
        "seed0": ca.get("seed0"),
        "readout_seed": ca.get("readout_seed"),
        "loop_seed": ca.get("loop_seed"),
        "leak": ea.get("world_leak"),
        "world_modes": ea.get("world_modes"),
        "populations": {k: ea.get(k) for k in ("cue_sha1", "action_sha1", "feedback_sha1")},
        "settings": {k: ca.get(k) for k in ("circuit_size", "repeats", "train", "test", "readout_size",
                                            "loop_noise", "loop_symbols", "loop_world_modes")},
        "rows": rows,
        "mean": paired([r["mean"] for r in rows], [0.0] * len(rows)),
        "spread": (statistics.stdev([d for r in rows for d in r["deltas"]])
                   if sum(len(r["deltas"]) for r in rows) > 1 else None),
    }


def frozen_divergence(size: int = FROZEN["size"], readout_size: int = FROZEN["readout_size"],
                      seed: int = FROZEN["seed"], scales=(FROZEN["weak"], FROZEN["strong"])) -> dict:
    """The closed-versus-open divergence of the frozen network's trajectory, at each strength.

    `e325`'s measurement, repeated here as the positive control: the channel is added to every step's input, so a
    trajectory that does not move under it would mean the strength never reached the dynamics.
    """
    from clfly.connectome import annotate, circuits, graph
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(seed).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=12)).torch_model()
    import torch
    out = {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "scales": {}}
    for scale in scales:
        e = fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=24, tau=12, world_modes=2,
                          world_leak=0.35, scale=float(scale))
        y = np.random.default_rng(seed + 7).integers(0, e.n_symbols, size=32)
        u = e.cue_input(y)
        fn = e.feedback()
        with torch.no_grad():
            open_ = net(torch.from_numpy(u.astype(np.float32))).numpy()
            closed = net(torch.from_numpy(u.astype(np.float32)), feedback=fn).numpy()
        peak = float(np.max(np.abs(open_))) or 1.0
        out["scales"][f"{scale:g}"] = {
            "peak": peak,
            "divergence": float(np.max(np.abs(closed - open_))),
            "divergence_of_peak": float(np.max(np.abs(closed - open_))) / peak,
            "readout_divergence_of_peak": float(np.max(np.abs(closed[:, -1, :][:, rs]
                                                           - open_[:, -1, :][:, rs]))) / peak,
        }
    weak, strong = out["scales"][f"{FROZEN['weak']:g}"], out["scales"][f"{FROZEN['strong']:g}"]
    out["rise"] = strong["divergence_of_peak"] - weak["divergence_of_peak"]
    out["rise_on_the_readout"] = strong["readout_divergence_of_peak"] - weak["readout_divergence_of_peak"]
    return out


def reading(paths=None, frozen=True) -> dict:
    paths = paths or PATHS
    #: a strength whose path is not given is read as absent rather than raising, so a caller can hand in a partial
    #: set and have the claims REFUSE
    out = {"strengths": [run_reading(load(paths[tag]), tag) if tag in paths else {"tag": tag, "ok": False}
                         for tag, _ in SCALES],
           "scales": [s for _, s in SCALES], "arm": ARM}
    out["runs"] = sum(2 for s in out["strengths"] if s.get("ok"))
    out["missing"] = [s["tag"] for s in out["strengths"] if not s.get("ok")]
    out["frozen"] = frozen_divergence() if frozen else None
    return out


def judge(r: dict) -> list[dict]:
    strengths = r.get("strengths") or []
    good = [s for s in strengths if s.get("ok")]
    if len(good) < len(SCALES):
        return [{"id": c[0], "measured": f"present {[s['tag'] for s in good]}",
                 "verdict": "REFUSED -- the four strengths are not all on disk"} for c in CLAIMS]

    first = good[0]
    fields = ("circuit", "readout", "task_names", "n", "seed0", "readout_seed", "loop_seed", "leak", "world_modes")
    agree = all(all(s[k] == first[k] for k in fields) for s in good)
    settings_agree = all(all(s["settings"][k] == first["settings"][k] for k in first["settings"]) for s in good)
    scales = [s["scale"] for s in good]
    j1 = {"id": "T1", "measured": f"scales {scales}, circuit {first['circuit']}, read-out {first['readout']}, tasks "
                                  f"{first['task_names']}, {first['n']} replicates each, seeds "
                                  f"{[first['seed0'], first['readout_seed'], first['loop_seed']]}, leak "
                                  f"{first['leak']}, world modes {first['world_modes']}, populations "
                                  f"{first['populations']}, settings {first['settings']}",
          "verdict": "MET -- four strengths of one configuration" if agree and settings_agree
          and len(set(scales)) == len(SCALES) else
          f"FALSIFIER FIRED -- fields agree {agree}, settings agree {settings_agree}, scales {scales}"}

    resolved = [s["tag"] for s in good if (s["mean"]["sigma"] or 0) >= SIGMA]
    detail = "; ".join(f"{s['scale']}: {s['mean']['delta']:+.4f} ({s['mean']['sigma']:.2f} sigma)" for s in good)
    j2 = {"id": "T2", "measured": f"the paired difference at each strength (averaged over the three tasks within a "
                                  f"replicate): {detail}",
          "verdict": "MET -- every strength's paired difference is within 2 sigma of zero" if not resolved else
                     f"FALSIFIER FIRED -- resolved at {resolved}"}

    weak_mag, strong_mag = abs(good[0]["mean"]["delta"]), abs(good[-1]["mean"]["delta"])
    growth = strong_mag - weak_mag
    j3 = {"id": "T3", "measured": f"the paired magnitude is {weak_mag:.4f} at {good[0]['scale']} and {strong_mag:.4f} "
                                  f"at {good[-1]['scale']}, a growth of {growth:+.4f}",
          "verdict": f"MET -- the magnitude does not grow, differing by {growth:+.4f}" if growth < SAME else
          f"FALSIFIER FIRED -- it grows by {growth:.4f}" if growth >= GREW else
          f"NULL -- {growth:+.4f}, between {SAME:.2f} and {GREW:.2f}"}

    fz = r.get("frozen")
    if not fz:
        j4 = {"id": "T4", "measured": "the frozen control was not measured",
              "verdict": "REFUSED -- the frozen divergence is absent"}
    else:
        rise = fz["rise"]
        weak = fz["scales"][f"{FROZEN['weak']:g}"]["divergence_of_peak"]
        strong = fz["scales"][f"{FROZEN['strong']:g}"]["divergence_of_peak"]
        j4 = {"id": "T4", "measured": f"the frozen divergence of the trajectory is {weak:.4f} at "
                                      f"{FROZEN['weak']} and {strong:.4f} at {FROZEN['strong']}, a rise of {rise:+.4f}"
                                      f"; on the decoder's own neurons it rises by "
                                      f"{fz['rise_on_the_readout']:+.4f}",
              "verdict": f"MET -- the state moves {rise:.2%} further at the stronger channel" if rise >= DIVERGED
              else f"FALSIFIER FIRED -- the rise is only {rise:.4f}" if rise < FLAT else
              f"NULL -- {rise:+.4f}, between {FLAT:.2f} and {DIVERGED:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the channel across strengths ==")
    for s in r.get("strengths", []):
        if not s.get("ok"):
            print(f"   {s['tag']}: REFUSED -- {'missing' if 'why' not in s else s['why']}")
            continue
        m = s["mean"]
        print(f"   scale {s['scale']:<5} {s['n']} replicates: paired difference {m['delta']:+.4f} on a sem of "
              f"{m['sem']:.4f} ({m['sigma']:.2f} sigma), per-task deltas "
              f"{[round(d, 4) for d in s['rows'][0]['deltas']]}")
    fz = r.get("frozen")
    if fz:
        print(f"\n   frozen control on {fz['circuit']}, read-out {fz['readout']}:")
        for scale, v in fz["scales"].items():
            print(f"      scale {scale:<5} divergence {v['divergence']:.4f} ({v['divergence_of_peak']:.2%} of the "
                  f"peak), on the decoder's own neurons {v['readout_divergence_of_peak']:.2%}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e325` measured the state diverging by 52% of the peak at scale 1.0 and `e341` measured the answer")
    print("    not moving at all at forty replicates; this asks whether the dissociation holds across strengths)")
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
