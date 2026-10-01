"""E325 -- the loop closes: the environment's next input is the agent's own last action.

Every task in this repository is a ``u`` array written before the model runs, so the world can never see what the
agent did. `e322` measured that a sustained stimulus makes the trial's time axis carry nothing, and named two ways
to give it one: **a writer whose value changes with the step**, which `e323` built and `e324` trained the five arms
on, and **an environment in the training loop**, which is this unit.

`clfly/network/env.py` supplies the second. The model's forward pass takes an optional ``feedback`` callable whose
value is added to each step's input, and `CueActionEnv` builds the smallest world that needs one: the cue is shown
at step ``0`` and taken away, and from step ``1`` on the only thing in the input is the agent's own last action,
read off a set of its neurons and shown back at another. The trial is therefore a **delayed report of a cue that is
gone**, under feedback from the report's own machinery -- the first setting here in which the agent's output is an
input to itself.

Four claims, registered before the reading below was taken. Everything is measured on the **frozen** connectome
network, so this is the substrate's behaviour before any training; the probe is the same closed-form linear
least-squares decoder `e322` and `e323` use, at the corpus's own read-out draw of 32 neurons, and the cue is
two-way so chance is 0.50.

- **T1 -- the loop closes.** The feedback term is non-zero at some step for every example. **Falsifier**: it is
  exactly zero at every step, which would mean the agent's action never reaches its own input.
- **T2 -- and it is not decorative.** The closed and open trajectories of the same network on the same inputs
  diverge by at least **1%** of the peak state magnitude either run reaches. **Falsifier**: below **0.1%**, which
  would make the loop a rounding difference.
- **T3 -- and the cue survives it.** The last-step cue probe under the **closed** loop is at least **0.15** above
  chance. **Falsifier**: at or below 0.05. **Null**: between the two.
- **T4 -- and the loop moves the read-out itself.** The last-step divergence **restricted to the decoder's own
  neurons** is at least **1%** of the peak state. This is the claim the first registration got wrong: it was written
  on the probe's *accuracy* margin, which is bounded above by 1.0 and which the frozen connectome already reads at
  **1.00** for this cue in **both** loops, so a "moves by 0.04" claim had no room on the upside and could only fire.
  A restricted divergence is the quantity with headroom, and it asks the question the accuracy claim was about: not
  whether the loop changes the state, which T2 settles, but whether it changes **what the decoder is looking at**.
  **Falsifier**: below **0.1%** of the peak.

**What it cannot do.** *The network is frozen*, so T3 and T4 are the substrate's feedback behaviour and not a
trained model's, and nothing here says a loop can be *learned in*. *The action is smooth* -- a ``tanh`` of the mean
activity over the action neurons -- so that it can be differentiated through; a hard `sign` is a one-word change and
is not measured. *Two circuit sizes, one draw of the three populations, one scale and one gain*, and the populations
come from `env.build`'s single seed. *The probe is linear and the read-out is the corpus's own 32-neuron draw*, which
is disjoint from the environment's action neurons by construction, so the loop and the decoder are not one object but
are also not independent. *And there is no reward, no episode and no policy*: this unit supplies the environment a
game would need, and a learning rule for acting in it is a separate question.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from clfly.network import env as fly_env
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: T2's two bars and T4's, as fractions of the peak state magnitude, and T3's
DIVERGENCE = 0.01
DECORATIVE = 0.001
BAR = 0.15
CEILING = 0.05
MOVED = 0.01
STILL = 0.001
CLAIMS = (
    ("T1", "the loop closes: the agent's own last action reaches its input",
     "The feedback term is non-zero at some step for every example",
     "falsifier: it is exactly zero at every step"),
    ("T2", f"and it is not decorative: the two trajectories diverge by at least {DIVERGENCE:.0%} of the peak state",
     f"The closed and open trajectories differ by at least {DIVERGENCE:.0%} of the peak magnitude in either run",
     f"falsifier: below {DECORATIVE:.1%}"),
    ("T3", f"and the cue survives it, at least {BAR:.2f} above chance",
     "The last-step cue probe under the closed loop is at least that far above chance",
     f"falsifier: at or below {CEILING:.2f} above chance"),
    ("T4", f"and the loop moves the read-out itself, at least {MOVED:.0%} of the peak state",
     "The last-step divergence restricted to the decoder's own neurons is at least that much of the peak",
     f"falsifier: below {STILL:.1%}"),
)


def roll(model, u, fn=None) -> np.ndarray:
    """The trajectory of ``u``, with the loop closed when ``fn`` is given."""
    import torch
    with torch.no_grad():
        out = model(torch.from_numpy(np.asarray(u, dtype=np.float32)), **({"feedback": fn} if fn else {}))
    return out.numpy()


def feedback_trace(fn, traj) -> list[float]:
    """``max |feedback|`` at each step, read off the state **before** that step's update."""
    import torch
    with torch.no_grad():
        return [float(torch.max(torch.abs(fn(torch.from_numpy(np.asarray(traj[:, t], dtype=np.float32)), t + 1))))
                for t in range(traj.shape[1] - 1)]


