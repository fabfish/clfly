"""E343 -- a read-out that looks: the state diverges by 85% and the decoder does not notice.

`e342` measured the dissociation across an eight-fold range of feedback strength: at `scale = 4.0` the frozen
network's closed and open trajectories differ by **85.05% of the peak state** -- and **19.83%** of it on the
decoder's own 32 neurons -- while a body trained in that world reads its tasks exactly as well with the world
switched off, by **+0.0028 at 0.78 sigma**.

**`e342` measured that on accuracy, which is a decoder fitted and read inside one loop.** So it cannot say *where*
the invariance lives: in the state's divergence being orthogonal to the task, or in the read-out being insensitive
to a divergence that is not. **This unit separates the two with the cheapest instrument there is: fit the decoder
inside one loop and read it inside the other.**

That is a **cross-loop probe**, and it is exactly the "read-out that can see it" the last finding asked for. If the
85% divergence lies anywhere the task's labels are separable along, a decoder fitted closed and read open must lose
accuracy; if it reads the same, the divergence is in directions the task does not use.

Nothing trains. The frozen connectome network is rolled on one task's examples under both loops, at four strengths
(`scale = 0.5, 1.0, 2.0, 4.0`), and four linear least-squares decoders are fitted and evaluated at each: two
**within** a loop and two **across** them. Four claims, registered before any of it was read.

- **T1 -- one configuration across the four strengths.** The same circuit, the same read-out draw, the same task
  examples, the same world and the same leak, differing only in the feedback strength. **Falsifier**: any of those
  differing.
- **T2 -- and the positive control holds: the state diverges.** The closed-versus-open divergence at `scale = 4.0`
  is at least **10%** of the peak. **Falsifier**: below **2%**, which would say this instrument is measuring a
  channel that is not there. This is `e342`'s T4 restated on this unit's own roll.
- **T3 -- and a decoder fitted in one loop reads the other.** At every strength the **worst** cross-loop accuracy is
  within **0.05** of its own within-loop accuracy. **Falsifier**: a gap of **0.10** or more somewhere, which is the
  finding this unit exists to look for -- a decoder that can see the divergence. **Null**: a gap between 0.05 and
  0.10.
- **T4 -- and the gap does not grow with the strength.** The worst cross-loop gap at `scale = 4.0` exceeds the one at
  `scale = 0.5` by at most **0.05**. **Falsifier**: a growth of **0.10** or more, which would say the divergence
  does reach the labels once the channel is strong enough. **Null**: between.

**What it cannot do.** *The network is frozen*, so this is the substrate's insensitivity and not a trained model's --
`e342`'s trained bodies are the evidence for those, and this unit cannot say a trained decoder would behave the same.
*The probe is linear* and fitted by least squares with a fixed ridge, which is the weakest decoder the task admits;
a non-linear one might see a divergence this does not. *One task, one read-out draw and one circuit*: the read-out is
the corpus's 32-neuron draw, and the question "would a wider or narrower read-out see it" is `e286`'s axis and not
this unit's. *The divergence is measured as a maximum over neurons and steps*, which is not a norm and not a
projection: it says how far the farthest neuron moves and not how much of the state is engaged. *And the two loops
see the same examples*: the cross-loop decoder's test set is the same inputs under the other loop, so this is
insensitivity to the channel and not generalisation across data.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: the four strengths, the same ones `e342` ran, and the frozen settings
SCALES = (0.5, 1.0, 2.0, 4.0)
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
#: the task's alphabet: two symbols, because a frozen linear probe on the corpus's 32-neuron read-out is at
#: chance on a twenty-four-way one, and a probe at chance cannot be compared with anything
N_SYMBOLS = 2
N_TRAIN = 96
N_TEST = 96
#: T2's two bars, T3's window and its falsifier, and T4's
DIVERGED = 0.10
FLAT = 0.02
IN_WINDOW = 0.05
SEES_IT = 0.10
GROWS = 0.10
CLAIMS = (
    ("T1", "one configuration across the four strengths",
     "Same circuit, read-out draw, task examples, world and leak, differing only in the feedback strength",
     "falsifier: any of those differing"),
    ("T2", f"and the positive control holds: the state diverges, by {DIVERGED:.0%} of the peak",
     f"The closed-versus-open divergence at {SCALES[-1]} is at least {DIVERGED:.0%} of the peak",
     f"falsifier: below {FLAT:.0%}"),
    ("T3", f"and a decoder fitted in one loop reads the other, within {IN_WINDOW:.2f}",
     f"At every strength the worst cross-loop accuracy is within {IN_WINDOW:.2f} of its own within-loop accuracy",
     f"falsifier: a gap of {SEES_IT:.2f} or more, a decoder that can see the divergence"),
    ("T4", f"and the gap does not grow with the strength, by {GROWS:.2f}",
     f"The worst cross-loop gap at {SCALES[-1]} exceeds the one at {SCALES[0]} by at most {GROWS:.2f}",
     f"falsifier: a growth of {GROWS:.2f} or more"),
)


def one_strength(circ, net, rs, scale: float, seed: int = SEED) -> dict:
    """One task's examples under both loops at one strength, with the four decoders fitted and read."""
    import torch
    from clfly.network import env as fly_env

    e = fly_env.build(circ, readout_subset=rs, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, world_modes=2,
                      world_leak=0.35, scale=float(scale), noise=1.0)
    rng = np.random.default_rng(seed + 7)
    y_tr = rng.integers(0, e.n_symbols, size=N_TRAIN)
    y_te = rng.integers(0, e.n_symbols, size=N_TEST)
    u_tr, u_te = e.cue_input(y_tr), e.cue_input(y_te)
    fn = e.feedback()

    def roll(u, feedback=None):
        with torch.no_grad():
            return net(torch.from_numpy(np.asarray(u, dtype=np.float32)), **(
                {"feedback": feedback} if feedback is not None else {})).numpy()

    #: the closed roll carries the environment's channel and the open one does not; the first version of this
    #: function forgot the argument, which made the two rolls identical and every claim about their difference
    #: vacuous -- T2 fired with a divergence of exactly zero, which is what caught it
    closed_tr, closed_te = roll(u_tr, fn), roll(u_te, fn)
    open_tr, open_te = roll(u_tr), roll(u_te)
    peak = float(np.max(np.abs(open_tr))) or 1.0
    out = {
        "scale": float(scale),
        "peak": peak,
        "divergence": float(max(np.max(np.abs(closed_tr - open_tr)), np.max(np.abs(closed_te - open_te)))),
        "readout_divergence": float(max(np.max(np.abs(closed_tr[:, -1, :][:, rs] - open_tr[:, -1, :][:, rs])),
                                       np.max(np.abs(closed_te[:, -1, :][:, rs] - open_te[:, -1, :][:, rs])))),
        "within": {
            "closed": probe(closed_tr, y_tr, closed_te, y_te, rs),
            "open": probe(open_tr, y_tr, open_te, y_te, rs),
        },
        #: **the cross-loop decoders**: the one this unit exists for. Fit inside one loop, read inside the other.
        "across": {
            "fit_closed_read_open": probe(closed_tr, y_tr, open_te, y_te, rs),
            "fit_open_read_closed": probe(open_tr, y_tr, closed_te, y_te, rs),
        },
    }
    out["divergence_of_peak"] = out["divergence"] / peak
    out["readout_divergence_of_peak"] = out["readout_divergence"] / peak
    #: the worst gap between a cross-loop reading and the within-loop reading it is compared against, at the last
    #: step of the trial, which is where the label is read
    out["gaps"] = {
        "fit_closed_read_open": abs(out["across"]["fit_closed_read_open"][-1]
                                    - out["within"]["closed"][-1]),
        "fit_open_read_closed": abs(out["across"]["fit_open_read_closed"][-1]
                                    - out["within"]["open"][-1]),
    }
    out["worst_gap"] = max(out["gaps"].values())
    return out


