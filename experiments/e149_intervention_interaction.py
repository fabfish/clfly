"""E149 -- do the two interventions remove the same forgetting, or two different halves of it?

Four arms of the **same design on the same forty seeds** are already on disk, and they form a 2x2:

                        offsets free                     offsets frozen (no penalty)
  no penalty    `e133` `naive`                     `e125` `--frozen-bias`
  `ewc`, lam=3e-4  `e141` `--methods ewc --lam 3e-4`   `e147` `--frozen-bias --methods ewc --lam 3e-4`

`e147`'s finding is that the penalty's effect is *masked* by the free channel: the same lam gives +0.0396
with the offsets free and +0.0026 with them held still. That is a statement about **how much** each
intervention achieves. This script asks the complementary question -- **whether the two are aimed at the same
forgetting** -- which the 2x2 answers by construction:

    additive prediction  F_add = F(freeze) + F(penalty) - F(naive)
    interaction          I     = F(both) - F_add

**I is the shared part of the two interventions' effects, in the additive reading.** With the effects written
as paired changes against the same `naive` row, ``d_freeze = F(freeze) - F(naive)`` (negative = less
forgetting) and ``d_pen = F(penalty) - F(naive)``, the identity is

    I = d_both - d_freeze - d_pen          (d_both = F(both) - F(naive))

so on a metric where less is better and both effects are negative, ``I > 0`` means the two together remove
**less** than the sum of what they remove apart: they were pressing,
at least in part, on the same thing. ``I = 0`` means disjoint effects at this resolution, and ``I`` cannot
exceed ``min(|d_freeze|, |d_pen|)``, which is therefore the ceiling and gives the share ``I / min(...)``.

**This is exploratory and is registered as such, which is the honest label: the four artifacts were read for
other purposes first, so unlike every other reader in this directory the prediction below was not written before
the runs existed.** What the script carries in exchange is the discipline that the artifacts can still support:
the **pairing check** (rule 39's arm-naming, done as an instrument -- the four configurations must agree on
every field that defines the seed stream and differ only in the two knobs) and the **ceiling**, so that a share
cannot be quoted without the bound that makes it meaningful.

**What would refute the shared-carrier reading.** ``I`` within 2 sigma of zero on every metric: then the two
interventions are additive at this resolution and the licensed sentence is *their overlap is below the
resolution of forty paired seeds*, which is a bound and not a zero. The metric axis is part of the test, not
decoration: `e141`'s registered P2 failed on the accuracy forgetting while the same forty pairs answered the
same question *yes* at 4.24 sigma on the loss-valued form, so **I is computed on both, and if they disagree the
disagreement is the result** (rule 37).

    python -m experiments.e149_intervention_interaction

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from experiments.e123_loss_metric import loss_forgetting

#: label -> (path, method, the arm's intervention in words)
ARMS: dict[str, tuple[str, str, str]] = {
    "naive": ("runs/e133_r32_naive_ewc_40reps.json", "naive", "neither"),
    "freeze": ("runs/e125_r32_frozenbias.json", "naive", "offsets frozen, no penalty"),
    "pen": ("runs/e141_r32_ewc_lam3e-4.json", "ewc", "ewc lam=3e-4, offsets free"),
    "both": ("runs/e147_r32_frozenbias_ewc_lam3e-4.json", "ewc", "ewc lam=3e-4 on frozen offsets"),
}

#: every field that defines the seed stream. The four arms must agree on all of them.
SEED_FIELDS = ("seed0", "repeats", "circuit_size", "iters", "lr", "batch", "train", "test", "noise",
               "classes", "support", "shared_head", "input_overlap", "readout_size")
#: the knobs the four arms are supposed to differ in.
KNOB_FIELDS = ("frozen_bias", "lam", "fisher_batches", "methods")

METRICS = ("forgetting", "loss_forgetting", "accuracy", "theta_drift")


def load_arm(path: Path, method: str) -> dict | None:
    """One method's per-replicate series, or None when the artifact or the method is not there."""
    if not Path(path).is_file():
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    entry = payload.get("methods", {}).get(method)
    if entry is None:
        return None
    reps = entry["replicates"]
    drift = np.array([float(np.mean(r["theta_drift"])) for r in reps])
    return {
        "forgetting": np.array([r["mean_forgetting"] for r in reps]),
        "loss_forgetting": np.array([loss_forgetting(r["retention_loss"]) for r in reps]),
        "accuracy": np.array([r["final_accuracy"] for r in reps]),
        "theta_drift": drift,
        "config": payload.get("config", {}),
        "n": len(reps),
    }