def one_config(circ, conn_net, rs, n_train: int, n_test: int, seed: int, scale: float, gain: float) -> dict:
    """The open and closed trajectories of one environment on one circuit.

    The probe is **fitted on the train examples and read on the test ones**, for both loops, so a curve cannot be
    earned by the decoder memorising the trial it is scored on.
    """
    env = fly_env.build(circ, readout_subset=rs, seed=seed, scale=scale, gain=gain)
    rng = np.random.default_rng(seed + 7)
    y_tr = rng.integers(0, env.n_symbols, size=n_train)
    y_te = rng.integers(0, env.n_symbols, size=n_test)
    fn = env.feedback()
    u_tr, u_te = env.cue_input(y_tr), env.cue_input(y_te)
    traj = {"open": (roll(conn_net, u_tr), roll(conn_net, u_te)),
            "closed": (roll(conn_net, u_tr, fn), roll(conn_net, u_te, fn))}
    peak = float(max(np.max(np.abs(traj["open"][0])), np.max(np.abs(traj["open"][1]))))
    out = {"circuit": circ.name, "size": circ.n_neurons, "env": env.summary(), "peak_state": peak,
           "feedback_max": float(np.max(feedback_trace(fn, traj["open"][0])))}
    for loop in ("open", "closed"):
        (tr, te) = traj[loop]
        out[f"cue_probe_{loop}"] = probe(tr, y_tr, te, y_te, rs)
    out["divergence"] = float(max(np.max(np.abs(traj["closed"][i] - traj["open"][i])) for i in (0, 1)))
    out["divergence_of_peak"] = out["divergence"] / (peak or 1.0)
    if rs is not None:
        out["readout_divergence"] = float(max(
            np.max(np.abs(traj["closed"][i][:, -1, :][:, rs] - traj["open"][i][:, -1, :][:, rs]))
            for i in (0, 1)))
        out["readout_divergence_of_peak"] = out["readout_divergence"] / (peak or 1.0)
    return out


def reading(sizes=(300, 800), n_train: int = 96, n_test: int = 96, readout_size: int = 32,
            seed: int = 0, scale: float = 1.0, gain: float = 1.0) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net
    conn, ann = graph.build(), annotate.load_annotations()
    out = {"sizes": list(sizes), "n_train": n_train, "n_test": n_test, "readout_size": readout_size,
           "seed": seed, "scale": scale, "gain": gain, "configs": []}
    for size in sizes:
        circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
        rs = None
        if readout_size and readout_size < circ.n_neurons:
            rs = np.sort(np.random.default_rng(seed).choice(circ.n_neurons, size=readout_size, replace=False))
        conn_net = build_net(circ, RateConfig(tau=12))
        out["configs"].append(one_config(circ, conn_net.torch_model(), rs, n_train, n_test, seed, scale, gain))
    return out


