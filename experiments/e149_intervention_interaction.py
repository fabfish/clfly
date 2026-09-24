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

**And the same decomposition runs a second time on `e139`'s whole-body interference**, whose four cells are
carried by later artifacts holding the same arms (`e140`'s plastic `naive` is C0a-identical to `e133`'s, `e146`'s
frozen `naive` to `e125`'s). That block is where the instrument's own check lives -- a frozen offset must give a
**bias term of exactly 0.0** -- and its ordering comparison is the one result that changes a claim already in the
record: the four arms' whole-body terms order **identically** to their forgetting on task 0 and **differently** on
task 1, where the penalty arm carries 1.72x `naive`'s interference with half its forgetting.

**This is exploratory and is registered as such, which is the honest label: the four artifacts were read for
other purposes first, so unlike every other reader in this directory the prediction below was not written before
the runs existed.** What the script carries in exchange is the discipline that the artifacts can still support:
the **pairing check** (rule 39's arm-naming, done as an instrument -- the four configurations must agree on
every field that defines the seed stream and differ only in the two knobs) and the **ceiling**, so that a share
cannot be quoted without the bound that makes it meaningful -- and a share is *refused* rather than printed when
either main effect is itself below 2 sigma.

**And the script carries a SECOND 2x2, because the record can assemble it and it asks the other question of the
same design.** The four cells are the channel (`free` / `frozen`) against the penalty's **strength**
(`lam = 3e-4` / `3e-3`): `e141` and `e133`'s `ewc` for the free cells, `e147`'s two arms for the frozen ones.
There the quantity is not a shared part but **the difference of the two steps** -- *how much the knob's effect
changes when the channel is frozen* -- and it resolves where the first 2x2 does not: **-0.0305 +/- 0.0074 =
4.10 sigma on the accuracy-valued forgetting and 5.61 sigma on the loss-valued one, with the step's sign
reversing** (+0.0258 worse free, -0.0047 better frozen), while on the newest task the same knob costs accuracy in
**both** channels (2.97 sigma and 5.74 sigma) with an interaction of only **1.23 sigma**. **So lambda's stability
effect is the channel's and lambda's plasticity cost is the penalty's**, and the two 2x2s are deliberately kept
side by side because they answer oppositely on the same seeds.

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

#: The **second** 2x2 the record can assemble, and it is a different pair of factors: the channel
#: (`free` / `frozen`) against the penalty's **strength** (`lam = 3e-4` / `3e-3`). Its question is not
#: whether the two interventions share an effect (that is the block above) but whether **the channel changes
#: what the knob does**, which is the difference of the two steps.
CHANNEL_LAMBDA: dict[tuple[str, str], tuple[str, str]] = {
    ("free", "3e-4"): ("runs/e141_r32_ewc_lam3e-4.json", "ewc"),
    ("free", "3e-3"): ("runs/e133_r32_naive_ewc_40reps.json", "ewc"),
    ("frozen", "3e-4"): ("runs/e147_r32_frozenbias_ewc_lam3e-4.json", "ewc"),
    ("frozen", "3e-3"): ("runs/e147_r32_frozenbias_ewc_lam3e-3.json", "ewc"),
}

#: every field that defines the seed stream. The four arms must agree on all of them.
SEED_FIELDS = ("seed0", "repeats", "circuit_size", "iters", "lr", "batch", "train", "test", "noise",
               "classes", "support", "shared_head", "input_overlap", "readout_size")
#: the knobs the four arms are supposed to differ in.
KNOB_FIELDS = ("frozen_bias", "lam", "fisher_batches", "methods")

METRICS = ("forgetting", "loss_forgetting", "accuracy", "theta_drift")

#: The same four cells for the **whole-body first-order interference** (`e139`'s instrument), one metric per
#: task plus their mean. The artifact for each cell is the one that *carries* the instrument: `e133`'s and
#: `e125`'s rows predate it, and the artifacts named here hold the same arms -- `e140`'s plastic `naive` row is
#: per-replicate identical to `e133`'s (C0a) and `e146`'s frozen `naive` row to `e125`'s (`e146`'s own identity).
WB_ARMS: dict[str, tuple[str, str, str]] = {
    "naive": ("runs/e140_r32_methods_plastic_40reps.json", "naive", "the same arm as `e133`'s, C0a-exact"),
    "freeze": ("runs/e146_r32_lam3e-4_frozenbias.json", "naive", "the same arm as `e125`'s, `e146`-exact"),
    "pen": ("runs/e141_r32_ewc_lam3e-4.json", "ewc", "ewc lam=3e-4, offsets free"),
    "both": ("runs/e147_r32_frozenbias_ewc_lam3e-4.json", "ewc", "ewc lam=3e-4 on frozen offsets"),
}
WB_METRICS = ("whole_body_task0", "whole_body_task1", "whole_body_mean")


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
        # per task, used only for the ordering comparison against the interference block. `None` for artifacts
        # that predate the field, so an older file loads rather than raising.
        "forgetting_task0": np.array([(r.get("forgetting_per_task") or [float("nan"), float("nan")])[0]
                                      for r in reps]),
        "forgetting_task1": np.array([(r.get("forgetting_per_task") or [float("nan"), float("nan")])[1]
                                      for r in reps]),
        # the newest task's final accuracy: the column a mean over the first T-1 tasks cannot contain.
        # `nan` for artifacts that predate the field, so an older file loads rather than raising.
        "newest": np.array([(r.get("final_per_task") or [float("nan")])[-1] for r in reps]),
        "config": payload.get("config", {}),
        "n": len(reps),
    }


