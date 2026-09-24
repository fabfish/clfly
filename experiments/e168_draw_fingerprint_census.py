"""E168 -- the matched-random control is a sample, and the corpus records which sample in 7 of 38 artifacts.

Rule 10 says the matched-random partition is a **population** and one draw is one **sample** of it, which is why
`--partition-seed` exists and why `e144`'s draw 1 and draw 2 were run as separate artifacts. The fingerprint that
identifies the sample is `partition_draw.fingerprint_sha1` -- a **top-level** field, so `e103`'s signature (which
reads `config`) cannot see it, and two artifacts that differ only in their draw are the *same configuration* by
every check the corpus applies.

This unit counts the exposure and then **measures the size of the thing that is missing**, from the two pairs of
40-seed runs that were made for exactly this purpose (`--partition-seed 1` against `2`, on both families):

  * **coverage**: how many artifacts run a `*-rand` arm -- so that someone could compare them -- and how many
    record which partition they drew;
  * **the sample's own size** on both axes, paired over forty seeds, for the base family and the wiring family;
  * **the two cross-artifact contrasts in this project that use a `-rand` arm** (`e162`'s lambda step on
    `ewc-block-rand`, and the margin it reports), each against the measured between-draw spread.

The verdict is not "the claim is wrong". It is which of the two axes survives the unrecorded draw and which does
not, which is a number rather than a caution.

    python -m experiments.e168_draw_fingerprint_census
    python -m experiments.e168_draw_fingerprint_census --json-out runs/e168_draw_fingerprint_census.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import load_artifacts
from experiments.e151_pertask_contrast_audit import load_arm, paired

#: the two same-command pairs that differ only in `--partition-seed`, i.e. two samples of one population
DRAW_PAIRS = (("base (input_overlap 0.0)", "runs/e140_r32_rand_draw1.json", "runs/e140_r32_rand_draw2.json"),
              ("wiring (input_overlap 1.0)", "runs/e144_r32_overlap1_rand_draw1.json",
               "runs/e144_r32_overlap1_rand_draw2.json"))
#: the pair `e162`'s block-rand lambda step is computed from: the wiring family at 3e-3 and at 1.0
LAMBDA_PAIR = ("runs/e144_r32_overlap1_methods_40reps.json", "runs/e153_r32_overlap1_methods_40reps.json")


def fingerprint(payload: dict) -> str | None:
    """The matched-random partition this run drew, as a fingerprint, or None when it does not say."""
    draw = payload.get("partition_draw")
    return draw.get("fingerprint_sha1") if isinstance(draw, dict) else None


def rand_arms(payload: dict) -> list[str]:
    """The `*-rand` arms a run carries -- the arms whose comparability depends on the draw."""
    methods = payload.get("methods")
    return sorted(m for m in methods if "rand" in m) if isinstance(methods, dict) else []


def fingerprint_of(partition) -> str:
    """The fingerprint the runner records, from the partition object.

    Duplicated from `experiments/e8_rate_network.py`'s inline expression **deliberately and with a guard**: the
    reconstruction is checked against three *recorded* fingerprints on every `--reconstruct` run, so a divergence
    between the two copies cannot pass silently -- which is the one thing that makes a second copy acceptable
    rather than the defect this project keeps finding.
    """
    import hashlib

    return hashlib.sha1(" ".join(str(int(i)) for g in partition.groups for i in g[:8]).encode()).hexdigest()[:12]


def reconstruct_fingerprint(*, circuit_size: int = 800, basis: str = "cell_class", pool_below: int = 0,
                            pool_buckets: int = 1, seed: int = 0) -> str:
    """Rebuild the matched-random draw from the config fields that determine it, and fingerprint it.

    This is what turns an unrecorded draw into an identified one: the control is
    `random_matched(from_labels(labels, pre, post, ...), default_rng(seed))`, none of which has changed since the
    commit that introduced it (`4b5d182`, and `clfly/network/fisher.py` has not been touched since), so the draw
    an artifact used is a function of its `config` alone -- **provided the fields it did not record took their
    then-defaults**, which for the artifacts at issue is checkable field by field (`pool_buckets = 1` is both the
    shipped default and the recorded value; `seed0 = 0`; `basis = cell_class`).
    """
    import numpy as np

    from clfly.connectome import annotate, circuits, graph
    from clfly.network.fisher import SynapsePartition
    from clfly.network.model import RateConfig, build_net

    conn = graph.build()
    circ = circuits.extract(conn, annotate.load_annotations(), hops=0, max_neurons=circuit_size)
    net = build_net(circ, RateConfig(seed=seed))
    pre, post = net.synapse_endpoints()
    bio = SynapsePartition.from_labels(circ.labels[basis], pre, post, name=basis,
                                       pool_below=pool_below, pool_buckets=pool_buckets)
    return fingerprint_of(SynapsePartition.random_matched(bio, np.random.default_rng(seed)))


def exposure(artifacts: list[dict]) -> dict:
    """Who runs a `-rand` arm, who records the draw, and how the comparable pairs classify."""
    users = [a for a in artifacts if rand_arms(a["payload"])]
    named = [a for a in users if fingerprint(a["payload"]) is not None]
    classes = {"both_same": 0, "both_different": 0, "one_side_only": 0, "neither": 0}
    one_sided = []
    for a, b in itertools.combinations(users, 2):
        if not set(rand_arms(a["payload"])) & set(rand_arms(b["payload"])):
            continue
        fa, fb = fingerprint(a["payload"]), fingerprint(b["payload"])
        if fa and fb:
            classes["both_same" if fa == fb else "both_different"] += 1
        elif fa or fb:
            classes["one_side_only"] += 1
            one_sided.append({"a": a["name"], "b": b["name"], "recorded": a["name"] if fa else b["name"]})
        else:
            classes["neither"] += 1
    return {"artifacts_with_a_rand_arm": len(users), "recording_the_draw": len(named),
            "unidentifiable": len(users) - len(named),
            "pairs": classes, "one_sided_examples": one_sided[:8],
            "fingerprints": sorted({fingerprint(a["payload"]) for a in named})}


def draw_size() -> dict:
    """How far two *samples* of the matched-random population sit apart, on both axes, over forty seeds."""
    out = {}
    for tag, pa, pb in DRAW_PAIRS:
        a, b = load_arm(Path(pa), "ewc-block-rand"), load_arm(Path(pb), "ewc-block-rand")
        out[tag] = {"n": a["n"], "forgetting_a": float(a["forgetting"].mean()),
                    "forgetting_b": float(b["forgetting"].mean()),
                    "forgetting": paired(b["forgetting"], a["forgetting"]),
                    "newest_a": float(a["newest"].mean()), "newest_b": float(b["newest"].mean()),
                    "newest": paired(b["newest"], a["newest"])}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--reconstruct", action="store_true",
                    help="rebuild the three draws from their seeds and check them (loads the connectome)")
    args = ap.parse_args(argv)

    out: dict = {}
    exp = exposure(load_artifacts())
    out["exposure"] = exp
    print("== the exposure ==")
    print(f"   artifacts running a `*-rand` arm (so a reader could compare them): "
          f"{exp['artifacts_with_a_rand_arm']}")
    print(f"   of those, recording which matched-random partition they drew:      {exp['recording_the_draw']}")
    print(f"   -> UNIDENTIFIABLE: {exp['unidentifiable']} of {exp['artifacts_with_a_rand_arm']}")
    print(f"   fingerprints seen: {', '.join(exp['fingerprints'])}")
    print(f"   pairs sharing a `-rand` arm, by whether the draw can be identified: "
          f"{exp['pairs']['both_same']} same, {exp['pairs']['both_different']} different, "
          f"{exp['pairs']['one_side_only']} one side only, {exp['pairs']['neither']} neither")

    size = draw_size()
    out["draw_size"] = size
    print("\n== the missing quantity, measured: two samples of one population ==")
    print(f"   {'configuration':<26}{'n':>4}{'forgetting':>14}{'sigma':>8}{'newest task':>14}{'sigma':>8}")
    for tag, d in size.items():
        print(f"   {tag:<26}{d['n']:>4}{d['forgetting']['change']:>+14.4f}{d['forgetting']['sigma']:>8.2f}"
              f"{d['newest']['change']:>+14.4f}{d['newest']['sigma']:>8.2f}")
    worst_f = max(abs(d["forgetting"]["change"]) for d in size.values())
    worst_n = max(abs(d["newest"]["change"]) for d in size.values())
    print(f"   -> two draws of the same control differ by up to {worst_f:.4f} forgetting and {worst_n:.4f} "
          f"newest, at 40 seeds")

    print("\n== whose comparisons depend on it ==")
    pa, pb = LAMBDA_PAIR
    ea, eb = load_arm(Path(pa), "ewc-block-rand"), load_arm(Path(pb), "ewc-block-rand")
    a3, a1 = load_arm(Path(pa), "naive"), load_arm(Path(pb), "naive")
    step_f = paired(eb["forgetting"], ea["forgetting"])
    step_n = paired(eb["newest"], ea["newest"])
    marg_f = paired(a1["forgetting"] - eb["forgetting"], a3["forgetting"] - ea["forgetting"])
    marg_n = paired(a1["newest"] - eb["newest"], a3["newest"] - ea["newest"])
    arts = {a["name"]: a["payload"] for a in load_artifacts()}
    fp_a, fp_b = fingerprint(arts[Path(pa).name]), fingerprint(arts[Path(pb).name])
    out["lambda_pair"] = {"a": Path(pa).name, "b": Path(pb).name, "fingerprint_a": fp_a,
                          "fingerprint_b": fp_b, "only_one_side": (fp_a is None) != (fp_b is None),
                          "forgetting_step": step_f, "newest_step": step_n,
                          "margin_step": marg_f, "margin_step_newest": marg_n,
                          "draw_size_forgetting": worst_f, "draw_size_newest": worst_n}
    print(f"   `e162`'s pair: {Path(pa).name} records {fp_a or 'NO DRAW'}; {Path(pb).name} records "
          f"{fp_b or 'NO DRAW'}")
    print(f"      -> {'ONE SIDE ONLY from the artifacts: the two draws are not KNOWN to be one sample' if (fp_a is None) != (fp_b is None) else 'both identified'}")
    print(f"   how much an unrecorded draw COULD move those contrasts -- the bound the identification rules out:")
    print(f"   {'contrast':<34}{'step':>12}{'sigma':>8}{'draw size':>12}   vs draw")
    for label, step, draw in (("block-rand forgetting step", step_f, worst_f),
                              ("block-rand newest step", step_n, worst_n),
                              ("block-rand margin over naive, f", marg_f, worst_f),
                              ("block-rand margin over naive, n", marg_n, worst_n)):
        ratio = abs(step["change"]) / draw if draw else float("inf")
        print(f"   {label:<34}{step['change']:>+12.4f}{step['sigma']:>8.2f}{draw:>12.4f}   "
              f"{'%.1fx the draw' % ratio if abs(step['change']) > draw else 'UNDER the draw'}")
    print("   -> and the one-sidedness is recoverable rather than fatal: the pre-flag code seeds the draw with")
    print("      `args.seed0` and the flag defaults to the same value, so the reconstruction below identifies it.")

    print("\n== the unrecorded draw is reconstructible, and it reproduces ==")
    print("   the control is random_matched(from_labels(labels, pre, post, ...), default_rng(seed)), and")
    print("   `clfly/network/fisher.py` has not been touched since the commit that introduced it (4b5d182), so")
    print("   the draw an artifact used is a function of its config. `e144`, which records no draw, predates")
    print("   `--partition-seed`; the pre-flag line seeds with `args.seed0`, and the flag defaults to the same")
    print("   value -- so the two sides of e162's pair should be ONE sample, and that is checkable:")
    if args.reconstruct:
        got = {s: reconstruct_fingerprint(seed=s) for s in (0, 1, 2)}
        out["reconstructed"] = got
        for s, fp in got.items():
            print(f"      seed {s}: reconstructed {fp}   recorded among the 7: "
                  f"{'MATCH' if fp in exp['fingerprints'] else 'MISMATCH'}")
        print(f"      -> all three recorded fingerprints are reproduced from their seeds: "
              f"{set(got.values()) == set(exp['fingerprints'])}")
        print(f"      -> e144's draw: seed0 = 0, pre-flag seeding = seed0, so fingerprint "
              f"{got[0]} = e153's recorded {fp_b} -> {got[0] == fp_b}")
    else:
        print("      (pass --reconstruct to rebuild the draws; it loads the connectome)")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