# --------------------------------------------------------------------------
def judge(r: dict) -> list[dict]:
    rows = list(r.get("configs", []))
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the circuit was not measured"} for c in CLAIMS]

    fb = max(v["feedback_max"] for v in rows)
    j1 = {"id": "T1", "measured": f"{len(rows)} circuits; largest feedback term {fb:g}",
          "verdict": "MET -- the action reaches the agent's own input" if fb > 0 else
                     "FALSIFIER FIRED -- the feedback term is exactly zero at every step"}

    worst_div = max(v["divergence_of_peak"] for v in rows)
    detail = "; ".join(f"{v['size']} {v['divergence_of_peak']:.4f}" for v in rows)
    j2 = {"id": "T2", "measured": f"largest divergence {worst_div:.4f} of the peak state against a bar of "
                                  f"{DIVERGENCE}: {detail}",
          "verdict": f"MET -- the closed trajectory leaves the open one by {worst_div:.2%} of the peak" if
          worst_div >= DIVERGENCE else
          f"FALSIFIER FIRED -- the largest divergence is {worst_div:.4%} of the peak" if worst_div < DECORATIVE
          else f"NULL -- {worst_div:.4%}, between {DECORATIVE:.1%} and {DIVERGENCE:.0%}"}

    closed = [v["cue_probe_closed"][-1] - 0.5 for v in rows]
    least = min(closed)
    j3 = {"id": "T3", "measured": f"{len(rows)} circuits; least last-step closed-loop cue probe "
                                  f"{min(v['cue_probe_closed'][-1] for v in rows):.4f} against a 0.50 chance, "
                                  f"i.e. {least:+.4f}",
          "verdict": f"MET -- the cue is still read to {least:+.4f} above chance under the loop" if least >= BAR
          else f"FALSIFIER FIRED -- it reads {least:+.4f} above chance" if least <= CEILING
          else f"NULL -- {least:+.4f}, between {CEILING:.2f} and {BAR:.2f}"}

    moved = [(v["size"], v.get("readout_divergence_of_peak")) for v in rows]
    detail = "; ".join(f"{size} {'n/a' if m is None else f'{m:.4f}'}" for size, m in moved)
    least_move = min(m for _, m in moved if m is not None) if any(m is not None for _, m in moved) else None
    j4 = {"id": "T4", "measured": f"last-step divergence on the decoder's own neurons, as a share of the peak: "
                                  f"{detail}",
          "verdict": "REFUSED -- no read-out subset was used" if least_move is None else
          f"MET -- the loop moves the read-out by at least {least_move:.2%} of the peak" if least_move >= MOVED else
          f"FALSIFIER FIRED -- it moves by only {least_move:.4%} of the peak" if least_move < STILL else
          f"NULL -- {least_move:.4%}, between {STILL:.1%} and {MOVED:.0%}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the loop closes ==")
    for v in r.get("configs", []):
        e = v["env"]
        print(f"   {v['circuit']:20} ({v['size']:5})  cue {e['n_cue']} action {e['n_action']} "
              f"feedback {e['n_feedback']} at scale {e['scale']} gain {e['gain']}")
        print(f"      peak state {v['peak_state']:.4f}  feedback max {v['feedback_max']:.4f}  "
              f"divergence {v['divergence']:.4f} ({v['divergence_of_peak']:.2%} of the peak), on the decoder's own "
              f"neurons {v.get('readout_divergence_of_peak', float('nan')):.4f}")
        print(f"      cue probe open   {' '.join(f'{a:.2f}' for a in v['cue_probe_open'])}")
        print(f"      cue probe closed {' '.join(f'{a:.2f}' for a in v['cue_probe_closed'])}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e322` named a step-varying writer and an environment in the training loop as the two ways to give")
    print("    the trial a time axis; `e323` and `e324` took the first, and this is the second)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", default="300,800", help="circuit sizes to measure, comma separated")
    ap.add_argument("--train", type=int, default=96)
    ap.add_argument("--test", type=int, default=96)
    ap.add_argument("--readout-size", type=int, default=32)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--scale", type=float, default=1.0, help="the feedback channel's strength")
    ap.add_argument("--gain", type=float, default=1.0, help="the action's slope in the action neurons' mean")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(sizes=tuple(int(s) for s in args.sizes.split(",") if s.strip()),
                n_train=args.train, n_test=args.test, readout_size=args.readout_size,
                seed=args.seed, scale=args.scale, gain=args.gain)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
