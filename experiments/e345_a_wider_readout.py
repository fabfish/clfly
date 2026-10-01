"""E345 -- a wider read-out: the axis `e343` named as not its own, tested for a decoder that can see.

`e343` fitted a linear decoder on the corpus's **32-neuron** read-out, read it through the other loop, and lost
**one decision in ninety-six** while the state moved by **117% of the peak** -- and its own "what it cannot do"
named what that leaves open: *"One task, one read-out draw and one circuit: ... the question 'would a wider or
narrower read-out see it' is `e286`'s axis and not this unit's."* `e286` and `e292` both point at the read-out width
as the variable that moves the corpus's numbers, so the escape hatch this unit closes is concrete: **the nil could
be a property of a 32-dimensional decoder rather than of the substrate.**

Nothing trains. One world is built **once** with its widest draw excluded from the environment's populations, the
frozen connectome network is rolled on one task's examples under both loops, and **four nested decoders** are fitted
and read at each width: the narrowest 8 of that draw, then 32, 128 and 512 -- each set containing the last, so the
only thing that changes across the rows is how many of the decoder's own inputs it gets. Because the roll does not
depend on the width, the closed and open trajectories are literally the same arrays at every row.

Four claims, registered before any of it was read.

- **T1 -- one configuration across the widths.** Same circuit, one world drawn once with the widest set excluded,
  the same 768 train and 384 test examples, the same cue templates, tau and strength, and the decoder's inputs
  **nested**: each width's set is a prefix of the widest draw. **Falsifier**: any of those differing, or a width
  whose set is not contained in the next one's.
- **T2 -- and the channel is on the decoder's own inputs.** At the widest width the closed-versus-open divergence on
  those very neurons is at least **10%** of the peak. **Falsifier**: below **2%**, which would say the widest probe
  is being asked about a channel that never reached its inputs. This is `e342`'s T4 and `e343`'s T2 on a wider set.
- **T3 -- and no width sees it.** At every width the worst cross-loop gap -- the largest distance between a decoder
  fitted in one loop and read in the other and the accuracy it had in its own -- is within **0.05**. **Falsifier**:
  a gap of **0.10** or more at any width, which is the read-out that can see the divergence and would make `e343`'s
  nil a width artefact. **Null**: between.
- **T4 -- and the gap does not grow with the width, by 0.05.** The worst gap at 512 exceeds the worst gap at 8 by at
  most **0.05**. **Falsifier**: a growth of **0.10** or more, which would say the channel becomes visible once the
  decoder is wide enough. **Null**: between.

**What it cannot do.** *The probe is linear*: this is the weakest decoder the task admits, and the widths are the
only thing that changes about it, so the result is about the width of a **linear** read-out and not about what a
non-linear one could see. *Width and capacity move together*: a 512-input probe has 2048 parameters against 768
training examples, so the within-loop accuracies are printed beside every gap -- if a wide probe merely overfits,
its own-loop accuracy falls and the gap is a capacity reading, which is why T3 and T4 are read against the
within-loop numbers and not against chance. *One task, one draw, one circuit and one strength*: `scale = 1.0`,
`leak = 0.35`, four symbols, and the nested draw is a single sample of the ladder the corpus has measured at 0, 32,
128, 300 and 700 through other instruments. *A frozen body*: nothing trains here, so this cannot say a trained
decoder at 512 inputs behaves the same, and `e343`'s own scope note applies unchanged. *And the divergence is still
a maximum over neurons and the last step*, which is not a norm and not a projection.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: the four nested widths, narrowest first; the widest is the draw, the others are its prefixes
WIDTHS = (8, 32, 128, 512)
SIZE = 300
SEED = 0
TAU = 12
#: four symbols rather than `e343`'s two: a linear probe on a two-symbol task is at 0.9479 on 32 neurons, and a
#: ceiling would make a width comparison vacuous
N_SYMBOLS = 4
#: enough examples that the widest probe, which has `4 x 512` parameters, is not being asked to interpolate
N_TRAIN = 768
N_TEST = 384
SCALE = 1.0
NOISE = 1.0
WORLD_MODES = 2
WORLD_LEAK = 0.35
#: T2's two bars, T3's window and its falsifier, and T4's
DIVERGED = 0.10
FLAT = 0.02
IN_WINDOW = 0.05
SEES_IT = 0.10
GROWS = 0.10
CLAIMS = (
    ("T1", "one configuration across the widths",
     "Same circuit, one world drawn once with the widest set excluded, the same examples, cue templates, tau and "
     "strength, and the decoder's inputs nested",
     "falsifier: any of those differing, or a width whose set is not contained in the next one's"),
    ("T2", f"and the channel is on the decoder's own inputs, by {DIVERGED:.0%} of the peak",
     f"At the widest width the closed-versus-open divergence on the decoder's own neurons is at least {DIVERGED:.0%} "
     f"of the peak",
     f"falsifier: below {FLAT:.0%}"),
    ("T3", f"and no width sees it, within {IN_WINDOW:.2f}",
     f"At every width the worst cross-loop gap is within {IN_WINDOW:.2f}",
     f"falsifier: a gap of {SEES_IT:.2f} or more at any width"),
    ("T4", f"and the gap does not grow with the width, by {GROWS:.2f}",
     f"The worst gap at {WIDTHS[-1]} exceeds the worst gap at {WIDTHS[0]} by at most {GROWS:.2f}",
     f"falsifier: a growth of {GROWS:.2f} or more"),
)


def one_width(closed_tr, closed_te, open_tr, open_te, y_tr, y_te, neurons, peak: float) -> dict:
    """One width's four decoders and the divergence on its own neurons, on the shared roll."""
    last_tr = closed_tr[:, -1, :][:, neurons]
    last_te = closed_te[:, -1, :][:, neurons]
    open_last_tr = open_tr[:, -1, :][:, neurons]
    open_last_te = open_te[:, -1, :][:, neurons]
    out = {
        "width": int(len(neurons)),
        #: the divergence **on the decoder's own inputs**, as a maximum over them and a mean, both at the last step
        "divergence_of_peak": float(max(np.max(np.abs(last_tr - open_last_tr)),
                                        np.max(np.abs(last_te - open_last_te)))) / peak,
        "mean_divergence_of_peak": float(max(np.mean(np.abs(last_tr - open_last_tr)),
                                             np.mean(np.abs(last_te - open_last_te)))) / peak,
        "within": {
            "closed": probe(closed_tr, y_tr, closed_te, y_te, neurons),
            "open": probe(open_tr, y_tr, open_te, y_te, neurons),
        },
        #: **the cross-loop decoders**: fit inside one loop, read inside the other
        "across": {
            "fit_closed_read_open": probe(closed_tr, y_tr, open_te, y_te, neurons),
            "fit_open_read_closed": probe(open_tr, y_tr, closed_te, y_te, neurons),
        },
    }
    out["gaps"] = {
        "fit_closed_read_open": abs(out["across"]["fit_closed_read_open"][-1] - out["within"]["closed"][-1]),
        "fit_open_read_closed": abs(out["across"]["fit_open_read_closed"][-1] - out["within"]["open"][-1]),
    }
    out["worst_gap"] = max(out["gaps"].values())
    return out