def pairing_check(arms: dict[str, dict]) -> dict:
    """Same seed stream, different knobs -- the manipulation check, as a list of differences.

    A contrast here is paired only if the four configurations share every field that determines the seeds. The
    knobs are then printed so that what each arm *is* is visible in the same breath.
    """
    seed_tables = {k: tuple(v["config"].get(f) for f in SEED_FIELDS) for k, v in arms.items()}
    agreements, disagreements = [], []
    for field_idx, field in enumerate(SEED_FIELDS):
        values = {k: t[field_idx] for k, t in seed_tables.items()}
        if len(set(values.values())) == 1:
            agreements.append(field)
        else:
            disagreements.append((field, values))
    knobs = {k: {f: v["config"].get(f) for f in KNOB_FIELDS} for k, v in arms.items()}
    reps = {k: v["n"] for k, v in arms.items()}
    return {"fields_agreeing": agreements,
            "fields_differing": disagreements,
            "replicates": reps,
            "replicates_agree": len(set(reps.values())) == 1,
            "knobs": knobs}


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = np.asarray(a) - np.asarray(b)
    n = len(d)
    sem = float(d.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    mean = float(d.mean())
    sigma = abs(mean) / sem if sem else (0.0 if mean == 0 else float("nan"))
    return {"change": mean, "sem": sem, "sigma": sigma, "n": n, "negative": int((d < 0).sum()),
            "positive": int((d > 0).sum())}


def decompose(arms: dict[str, dict]) -> dict:
    """The 2x2, metric by metric: main effects, the additive prediction, and the interaction.

    Pure, so a test can drive it with four synthetic arms and the algebra can be checked against the identity
    ``I = d_freeze + d_pen - d_both`` rather than trusted.
    """
    out: dict = {}
    for metric in METRICS:
        sign = -1.0 if metric in ("forgetting", "loss_forgetting", "theta_drift") else 1.0
        nz, fz, pe, bo = (arms[k][metric] for k in ("naive", "freeze", "pen", "both"))
        add = fz + pe - nz                                 # the additive prediction, per seed
        d_freeze, d_pen, d_both = fz - nz, pe - nz, bo - nz
        inter = paired(bo, add)
        ceiling = min(abs(float(d_freeze.mean())), abs(float(d_pen.mean())))
        out[metric] = {
            "levels": {k: float(arms[k][metric].mean()) for k in ("naive", "freeze", "pen", "both")},
            "levels_sem": {k: paired(arms[k][metric], np.zeros_like(arms[k][metric]))["sem"]
                           for k in ("naive", "freeze", "pen", "both")},
            "d_freeze": paired(d_freeze, np.zeros_like(d_freeze)),
            "d_pen": paired(d_pen, np.zeros_like(d_pen)),
            "d_both": paired(d_both, np.zeros_like(d_both)),
            "additive_predicted_level": float(add.mean()),
            "interaction": inter,
            "ceiling": ceiling,
            "ceiling_share": (inter["change"] / ceiling) if ceiling else float("nan"),
            # conditional effects, in the direction the metric's sign says is good
            "pen_given_freeze": paired(bo, fz),
            "freeze_given_pen": paired(bo, pe),
            "retention_of_pen": (float(paired(bo, fz)["change"]) / float(d_pen.mean())
                                 if float(d_pen.mean()) else float("nan")),
            "retention_of_freeze": (float(paired(bo, pe)["change"]) / float(d_freeze.mean())
                                    if float(d_freeze.mean()) else float("nan")),
            "good_is_negative": sign < 0,
            "identical_arms": bool(np.array_equal(fz, pe)),
            "sign_test": sign_test(bo - add),
            "interaction_sd": float((bo - add).std(ddof=1)),
            "interaction_sd_over_ceiling": (float((bo - add).std(ddof=1)) / ceiling) if ceiling else float("nan"),
            # how many paired seeds this interaction's own spread would need for a 2- and 3-sigma reading
            "seeds_needed": {f"{z}sigma": (z * float((bo - add).std(ddof=1)) / float(inter["change"])) ** 2
                             if float(inter["change"]) else float("inf") for z in (2, 3)},
        }
    return out


def sign_test(per: np.ndarray) -> tuple[int, int, int, float]:
    """Two-sided sign test on ``per``, **ties dropped** -- `e56`'s convention, imported as a rule.

    `e56`'s twelve per-seed correlations contained exactly one tie and the three conventions disagreed by
    1.7x on the headline p, so ties are counted *separately* here and the caller cannot pick one by accident.
    """
    pos = int((np.asarray(per) > 0).sum())
    neg = int((np.asarray(per) < 0).sum())
    tied = int((np.asarray(per) == 0).sum())
    n = pos + neg
    return pos, neg, tied, (float(binomtest(pos, n).pvalue) if n else float("nan"))


def verdicts(decomp: dict) -> dict:
    """The exploratory reading, stated as a rule rather than a sentence per metric."""
    out = {}
    for metric, d in decomp.items():
        i = d["interaction"]
        resolves = i["sigma"] >= 2.0
        if not resolves:
            out[metric] = "additive at this resolution: the overlap is below the bound, not zero"
        elif (d["good_is_negative"] and i["change"] > 0) or (not d["good_is_negative"] and i["change"] < 0):
            out[metric] = "sub-additive: the two interventions share part of what they remove"
        else:
            out[metric] = "super-additive: together they remove more than the sum of the parts"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    arms = {}
    for label, (path, method, words) in ARMS.items():
        arm = load_arm(Path(path), method)
        if arm is None:
            print(f"missing: {label} <- {path} [{method}]")
        arms[label] = arm
    if any(v is None for v in arms.values()):
        print("a quarter of the 2x2 is not on disk; nothing is printed from a partial design")
        return 1

    check = pairing_check(arms)
    print("== pairing check: one seed stream, two knobs ==")
    print(f"   seed fields agreeing : {len(check['fields_agreeing'])} of {len(SEED_FIELDS)}"
          + ("" if not check["fields_differing"] else "  DIFFERING: "
             + ", ".join(f"{f} {v}" for f, v in check["fields_differing"])))
    print(f"   replicates           : {check['replicates']}  agree={check['replicates_agree']}")
    for label, knobs in check["knobs"].items():
        print(f"   {label:<7} {knobs}")

    decomp = decompose(arms)
    print("\n== the 2x2, by metric (levels, then paired changes; good is negative for "
          "forgetting/loss/drift) ==")
    hdr = ("metric", "naive", "freeze", "pen", "both", "additive", "interaction", "sigma", "ceil.share")
    print("  " + "".join(f"{h:>12}" for h in hdr))
    for metric, d in decomp.items():
        lv = d["levels"]
        print(f"  {metric:<12}{lv['naive']:>12.4f}{lv['freeze']:>12.4f}{lv['pen']:>12.4f}"
              f"{lv['both']:>12.4f}{d['additive_predicted_level']:>12.4f}"
              f"{d['interaction']['change']:>12.4f}{d['interaction']['sigma']:>12.2f}"
              f"{d['ceiling_share']:>12.2f}")

    print("\n== the identity, per metric: I = d_both - d_freeze - d_pen ==")
    for metric, d in decomp.items():
        lhs = d["interaction"]["change"]
        rhs = d["d_both"]["change"] - d["d_freeze"]["change"] - d["d_pen"]["change"]
        print(f"  {metric:<12} I={lhs:+.6f}  d_both-d_freeze-d_pen={rhs:+.6f}  "
              f"residual={lhs - rhs:+.2e}")

    print("\n== conditional against alone: how much of each effect survives the other ==")
    for metric, d in decomp.items():
        print(f"  {metric:<12} pen alone {d['d_pen']['change']:+.4f} ({d['d_pen']['sigma']:.2f}s) -> "
              f"given freeze {d['pen_given_freeze']['change']:+.4f} "
              f"({d['pen_given_freeze']['sigma']:.2f}s), retained {d['retention_of_pen']:.2f}x")
        print(f"  {'':<12} freeze alone {d['d_freeze']['change']:+.4f} ({d['d_freeze']['sigma']:.2f}s) -> "
              f"given pen {d['freeze_given_pen']['change']:+.4f} "
              f"({d['freeze_given_pen']['sigma']:.2f}s), retained {d['retention_of_freeze']:.2f}x")

    print("\n== reading ==")
    for metric, verdict in verdicts(decomp).items():
        d = decomp[metric]
        i = d["interaction"]
        pos, neg, tied, p = d["sign_test"]
        print(f"  {metric:<12} {verdict}  (I={i['change']:+.4f} "
              f"+/- {i['sem']:.4f}, {i['sigma']:.2f}s, {pos}/{pos + neg} positive, {tied} tied, "
              f"sign p={p:.3f}, ceiling {d['ceiling']:.4f})")
        print(f"  {'':<12}   seed spread of I {d['interaction_sd']:.4f} = "
              f"{d['interaction_sd_over_ceiling']:.2f}x the ceiling; a 2s/3s reading of THIS interaction "
              f"would need {d['seeds_needed']['2sigma']:.0f} / {d['seeds_needed']['3sigma']:.0f} seeds")

    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, {"pairing": check, "decomposition": decomp,
                                   "verdicts": verdicts(decomp), "arms": {k: list(v) for k, v in ARMS.items()}})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
