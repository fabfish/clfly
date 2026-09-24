"""E162 -- the wiring family's lambda step from 3e-3 to 1.0, on both axes, for four arms.

`e153` ran the wiring family's five-method table at the runner's **default** `lam = 1.0` instead of the intended
`3e-3` (rule 44), which makes it the record's only **properly powered** point at the top of the λ range -- three
and a half decades above the interior optimum `e141` located on the base family. `e144` ran the same four arms on
the same family and the same forty seeds at λ = 3e-3, so the step between the two is **paired** and the only
manipulated field is `lam` (`e160` derives that `ewc` and the two block arms read it and `naive` does not, which is
why `naive` is this unit's control).

    python -m experiments.e162_wiring_lambda_step
    python -m experiments.e162_wiring_lambda_step --json-out runs/e162_wiring_lambda_step.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import load_arm, paired

AT_3E3 = "runs/e144_r32_overlap1_methods_40reps.json"
AT_1_0 = "runs/e153_r32_overlap1_methods_40reps.json"
ARMS = ("naive", "ewc", "ewc-block", "ewc-block-rand")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    A = {tag: {m: load_arm(Path(p), m) for m in ARMS} for tag, p in (("3e-3", AT_3E3), ("1.0", AT_1_0))}
    out: dict = {"arms": {}}

    print("== the wiring family: lambda 3e-3 (e144) -> lambda 1.0 (e153), paired on forty seeds ==")
    print(f"   {'arm':<16}{'forgetting step':>18}{'sigma':>8}{'newest step':>14}{'sigma':>8}")
    for m in ARMS:
        f3, f1 = A["3e-3"][m]["forgetting"], A["1.0"][m]["forgetting"]
        step = paired(f1, f3)
        newest = paired(A["1.0"][m]["newest"], A["3e-3"][m]["newest"])
        out["arms"][m] = {"forgetting_step": step, "newest_step": newest,
                          "levels": {"3e-3": float(f3.mean()), "1.0": float(f1.mean())}}
        print(f"   {m:<16}{step['change']:>+18.4f}{step['sigma']:>8.2f}"
              f"{newest['change']:>+14.4f}{newest['sigma']:>8.2f}")
    ctrl = out["arms"]["naive"]["forgetting_step"]
    print(f"   control -- `naive` is exactly zero to {ctrl['change']:.3g} "
          f"({'PASSES' if ctrl['change'] == 0.0 else 'FAILS'}: `lam` is a field `naive` does not read)")

    print("\n== and each arm against its own `naive`, at each lambda ==")
    print(f"   {'lambda':<8}{'arm':<16}{'forgetting':>14}{'sigma':>8}{'newest':>12}{'sigma':>8}")
    for tag in ("3e-3", "1.0"):
        for m in ARMS[1:]:
            fg = paired(A[tag][m]["forgetting"], A[tag]["naive"]["forgetting"])
            nw = paired(A[tag][m]["newest"], A[tag]["naive"]["newest"])
            out["arms"][m].setdefault("vs_naive", {})[tag] = {"forgetting": fg, "newest": nw}
            print(f"   {tag:<8}{m:<16}{fg['change']:>+14.4f}{fg['sigma']:>8.2f}"
                  f"{nw['change']:>+12.4f}{nw['sigma']:>8.2f}")

    print("\n== reading ==")
    print("   On the base family one step up the ladder (3e-4 -> 3e-3) worsens BOTH axes with both resolved")
    print("   (forgetting +0.0258 at 3.74 sigma, newest -0.0229 at 2.97) and 3e-2/3e-1 are dominated. Here a")
    print("   333x larger lambda leaves the diagonal unmoved on both axes (0.62 and 0.33 sigma) while the two")
    print("   block arms GAIN stability (2.03 sigma) and acquire their first resolved plasticity cost")
    print("   (-0.0266 at 4.29 and -0.0219 at 4.19 sigma) -- so the knob's size is family-relative.")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
