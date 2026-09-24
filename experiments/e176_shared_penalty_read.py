"""E176 -- `e175`'s registered read: the room account with the penalty held fixed.

`e173`'s finding is that the Fisher and the anchor are measured **after** each task's training, so every knob that
moves the forgetting level moves the penalty's *inputs* too — which is why no single-field manipulation in this
corpus can tell "less room to forget" from "a weaker penalty". `e175` is the design that removes it: a reference
run at noise 1.0 that **stores** the diagonal Fisher and its anchor (`--save-fisher`), and a noise-0.5 run that
**replays** them (`--fisher-from`), so the second run is penalised by the first's term while its level is lower.

**This file is written before `e175`'s artifacts exist**, so the verdict is mechanical rather than improvised once
the numbers are in. Its four registered predictions, evaluated and nothing else:

  * **P0** — a free control on the new flags: the reference's `ewc` is **bit-identical** to `e141`'s and its
    `naive` to `e133`'s. Arms are independent of the methods list (the `e133`/`e140` twin measured that), so
    *writing* the Fisher must not move a number;
  * **P1** — the control the design needs: the shared run's `naive` is **bit-identical** to `e167`'s noise-0.5
    `naive`, because that arm has no penalty for a stored Fisher to reach;
  * **P2** — the account's test: the gain still falls with the level, by a **comparable amount to `e167`'s
    −0.0370**, which was measured with each side using its own Fisher;
  * **falsifier** — with the penalty shared the gain's step **collapses toward zero**, which would say the whole
    `e167` effect was the Fisher being re-measured and would overturn the account's only direct evidence.

    python -m experiments.e176_shared_penalty_read
    python -m experiments.e176_shared_penalty_read --json-out runs/e176_shared_penalty_read.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import load_arm, paired

REFERENCE = "runs/e175_r32_ref_noise1.0.json"
SHARED = "runs/e175_r32_noise0.5_shared.json"
#: P0's two twins: the reference's arms must be the ones the corpus already has at this configuration
TWIN_EWC = "runs/e141_r32_ewc_lam3e-4.json"
TWIN_NAIVE = "runs/e133_r32_naive_ewc_40reps.json"
#: P1's twin: `e167`'s own low-noise arm, whose `naive` no stored Fisher can reach
LOW_NOISE_NAIVE = "runs/e167_r32_noise0.5_lam3e-4.json"
#: and the effect P2 is compared against, measured with each side using its own Fisher
OWN_FISHER_GAIN_STEP = -0.0370
#: the resolution a claim needs, and the share of the own-Fisher step below which the falsifier fires
RESOLVED = 2.0
COLLAPSE_SHARE = 0.5


def verdict(gain_step: float, gain_sigma: float, own: float = OWN_FISHER_GAIN_STEP) -> dict:
    """The registered test, as a rule over the shared-penalty gain step and its own resolution.

    The falsifier is a **share** of the own-Fisher step and not a threshold on a σ, because the question is not
    whether the step resolves but whether it *survives*: with the penalty shared, a step that collapses toward zero
    says the earlier effect was the Fisher's re-measurement rather than the room's.
    """
    collapsed = abs(gain_step) < COLLAPSE_SHARE * abs(own)
    survives = abs(gain_step) >= COLLAPSE_SHARE * abs(own) and abs(gain_sigma) >= RESOLVED
    return {"gain_step": gain_step, "gain_sigma": gain_sigma, "share_of_own_fisher_step":
            (gain_step / own) if own else float("nan"),
            "survives": bool(survives), "collapsed": bool(collapsed and abs(gain_sigma) >= RESOLVED)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    missing = [p for p in (REFERENCE, SHARED) if not Path(p).is_file()]
    naive_twin = load_arm(Path(TWIN_NAIVE), "naive")
    ewc_twin = load_arm(Path(TWIN_EWC), "ewc")
    low_naive = load_arm(Path(LOW_NOISE_NAIVE), "naive")
    out: dict = {"reference": REFERENCE, "shared": SHARED, "missing": missing}

    print("== P0: writing the Fisher must not move a number (a free control on the new flags) ==")
    if REFERENCE in missing:
        print("   the reference run has not happened: `ewc` must reproduce `e141_r32_ewc_lam3e-4` bit for bit")
        print("   and `naive` must reproduce `e133_r32_naive_ewc_40reps`, because arms are independent of the")
        print("   methods list -- the `e133`/`e140` twin measured that -- and `--save-fisher` only writes a file.")
    else:
        ref_naive, ref_ewc = load_arm(Path(REFERENCE), "naive"), load_arm(Path(REFERENCE), "ewc")
        same_n = bool(np.array_equal(ref_naive["forgetting"], naive_twin["forgetting"]))
        same_e = bool(np.array_equal(ref_ewc["forgetting"], ewc_twin["forgetting"]))
        out["p0"] = {"naive_bit_identical": same_n, "ewc_bit_identical": same_e}
        print(f"   `naive` vs `e133`: {'BIT-IDENTICAL' if same_n else 'DIFFERS'}   "
              f"`ewc` vs `e141`: {'BIT-IDENTICAL' if same_e else 'DIFFERS'}")

        print("\n== P1: the stored Fisher cannot reach the `naive` arm ==")
        if SHARED in missing:
            print("   the shared-penalty run has not happened: its `naive` must equal `e167`'s noise-0.5 `naive`")
        else:
            sh_naive, sh_ewc = load_arm(Path(SHARED), "naive"), load_arm(Path(SHARED), "ewc")
            same = bool(np.array_equal(sh_naive["forgetting"], low_naive["forgetting"]))
            out["p1"] = {"naive_bit_identical_to_low_noise": same}
            print(f"   vs `e167`'s noise-0.5 `naive`: {'BIT-IDENTICAL' if same else 'DIFFERS'}")

            print("\n== P2: the account's test, with the penalty held fixed ==")
            level = paired(sh_naive["forgetting"], ref_naive["forgetting"])
            gain_step = paired(sh_naive["forgetting"] - sh_ewc["forgetting"],
                               ref_naive["forgetting"] - ref_ewc["forgetting"])
            v = verdict(gain_step["change"], gain_step["sigma"])
            out["p2"] = {"level": level, "gain_step": gain_step, "verdict": v,
                         "own_fisher_gain_step": OWN_FISHER_GAIN_STEP}
            print(f"   the level moved {level['change']:+.4f} ({level['sigma']:.2f} sigma)")
            print(f"   the gain stepped {gain_step['change']:+.4f} ({gain_step['sigma']:.2f} sigma), "
                  f"{100 * v['share_of_own_fisher_step']:.0f}% of the {OWN_FISHER_GAIN_STEP:+.4f} measured with "
                  f"each side using its own Fisher")
            print(f"   -> the room account {'SURVIVES the penalty being held fixed' if v['survives'] else 'does not survive it'}"
                  f"{'; the falsifier FIRES (the effect was the Fisher)' if v['collapsed'] else ''}")

    if missing:
        print("\n   `e175` has no complete pair yet: the registration's row carries the predictions, and this")
        print("   script refuses to print a verdict for a design whose arms do not exist.")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