def reading(scales=SCALES, size: int = SIZE, readout_size: int = READOUT_SIZE, seed: int = SEED) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(seed).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    rows = [one_strength(circ, net, rs, s, seed=seed) for s in scales]
    return {
        "circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)),
        "readout_sha1": None, "seed": seed, "n_train": N_TRAIN, "n_test": N_TEST, "tau": TAU,
        "strengths": rows,
        "scales": list(scales),
        "worst_gap": max(r["worst_gap"] for r in rows),
        "gap_at_weakest": rows[0]["worst_gap"],
        "gap_at_strongest": rows[-1]["worst_gap"],
        "worst_gap_growth": rows[-1]["worst_gap"] - rows[0]["worst_gap"],
    }


def judge(r: dict) -> list[dict]:
    rows = r.get("strengths") or []
    if len(rows) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the strengths were not measured"} for c in CLAIMS]

    same = all(row["peak"] == rows[0]["peak"] for row in rows)
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']}, read-out {r['readout']} neurons, {r['n_train']} train and "
                                  f"{r['n_test']} test examples at each of the strengths {r['scales']}, one world "
                                  f"with leak 0.35 and world modes 2, the peak state equal across them {same}",
          "verdict": "MET -- one configuration across the four strengths" if same and len(rows) == len(r["scales"])
          else f"FALSIFIER FIRED -- the peak state differs across the strengths: "
               f"{[round(row['peak'], 6) for row in rows]}"}

    strong = rows[-1]
    j2 = {"id": "T2", "measured": f"at scale {strong['scale']} the trajectories differ by {strong['divergence']:.4f}, "
                                  f"i.e. {strong['divergence_of_peak']:.2%} of the peak ({strong['peak']:.4f}), and "
                                  f"on the decoder's own neurons by {strong['readout_divergence_of_peak']:.2%}",
          "verdict": f"MET -- the state diverges by {strong['divergence_of_peak']:.2%} at the strongest channel" if
          strong["divergence_of_peak"] >= DIVERGED else
          f"FALSIFIER FIRED -- only {strong['divergence_of_peak']:.4f}" if strong["divergence_of_peak"] < FLAT else
          f"NULL -- {strong['divergence_of_peak']:.4f}, between {FLAT:.2f} and {DIVERGED:.2f}"}

    detail = "; ".join(f"{row['scale']}: within {row['within']['closed'][-1]:.3f}/{row['within']['open'][-1]:.3f}, "
                       f"across {row['across']['fit_closed_read_open'][-1]:.3f}/"
                       f"{row['across']['fit_open_read_closed'][-1]:.3f}, worst gap {row['worst_gap']:.4f}"
                       for row in rows)
    j3 = {"id": "T3", "measured": f"the last-step probe accuracy per strength (within closed/within open, then the "
                                  f"two cross-loop decoders): {detail}",
          "verdict": f"MET -- the worst cross-loop gap is {r['worst_gap']:.4f} at every strength" if
          r["worst_gap"] < IN_WINDOW else
          f"FALSIFIER FIRED -- a decoder sees the divergence, gap {r['worst_gap']:.4f}" if
          r["worst_gap"] >= SEES_IT - 1e-9 else
          f"NULL -- worst gap {r['worst_gap']:.4f}, between {IN_WINDOW:.2f} and {SEES_IT:.2f}"}

    growth = r["worst_gap_growth"]
    j4 = {"id": "T4", "measured": f"the worst gap is {r['gap_at_weakest']:.4f} at scale {r['scales'][0]} and "
                                  f"{r['gap_at_strongest']:.4f} at {r['scales'][-1]}, a growth of {growth:+.4f}",
          "verdict": f"MET -- the gap does not grow, differing by {growth:+.4f}" if growth < GROWS else
          f"FALSIFIER FIRED -- it grows by {growth:.4f}" if growth >= GROWS else
          f"NULL -- {growth:+.4f}, between {IN_WINDOW:.2f} and {GROWS:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("strengths"):
        print("== a read-out that looks ==\n   REFUSED -- the strengths were not measured")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== a read-out that looks ==")
    print(f"   {r['circuit']} ({r['size']} neurons), read-out {r['readout']} neurons, seed {r['seed']}, "
          f"{r['n_train']}/{r['n_test']} examples, tau {r['tau']}")
    print(f"\n   {'scale':>6} {'divergence':>11} {'of peak':>8} {'on readout':>11} {'within c/o':>12} "
          f"{'across c/o':>12} {'worst gap':>10}")
    for row in r["strengths"]:
        print(f"   {row['scale']:6.1f} {row['divergence']:11.4f} {row['divergence_of_peak']:8.2%} "
              f"{row['readout_divergence_of_peak']:11.2%} "
              f"{row['within']['closed'][-1]:6.3f}/{row['within']['open'][-1]:.3f} "
              f"{row['across']['fit_closed_read_open'][-1]:6.3f}/{row['across']['fit_open_read_closed'][-1]:.3f} "
              f"{row['worst_gap']:10.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e342` found the state diverging by 85% of the peak while a trained body's answer does not move,")
    print("    on accuracy -- a decoder fitted and read inside one loop; this fits it in one loop and reads the other)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", default="300", help="circuit sizes to measure, comma separated")
    ap.add_argument("--readout-size", type=int, default=READOUT_SIZE)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(size=int(args.sizes.split(",")[0]), readout_size=args.readout_size, seed=args.seed)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