def reading(widths=WIDTHS, size: int = SIZE, seed: int = SEED) -> dict:
    """One world, one roll, and a nested decoder at each width."""
    import torch
    from clfly.connectome import annotate, circuits, graph
    from clfly.network import env as fly_env
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    #: the draw is the **widest** set; every narrower decoder is a prefix of it, so the sets are nested and the
    #: environment -- which excludes the read-out from its populations -- excludes all of them at once
    draw = np.sort(np.random.default_rng(seed).choice(circ.n_neurons, size=max(widths), replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    e = fly_env.build(circ, readout_subset=draw, seed=seed, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=1.0,
                      noise=NOISE, world_modes=WORLD_MODES, world_leak=WORLD_LEAK)
    rng = np.random.default_rng(seed + 7)
    y_tr = rng.integers(0, e.n_symbols, size=N_TRAIN)
    y_te = rng.integers(0, e.n_symbols, size=N_TEST)
    u_tr, u_te = e.cue_input(y_tr), e.cue_input(y_te)
    fn = e.feedback()

    def roll(u, feedback=None):
        with torch.no_grad():
            return net(torch.from_numpy(np.asarray(u, dtype=np.float32)), **(
                {"feedback": feedback} if feedback is not None else {})).numpy()

    closed_tr, closed_te = roll(u_tr, fn), roll(u_te, fn)
    open_tr, open_te = roll(u_tr), roll(u_te)
    peak = float(np.max(np.abs(open_tr))) or 1.0
    #: how much of the state the channel touches, neuron by neuron, as a maximum over the two splits at the last
    #: step. The maximum over the decoder's own neurons is what T2 uses; this says how many neurons carry it, which
    #: is the difference between "the read-out's inputs move" and "one of them moves".
    move = np.maximum(np.abs(closed_tr[:, -1, :] - open_tr[:, -1, :]).max(axis=0),
                      np.abs(closed_te[:, -1, :] - open_te[:, -1, :]).max(axis=0))
    rows = [one_width(closed_tr, closed_te, open_tr, open_te, y_tr, y_te, draw[:w], peak) for w in widths]
    return {
        "circuit": circ.name, "size": circ.n_neurons, "seed": seed, "tau": TAU, "peak": peak,
        "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS,
        "n_train": N_TRAIN, "n_test": N_TEST, "scale": SCALE, "noise": NOISE,
        "world_modes": WORLD_MODES, "world_leak": WORLD_LEAK,
        "draw_size": int(len(draw)), "draw_sha1": None,
        #: the nesting T1 asserts, recorded as the fraction of the widest set each width is
        "nested": [[int(w), float(len(draw[:w]) / len(draw))] for w in widths],
        "widths": [int(w) for w in widths],
        "readouts": rows,
        #: how many neurons of the circuit, and of the draw, move by at least a fraction of the peak at the last step
        "concentration": {
            "circuit_neurons": int(circ.n_neurons),
            "n_at_least": {f"{f:.0%}": int((move >= f * peak).sum()) for f in (0.01, 0.10, 0.50)},
            "on_the_draw": {f"{f:.0%}": int((move[draw] >= f * peak).sum()) for f in (0.01, 0.10, 0.50)},
            "draw_size": int(len(draw)),
        },
        #: the divergence on the **whole** last-step state, which does not depend on the decoder at all
        "divergence_of_peak": float(max(np.max(np.abs(closed_tr[:, -1, :] - open_tr[:, -1, :])),
                                        np.max(np.abs(closed_te[:, -1, :] - open_te[:, -1, :])))) / peak,
        "worst_gap": max(r["worst_gap"] for r in rows),
        "gap_at_narrowest": rows[0]["worst_gap"],
        "gap_at_widest": rows[-1]["worst_gap"],
        "worst_gap_growth": rows[-1]["worst_gap"] - rows[0]["worst_gap"],
    }


def judge(r: dict) -> list[dict]:
    rows = r.get("readouts") or []
    if len(rows) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the widths were not measured"} for c in CLAIMS]

    #: T1: the sets have to be nested, which is the one structural thing a prefix draw gives for free and a
    #: re-draw would silently break
    nested = all(rows[i]["width"] < rows[i + 1]["width"] for i in range(len(rows) - 1))
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), one world at scale {r['scale']} "
                                  f"with leak {r['world_leak']} and {r['world_modes']} modes, {r['n_symbols']} "
                                  f"symbols, {r['n_train']} train and {r['n_test']} test examples, widths "
                                  f"{r['widths']} as prefixes of one {r['draw_size']}-neuron draw "
                                  f"(nested {nested})",
          "verdict": "MET -- one configuration across the widths" if nested else
          f"FALSIFIER FIRED -- the widths are not nested: {r['widths']}"}

    wide = rows[-1]
    j2 = {"id": "T2", "measured": f"on the widest decoder's own {wide['width']} neurons the closed and open "
                                  f"trajectories differ by {wide['divergence_of_peak']:.2%} of the peak at the "
                                  f"last step ({wide['mean_divergence_of_peak']:.2%} on average over them), "
                                  f"against {r['divergence_of_peak']:.2%} for the whole state",
          "verdict": f"MET -- the channel is on the decoder's own inputs, by {wide['divergence_of_peak']:.2%}" if
          wide["divergence_of_peak"] >= DIVERGED else
          f"FALSIFIER FIRED -- only {wide['divergence_of_peak']:.4f}" if
          wide["divergence_of_peak"] < FLAT else
          f"NULL -- {wide['divergence_of_peak']:.4f}, between {FLAT:.2f} and {DIVERGED:.2f}"}

    detail = "; ".join(f"{row['width']}: within {row['within']['closed'][-1]:.3f}/{row['within']['open'][-1]:.3f}, "
                       f"across {row['across']['fit_closed_read_open'][-1]:.3f}/"
                       f"{row['across']['fit_open_read_closed'][-1]:.3f}, gap {row['worst_gap']:.4f}"
                       for row in rows)
    j3 = {"id": "T3", "measured": f"the last-step probe accuracy per width (within closed / within open, then the "
                                  f"two cross-loop decoders): {detail}",
          "verdict": f"MET -- the worst cross-loop gap is {r['worst_gap']:.4f} at every width" if
          r["worst_gap"] < IN_WINDOW else
          f"FALSIFIER FIRED -- a wider read-out sees the divergence, gap {r['worst_gap']:.4f}" if
          r["worst_gap"] >= SEES_IT - 1e-9 else
          f"NULL -- worst gap {r['worst_gap']:.4f}, between {IN_WINDOW:.2f} and {SEES_IT:.2f}"}

    growth = r["worst_gap_growth"]
    j4 = {"id": "T4", "measured": f"the worst gap is {r['gap_at_narrowest']:.4f} at width {r['widths'][0]} and "
                                  f"{r['gap_at_widest']:.4f} at {r['widths'][-1]}, a growth of {growth:+.4f}",
          "verdict": f"MET -- the gap does not grow, differing by {growth:+.4f}" if growth < IN_WINDOW else
          f"FALSIFIER FIRED -- it grows by {growth:.4f} as the decoder widens" if growth >= GROWS else
          f"NULL -- {growth:+.4f}, between {IN_WINDOW:.2f} and {GROWS:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("readouts"):
        print("== a wider read-out ==\n   REFUSED -- the widths were not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== a wider read-out ==")
    print(f"   {r['circuit']} ({r['size']} neurons), seed {r['seed']}, {r['n_symbols']} symbols at a chance of "
          f"{r['chance']:.2f}, {r['n_train']}/{r['n_test']} examples, one world at scale {r['scale']}, "
          f"leak {r['world_leak']}, {r['world_modes']} modes")
    print(f"   the whole last-step state diverges by {r['divergence_of_peak']:.2%} of the peak; the decoder's own "
          f"inputs, by width:")
    c = r.get("concentration") or {}
    if c:
        print(f"   the channel moves {c['n_at_least']} of the circuit's {c['circuit_neurons']} neurons by at least "
              f"1% / 10% / 50% of the peak, and {c['on_the_draw']} of the draw's {c['draw_size']}")
    print(f"\n   {'width':>6} {'divergence':>11} {'mean':>8} {'within c/o':>12} {'across c/o':>12} {'worst gap':>10}")
    for row in r["readouts"]:
        print(f"   {row['width']:6d} {row['divergence_of_peak']:11.2%} {row['mean_divergence_of_peak']:8.2%} "
              f"{row['within']['closed'][-1]:6.3f}/{row['within']['open'][-1]:.3f} "
              f"{row['across']['fit_closed_read_open'][-1]:6.3f}/{row['across']['fit_open_read_closed'][-1]:.3f} "
              f"{row['worst_gap']:10.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e343` lost one decision in 96 on a 32-neuron decoder while 117% of the peak moved; this asks")
    print("    whether a decoder with 512 of the same draw's neurons sees it, on the same roll)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--widths", default=",".join(str(w) for w in WIDTHS),
                    help="read-out widths to measure, comma separated, narrowest first")
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(widths=tuple(int(x) for x in args.widths.split(",")), size=args.size, seed=args.seed)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