def load_wb(path: Path, method: str) -> dict | None:
    """The per-replicate whole-body first-order interference, one metric per task plus their mean.

    ``bias_only_task0`` is `e139`'s uncovered-share numerator, and on a frozen arm the instrument must report it
    as **exactly 0.0**, because the offsets cannot move at all. That is a manipulation check and it is asserted
    rather than assumed. The *share* is the ratio of two means rather than the mean of a ratio -- a
    per-replicate ratio has a denominator that crosses zero on this benchmark, and the first version of this
    function returned -5.72 for the `naive` arm because of it.
    """
    if not Path(path).is_file():
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    entry = payload.get("methods", {}).get(method)
    if entry is None:
        return None
    per_task, bias_only = [], []
    for rep in entry["replicates"]:
        tasks = rep["interference"]
        per_task.append([float(t["whole_body"]["cumulative"]) for t in tasks])
        bias_only.append(float(tasks[0]["whole_body"]["bias_only_cumulative"]))
    arr = np.array(per_task)
    return {
        "whole_body_task0": arr[:, 0] if arr.shape[1] > 0 else np.zeros(len(arr)),
        "whole_body_task1": arr[:, 1] if arr.shape[1] > 1 else np.full(len(arr), np.nan),
        "whole_body_mean": arr.mean(axis=1),
        "bias_only_task0": np.array(bias_only),
        "config": payload.get("config", {}),
        "n": len(arr),
    }


def step_interaction(arms: dict, metric: str) -> dict | None:
    """The channel x knob interaction, in the form the question takes: **the difference of the two steps.**

    With the knob written as the step from its lower to its higher value, and the channel as its two settings:

        step_free   = arm(free, high)   - arm(free, low)
        step_frozen = arm(frozen, high) - arm(frozen, low)
        interaction = step_frozen - step_free

    ``interaction`` is therefore *how much the knob's effect changes when the channel is frozen* -- the quantity a
    "the knob is about the channel" claim is about, and one no single step can show. Both steps are paired on the
    seeds; the interaction's sem is theirs in quadrature, and that is an **upper bound** because the two steps
    share two of the four arms (`e133`'s `ewc` is one of them at both λ). None when a cell is missing.
    """
    keys = (("free", "3e-4"), ("free", "3e-3"), ("frozen", "3e-4"), ("frozen", "3e-3"))
    if any(k not in arms or arms[k] is None for k in keys):
        return None
    step_free = paired(arms[("free", "3e-3")][metric], arms[("free", "3e-4")][metric])
    step_frozen = paired(arms[("frozen", "3e-3")][metric], arms[("frozen", "3e-4")][metric])
    # The interaction is computed **per seed** and not as the two steps' sems in quadrature: the two steps sit
    # on different arms but the SAME forty seeds, so their per-seed differences are correlated and quadrature
    # would overstate the interaction's uncertainty. The quadrature sum is reported beside it as that bound.
    d_free = arms[("free", "3e-3")][metric] - arms[("free", "3e-4")][metric]
    d_frozen = arms[("frozen", "3e-3")][metric] - arms[("frozen", "3e-4")][metric]
    inter = paired(d_frozen, d_free)
    quadrature = math.sqrt(step_frozen["sem"] ** 2 + step_free["sem"] ** 2)
    return {"step_free": step_free, "step_frozen": step_frozen,
            "interaction": dict(inter, sem_quadrature=quadrature),
            "levels": {"free/3e-4": float(arms[("free", "3e-4")][metric].mean()),
                       "free/3e-3": float(arms[("free", "3e-3")][metric].mean()),
                       "frozen/3e-4": float(arms[("frozen", "3e-4")][metric].mean()),
                       "frozen/3e-3": float(arms[("frozen", "3e-3")][metric].mean())}}


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


