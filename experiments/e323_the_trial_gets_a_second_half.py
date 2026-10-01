r"""E323 -- the trial gets a second half: the benchmark's first stimulus that changes with time.

`e322` measured the trial's time axis across both suite builders, both splits and two circuit sizes and found the
stimulus equal to its first step **exactly**, everywhere: 18 task instances, worst deviation zero. Its conclusion was
that a temporal task needs *either a second writer with a time index or an environment in the training loop*, and its
"what it cannot do" left the choice open. This unit takes the first option.

`make_sequence_task` in `clfly/network/tasks.py` delivers **two** sub-stimuli per trial -- one for the first
``tau // 2`` steps, one for the rest, with fresh noise at every step -- and labels the example by their **ordered
pair**. The second half's symbol is in the drive throughout the second half; the **first** half's symbol is not in
the drive any more once the boundary is crossed. So a decoder that reports the pair from the last step has to have
carried the first symbol there in the recurrent state, which is the thing a constant drive can never ask for.

Four claims, registered before the reading below was taken. The pair is four-way and the first symbol two-way, so
chance is 0.25 and 0.50, and both are measured on the **narrow read-out** -- 32 neurons drawn at the runner's own
seed -- because that is the regime in which the body is load-bearing.

- **T1 -- the builder really does write a sequence.** Every example's stimulus is constant within each half and
  **changes at the boundary**. **Falsifier**: an example whose two halves are the same vector, or a half that is not
  internally constant.
- **T2 -- the pair is readable from the last step.** The four-way probe at the last step is at least **0.15 above
  chance**. **Falsifier**: at or below 0.05 above chance. **Null**: between the two.
- **T3 -- and it is not readable before the second half arrives.** The same probe at the last step of the first half
  is at most **0.05 above chance**, since ``b`` has not been delivered yet. **Falsifier**: at or above 0.15 above
  chance, which would mean the label leaks into the first half. **Null**: between the two.
- **T4 -- and the first symbol survives the boundary.** A two-way probe of the **first** half's identity, fitted and
  read at the last step of the trial, is at least **0.15 above chance**. This is the memory claim and it is measured
  on the **frozen** network, so it says the circuit holds the symbol and not that training put it there.
  **Falsifier**: at or below 0.05 above chance, which would say the first symbol is gone and the task is a training
  problem rather than a substrate one. **Null**: between the two.

**What it cannot do.** *The frozen network is the connectome initialisation*, so `T4` is the substrate's memory and
not a trained model's. *The probe is linear and fitted per step*, so a non-linear decoder would place the ceiling
elsewhere. *Two circuit sizes, one connectome, one weight scale, one leak*: whether the memory is the circuit's or
``alpha``'s is not separated. *Nothing here trains*, so the pair being readable at the last step on the frozen
network is not the same as the task being learnable by any of the five arms -- that needs the runner, and the second
half of this design is a run. *And a single boundary at ``tau // 2``* is one sequence length and one split point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: T2's and T4's bar above chance, T3's ceiling above it, and the window that separates each from its falsifier
BAR = 0.15
CEILING = 0.05
CLAIMS = (
    ("T1", "the builder really does write a sequence",
     "Every example's stimulus is constant within each half and changes at the boundary",
     "falsifier: the two halves identical, or a half that is not internally constant"),
    ("T2", f"the pair is readable from the last step, at least {BAR:.2f} above chance",
     "The four-way probe at the last step is at least that far above chance",
     f"falsifier: at or below {CEILING:.2f} above chance"),
    ("T3", f"and it is not readable before the second half arrives, at most {CEILING:.2f} above chance",
     "The same probe at the last step of the first half is at most that far above chance",
     f"falsifier: at or above {BAR:.2f} above chance"),
    ("T4", f"and the first symbol survives the boundary, at least {BAR:.2f} above chance",
     "A two-way probe of the FIRST half's identity, read at the last step, is at least that far above chance",
     f"falsifier: at or below {CEILING:.2f} above chance"),
)


# --------------------------------------------------------------------------
def describe_sequence(task) -> dict:
    """T1's measurement: the two halves, their internal constancy, and the change at the boundary."""
    u = np.asarray(task.u_train)
    half = max(1, task.tau // 2)
    within = [float(np.max(np.abs(u[:, t] - u[:, 0]))) for t in range(half)]
    within += [float(np.max(np.abs(u[:, t] - u[:, half]))) for t in range(half, task.tau)]
    boundary = float(np.min(np.max(np.abs(u[:, half] - u[:, 0]), axis=1)))
    return {"task": task.name, "tau": task.tau, "half": half,
            "within_half_worst": max(within), "boundary_least": boundary,
            "at_boundary_max": float(np.max(np.abs(u[:, half] - u[:, half - 1])))}


def frozen_trajectories(conn_net, suite, materialise=None):
    import torch
    model = materialise or conn_net.torch_model()
    out = {}
    with torch.no_grad():
        for task in suite:
            tr = model(torch.from_numpy(np.asarray(task.u_train, dtype=np.float32))).numpy()
            te = model(torch.from_numpy(np.asarray(task.u_test, dtype=np.float32))).numpy()
            out[task.name] = (task, tr, te)
    return out


def curves(task, tr, te, neurons) -> dict:
    """The pair probe and the two single-symbol probes at every step of one task.

    The single-symbol curves are a **description taken after the four claims were registered** and they decide none
    of them: ``first`` is ``y // k`` and ``second`` is ``y % k``. They are what the third claim's falsifier turned
    out to be about -- a probe that reads only the first symbol scores 0.50 on a four-way ordered pair, so the pair
    probe's margin over 0.25 at mid-trial cannot test "the label needs the second half" and these two can.
    """
    y = np.asarray(task.y_train)
    yt = np.asarray(task.y_test)
    k = int(round(task.n_classes ** 0.5))
    mid = max(1, task.tau // 2) - 1
    pair = probe(tr, y, te, yt, neurons)
    first = probe(tr, y // k, te, yt // k, neurons)
    second = probe(tr, y % k, te, yt % k, neurons)
    return {"pair": pair, "first": first, "second": second,
            "pair_last": pair[-1], "pair_at_half": pair[mid],
            "first_last": first[-1], "second_at_half": second[mid]}


def measure(conn_net, name: str, suite, neurons_of, chance: float, half: int) -> dict:
    traj = frozen_trajectories(conn_net, suite)
    rows = {}
    for tname, (task, tr, te) in traj.items():
        rows[tname] = curves(task, tr, te, neurons_of(task))
    return {"suite": name, "half": half, "chance_pair": chance, "chance_first": 0.5, "tasks": rows}


def reading(sizes=(300, 800), n_train: int = 48, n_test: int = 24, k: int = 2,
            readout_size: int | None = 32) -> dict:
    from clfly.network import tasks as rate_tasks
    from clfly.network.model import RateConfig, build_net
    from clfly.connectome import annotate, circuits, graph

    conn, ann = graph.build(), annotate.load_annotations()
    out = {"sizes": list(sizes), "readout_size": readout_size, "k": k,
           "sequence": [], "constant": [], "configs": []}
    for size in sizes:
        circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
        subset = None
        if readout_size and readout_size < circ.n_neurons:
            subset = np.sort(np.random.default_rng(0).choice(circ.n_neurons, size=readout_size, replace=False))
        conn_net = build_net(circ, RateConfig(tau=12))
        for label, rs in (("narrow", subset), ("head", None)):
            seq = rate_tasks.make_sequence_suite(circ, k=k, n_train=n_train, n_test=n_test, readout_subset=rs)
            const = rate_tasks.make_suite(circ, n_train=n_train, n_test=n_test, readout_subset=rs)
            out["configs"].append({"circuit": circ.name, "size": circ.n_neurons, "readout": label,
                                   "n_readout": int(len(rs)) if rs is not None else None})
            out["sequence"].append({"circuit": circ.name, "size": circ.n_neurons, "readout": label,
                                    "checks": [describe_sequence(t) for t in seq],
                                    **measure(conn_net, f"seq/{label}", seq,
                                              lambda t: t.readout_neurons, 1.0 / (k * k), max(1, 12 // 2))})
            out["constant"].append({"circuit": circ.name, "size": circ.n_neurons, "readout": label,
                                    **measure(conn_net, f"assembly/{label}", const,
                                              lambda t: t.readout_neurons, 1.0 / 4, max(1, 12 // 2))})
    return out


# --------------------------------------------------------------------------
def judge(r: dict) -> list[dict]:
    seq = [x for x in r.get("sequence", []) if x.get("readout") == "narrow"] or r.get("sequence", [])
    if not seq:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the circuit was not measured"} for c in CLAIMS]

    checks = [c for x in seq for c in x["checks"]]
    worst_within = max(c["within_half_worst"] for c in checks)
    least_boundary = min(c["boundary_least"] for c in checks)
    j1 = {"id": "T1", "measured": f"{len(checks)} tasks: worst within-half deviation {worst_within:g}, least "
                                  f"boundary change over examples {least_boundary:.4f}",
          "verdict": "MET -- each half is constant and the boundary always moves" if
          worst_within == 0.0 and least_boundary > 0 else
          f"FALSIFIER FIRED -- within-half deviation {worst_within:g}, boundary {least_boundary:g}"}

    pair_rows = [(x, t, v) for x in seq for t, v in x["tasks"].items()]
    all_rows = [(x, t, v) for x in r.get("sequence", []) for t, v in x["tasks"].items()]
    head_rows = [(x, t, v) for x, t, v in all_rows if x.get("readout") == "head"]
    pair_last = [v["pair_last"] - x["chance_pair"] for x, _, v in pair_rows]
    pair_half = [v["pair_at_half"] - x["chance_pair"] for x, _, v in pair_rows]
    first_last = [v["first_last"] - x["chance_first"] for x, _, v in pair_rows]
    second_half = [v["second_at_half"] - x["chance_first"] for x, _, v in pair_rows]
    worst_last = min(pair_last)
    worst_half = max(pair_half)
    worst_first = min(first_last)

    head_note = ""
    if head_rows:
        margins = [v["pair_last"] - x["chance_pair"] for x, _, v in head_rows]
        head_note = f"; at the task head the same margins are {', '.join(f'{m:+.4f}' for m in margins)}"
    second_note = (f"; the SECOND symbol's probe at the same step is "
                   f"{max(v['second_at_half'] for _, _, v in pair_rows):.4f}, "
                   f"i.e. {max(second_half):+.4f} above chance")
    j2 = {"id": "T2", "measured": f"{len(pair_rows)} tasks at the narrow read-out; least last-step pair probe "
                                  f"{min(v['pair_last'] for _, _, v in pair_rows):.4f} against chance "
                                  f"{pair_rows[0][0]['chance_pair']:.2f}, i.e. {worst_last:+.4f}{head_note}",
          "verdict": (f"MET -- the pair is readable from the last step, least margin {worst_last:+.4f}"
                      if worst_last >= BAR else
                      f"FALSIFIER FIRED -- the last step is {worst_last:+.4f} above chance"
                      if worst_last <= CEILING else
                      f"NULL -- the least margin is {worst_last:+.4f}, between {CEILING:.2f} and {BAR:.2f}")}

    j3 = {"id": "T3", "measured": f"most first-half pair probe {max(v['pair_at_half'] for _, _, v in pair_rows):.4f} "
                                  f"against chance {pair_rows[0][0]['chance_pair']:.2f}, i.e. {worst_half:+.4f}; a "
                                  f"probe reading only the first symbol scores 0.50 on this label by construction"
                                  f"{second_note}",
          "verdict": (f"FALSIFIER FIRED -- the pair is {worst_half:+.4f} above chance before the second half"
                      if worst_half >= BAR else
                      f"MET -- at most {worst_half:+.4f} above chance, so the label needs the second half"
                      if worst_half <= CEILING else
                      f"NULL -- {worst_half:+.4f}, between {CEILING:.2f} and {BAR:.2f}")}

    j4 = {"id": "T4", "measured": f"least last-step first-symbol probe "
                                  f"{min(v['first_last'] for _, _, v in pair_rows):.4f} against chance "
                                  f"{pair_rows[0][0]['chance_first']:.2f}, i.e. {worst_first:+.4f}",
          "verdict": (f"MET -- the first symbol survives the boundary, least margin {worst_first:+.4f}"
                      if worst_first >= BAR else
                      f"FALSIFIER FIRED -- the first symbol reads {worst_first:+.4f} above chance at the last step"
                      if worst_first <= CEILING else
                      f"NULL -- the least margin is {worst_first:+.4f}, between {CEILING:.2f} and {BAR:.2f}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the trial gets a second half ==")
    for c in r.get("configs", []):
        print(f"   {c['circuit']:20} ({c['size']:5}) read-out {c['readout']:7} "
              f"({'%d neurons' % c['n_readout'] if c['n_readout'] else 'the task head'})")

    print("\n== T1, the stimulus itself ==")
    for x in r.get("sequence", []):
        for c in x["checks"]:
            print(f"   {x['readout']:7} {x['circuit']:20} {c['task']:14} tau {c['tau']} half {c['half']}  "
                  f"within-half worst {c['within_half_worst']:g}  least boundary change {c['boundary_least']:.4f}")

    for key, title in (("sequence", "T2/T3/T4, the sequence suite"),
                       ("constant", "the control: the same circuits on a sustained drive")):
        print(f"\n== {title} ==")
        print(f"   {'read-out':9} {'task':16} {'pair':>44} {'first':>44} {'second':>44}")
        for x in r.get(key, []):
            for t, v in x["tasks"].items():
                p = " ".join(f"{a:.2f}" for a in v["pair"])
                f_ = " ".join(f"{a:.2f}" for a in v["first"])
                s_ = " ".join(f"{a:.2f}" for a in v["second"])
                print(f"   {x['readout']:9} {t:16} {p:>44} {f_:>44} {s_:>44}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e322` found the trial's time axis carried nothing and named the two ways to give it one; this is")
    print("    the second writer with a step index, and the pair label is what makes the first half load-bearing)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sizes", default="300,800", help="circuit sizes to measure, comma separated")
    ap.add_argument("--train", type=int, default=48)
    ap.add_argument("--test", type=int, default=24)
    ap.add_argument("--k", type=int, default=2, help="the sequence alphabet; the class count is its square")
    ap.add_argument("--readout-size", type=int, default=32, help="the narrow read-out; 0 for the whole state")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(sizes=tuple(int(s) for s in args.sizes.split(",") if s.strip()),
                n_train=args.train, n_test=args.test, k=args.k,
                readout_size=args.readout_size or None)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
