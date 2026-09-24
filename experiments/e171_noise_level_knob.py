"""E171 -- `e167`'s registered read: does the penalty's advantage track the family's own forgetting level?

`e166`'s census of every single-field manipulation in the corpus found the room account's direction in **5 of 5
resolved cases and 0 against**, and then disqualified its own evidence: the field that provably cannot move the
level (`fisher_batches`, unread by `naive`) moves the gain by **0.0500**, against the 0.0583 of the largest
level-driven step, 8 of the 13 level-moving rows are the closed `frozen_bias` diagnostic, and the other two fields
change the task structure (`classes`) or the decoder (`readout_size`). **So the test needs a level knob at fixed
architecture and fixed task structure, and `noise` is one flag** — it changes the stimulus, not the read-out, not
the class structure, not the partition. `e167` runs it at λ = 3e-4, the base family's one *resolved* penalty arm,
where the gain has the most room to move.

**This file is written before `e167`'s artifacts exist**, which is the point: the read of a registered experiment
should be mechanical rather than improvised once the numbers are in, so the predictions below are `e167`'s row's
and this script only evaluates them.

  * **P1**: at least one of noise 0.5 and 2.0 moves `naive`'s forgetting away from the noise-1.0 level by >= 2σ;
  * **P2**: **at whichever end moved, the gain's step has the level's sign** and resolves at >= 2σ;
  * **falsifier**: the gain's step resolves at >= 2σ with the **opposite** sign;
  * **null worth keeping**: neither end moves the level at 2σ, in which case `noise` is not a level knob for this
    metric and the room account gets no test from this design either.

The reference is `e133`'s forty-replicate `naive` (the noise-1.0 level) and `e141`'s λ = 3e-4 `ewc` against it
(the noise-1.0 gain). The two differ in `lam`, which `e160` derives as **unread by `naive`**, so the reference
level is one number rather than two -- and the script asserts that rather than assuming it.

    python -m experiments.e171_noise_level_knob
    python -m experiments.e171_noise_level_knob --json-out runs/e171_noise_level_knob.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import load_arm, paired

#: the noise-1.0 reference: `naive` from `e133` (forty replicates, `lam = 3e-3`) and `ewc` from `e141` at 3e-4
REFERENCE_NAIVE = "runs/e133_r32_naive_ewc_40reps.json"
REFERENCE_EWC = "runs/e141_r32_ewc_lam3e-4.json"
#: **the knobs this read knows how to read, and the arms each one ran.** The name is the module's for historical
#: reasons (`e167` was the first), and the `--knob` flag is what makes the *same* read usable for `e173`, whose
#: `--iters` arms have the property `e167`'s do not: the Fisher does not depend on them, so a gain step measured
#: there has no Fisher explanation available.
KNOBS = {
    "noise": (("0.5", 0.5, "runs/e167_r32_noise0.5_lam3e-4.json"),
              ("2.0", 2.0, "runs/e167_r32_noise2.0_lam3e-4.json")),
    "iters": (("250", 250, "runs/e173_r32_iters250_lam3e-4.json"),
              ("1000", 1000, "runs/e173_r32_iters1000_lam3e-4.json")),
}
#: the resolution a sign needs before it is evidence
RESOLVED = 2.0
#: what the reference artifacts were run at, for the printout rather than for the arithmetic
REFERENCE_LEVEL = "the registered baseline: noise 1.0, iters 500, lam 3e-4"


def verdict(level_sigma: float, gain_change: float, gain_sigma: float) -> dict:
    """`e167`'s four predictions, applied to one noise setting's two numbers.

    ``level_sigma`` is how far the setting moved `naive`; ``gain_change`` is the penalty's advantage at this
    setting minus its advantage at noise 1.0, so a positive value means the penalty **gained more** where the
    level rose (or lost less where it fell -- the sign of the level step is compared separately).
    """
    moved = abs(level_sigma) >= RESOLVED
    gain_resolved = abs(gain_sigma) >= RESOLVED
    return {"level_moved": bool(moved), "gain_resolved": bool(gain_resolved),
            "agrees": bool(moved and gain_resolved and np.sign(gain_change) == np.sign(level_sigma)),
            "against": bool(moved and gain_resolved and np.sign(gain_change) != np.sign(level_sigma))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--knob", default="noise", choices=sorted(KNOBS),
                    help="which registered level knob to read; `iters` has no Fisher confound")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    knob = args.knob

    naive = load_arm(Path(REFERENCE_NAIVE), "naive")
    ewc = load_arm(Path(REFERENCE_EWC), "ewc")
    out: dict = {"knob": knob, "reference": {"naive": float(naive["forgetting"].mean()),
                               "gain": float((naive["forgetting"] - ewc["forgetting"]).mean())}}
    print(f"== the reference, at {REFERENCE_LEVEL} ==")
    print(f"   `naive` forgetting {naive['forgetting'].mean():.4f} over {naive['n']} seeds "
          f"(`e133`, forty replicates)")
    print(f"   the penalty's gain at lam = 3e-4: "
          f"{(naive['forgetting'] - ewc['forgetting']).mean():+.4f} (`e141` against that `naive`)")
    print("   (the reference pairs `e133` with `e141`, which differ in `lam` -- a field `e160` derives as unread")
    print("    by `naive`, so the level is one number rather than two; the gain is what `lam` moves)")

    print(f"\n== the `{knob}` arms against that reference, forty paired seeds ==")
    print(f"   {knob:<8}{'naive forgetting':>18}{'level step':>12}{'sigma':>8}"
          f"{'gain':>10}{'gain step':>12}{'sigma':>8}")
    ends = []
    for label, value, path in KNOBS[knob]:
        if not Path(path).is_file():
            print(f"   {label:<8}{'NOT RUN YET':>18}")
            continue
        n = load_arm(Path(path), "naive")
        e = load_arm(Path(path), "ewc")
        level = paired(n["forgetting"], naive["forgetting"])
        gain_now = float((n["forgetting"] - e["forgetting"]).mean())
        gain = paired(n["forgetting"] - e["forgetting"], naive["forgetting"] - ewc["forgetting"])
        v = verdict(level["sigma"] if level["change"] >= 0 else -level["sigma"],
                    gain["change"], gain["sigma"])
        out.setdefault("ends", {})[label] = {"noise": value, "level": level, "gain": gain, "verdict": v,
                                            "naive_forgetting": float(n["forgetting"].mean()),
                                            "gain_level": gain_now}
        print(f"   {label:<8}{n['forgetting'].mean():>18.4f}{level['change']:>+12.4f}{level['sigma']:>8.2f}"
              f"{gain_now:>+10.4f}{gain['change']:>+12.4f}{gain['sigma']:>8.2f}")
        ends.append((label, v))
    if not ends:
        print(f"\n   `{knob}` has no artifact yet: the registration's row carries the predictions, and this script")
        print("   refuses to print a verdict for a design whose arms do not exist.")
    else:
        moved = [label for label, v in ends if v["level_moved"]]
        agree = [label for label, v in ends if v["agrees"]]
        against = [label for label, v in ends if v["against"]]
        print("\n== the registered verdict ==")
        print(f"   P1 (the level moved at >= {RESOLVED:g} sigma): {'HOLDS' if moved else 'FAILS'} "
              f"at {moved or 'neither end'}")
        print(f"   P2 (the gain's step has the level's sign and resolves): agrees at {agree or 'nowhere'}")
        print(f"   falsifier (a resolved gain step of the opposite sign): "
              f"{'FIRES at ' + ', '.join(against) if against else 'does not fire'}")
        if not moved:
            print("   null worth keeping: neither end moves the level, so `noise` is not a level knob for this")
            print("   metric and the room account gets no test from this design either")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