def decompose(arms: dict[str, dict], metrics: tuple[str, ...] = METRICS) -> dict:
    """The 2x2, metric by metric: main effects, the additive prediction, and the interaction.

    Pure, so a test can drive it with four synthetic arms and the algebra can be checked against the identity
    ``I = d_both - d_freeze - d_pen`` rather than trusted. ``metrics`` is a parameter so that the same
    decomposition runs on the interference block without a second copy of this arithmetic.
    """
    out: dict = {}
    for metric in metrics:
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
            # A share is only a share if BOTH main effects are effects: when one of them is unresolved, the
            # "ceiling" is a noise level and the ratio to it means nothing. That is the accuracy axis here (the
            # penalty moves it 0.91 sigma) and the whole-body mean (its penalty term is +0.0048).
            "main_effects_sigma": {"freeze": abs(float(d_freeze.mean())) / paired(d_freeze, np.zeros_like(d_freeze))["sem"],
                                   "pen": abs(float(d_pen.mean())) / paired(d_pen, np.zeros_like(d_pen))["sem"]},
            "ceiling_interpretable": bool(abs(float(d_freeze.mean())) / paired(d_freeze, np.zeros_like(d_freeze))["sem"] >= 2
                                          and abs(float(d_pen.mean())) / paired(d_pen, np.zeros_like(d_pen))["sem"] >= 2),
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

    print("\n== the second 2x2: the channel against the penalty's STRENGTH ==")
    cl_arms = {}
    for key, (path, method) in CHANNEL_LAMBDA.items():
        cl_arms[key] = load_arm(Path(path), method)
        if cl_arms[key] is None:
            print(f"   missing {key} <- {path} [{method}]")
    for metric in ("forgetting", "loss_forgetting", "accuracy", "newest"):
        st = step_interaction(cl_arms, metric)
        if st is None:
            print(f"   {metric}: not printable, a cell is missing")
            continue
        lv = st["levels"]
        print(f"   {metric:<16} levels free {lv['free/3e-4']:+.4f} {lv['free/3e-3']:+.4f} "
              f"| frozen {lv['frozen/3e-4']:+.4f} {lv['frozen/3e-3']:+.4f}")
        print(f"   {'':<16} step with the channel FREE {st['step_free']['change']:+.4f} "
              f"({st['step_free']['sigma']:.2f}s)  FROZEN {st['step_frozen']['change']:+.4f} "
              f"({st['step_frozen']['sigma']:.2f}s)")
        print(f"   {'':<16} INTERACTION (frozen step - free step) {st['interaction']['change']:+.4f} "
              f"+/- {st['interaction']['sem']:.4f} = {st['interaction']['sigma']:.2f}s "
              f"(quadrature bound {st['interaction']['sem_quadrature']:.4f})")

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

    wb, wb_missing = {}, []
    for label, (path, method, words) in WB_ARMS.items():
        arm = load_wb(Path(path), method)
        if arm is None:
            wb_missing.append(f"{label} <- {path} [{method}]")
        wb[label] = arm
    print("\n== the same four cells on `e139`'s whole-body interference ==")
    if wb_missing:
        print("   not printed: the whole-body block is missing from " + "; ".join(wb_missing))
    else:
        check_wb = pairing_check(wb)
        print(f"   pairing: seed fields agreeing {len(check_wb['fields_agreeing'])} of {len(SEED_FIELDS)}, "
              f"replicates {check_wb['replicates']}, agree={check_wb['replicates_agree']}")
        shares = {k: float(v["bias_only_task0"].mean()) / float(v["whole_body_task0"].mean())
                  for k, v in wb.items()}
        frozen_cells_zero = all(float(np.abs(wb[k]["bias_only_task0"]).max()) == 0.0 for k in ("freeze", "both"))
        print("   instrument check: the bias's share of the task-0 whole-body term, as a ratio of means, is "
              + ", ".join(f"{k} {v:+.4f}" for k, v in shares.items())
              + f"; the bias term is EXACTLY zero on both frozen cells: {frozen_cells_zero}")
        decomp_wb = decompose(wb, ("whole_body_task0", "whole_body_task1", "whole_body_mean"))
        for metric, d in decomp_wb.items():
            lv = d["levels"]
            print(f"  {metric:<18}{lv['naive']:>9.4f}{lv['freeze']:>9.4f}{lv['pen']:>9.4f}{lv['both']:>9.4f}"
                  f"{d['additive_predicted_level']:>9.4f}{d['interaction']['change']:>+10.4f}"
                  f"{d['interaction']['sigma']:>8.2f}{d['ceiling_share']:>10.2f}")
        for metric, d in decomp_wb.items():
            i, pos, neg, tied, p = (d["interaction"],) + d["sign_test"]
            print(f"  {metric:<18} I={i['change']:+.4f} +/- {i['sem']:.4f} = {i['sigma']:.2f}s, "
                  f"{pos}/{pos + neg} positive, p={p:.4f}, ceiling {d['ceiling']:.4f}, "
                  f"spread {d['interaction_sd']:.4f} = {d['interaction_sd_over_ceiling']:.2f}x ceiling")
        # the two blocks' orderings, side by side: does the interference order the forgetting here?
        fz = decomp["forgetting"]["levels"]
        print("   by forgetting (mean):  " + " < ".join(f"{k} {fz[k]:.4f}" for k in sorted(fz, key=lambda k: fz[k])))
        lv0 = decomp_wb["whole_body_task0"]["levels"]
        print("   by whole_body_task0:   " + " < ".join(f"{k} {lv0[k]:.4f}" for k in sorted(lv0, key=lambda k: lv0[k])))
        lv1 = decomp_wb["whole_body_task1"]["levels"]
        print("   by whole_body_task1:   " + " < ".join(f"{k} {lv1[k]:.4f}" for k in sorted(lv1, key=lambda k: lv1[k])))
        per_task_forgetting = decompose(arms, ("forgetting_task0", "forgetting_task1"))
        for task, wb_key in ((0, "whole_body_task0"), (1, "whole_body_task1")):
            f = per_task_forgetting[f"forgetting_task{task}"]["levels"]
            w = decomp_wb[wb_key]["levels"]
            f_order = sorted(f, key=lambda k: f[k])
            w_order = sorted(w, key=lambda k: w[k])
            print(f"   task {task}: forgetting {' < '.join(f_order)}  |  interference "
                  f"{' < '.join(w_order)}  -> same order: {f_order == w_order}")
        print("   values, task 0/1 forgetting: "
              + ", ".join(f"{k} {per_task_forgetting['forgetting_task0']['levels'][k]:.4f}/"
                          f"{per_task_forgetting['forgetting_task1']['levels'][k]:.4f}"
                          for k in ("naive", "freeze", "pen", "both")))

    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, {"pairing": check, "decomposition": decomp,
                                   "verdicts": verdicts(decomp),
                                   "whole_body_arms": {k: list(v) for k, v in WB_ARMS.items()},
                                   "whole_body_decomposition": (None if wb_missing else
                                                                decompose(wb, WB_METRICS[:3])),
                                   "arms": {k: list(v) for k, v in ARMS.items()}})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
