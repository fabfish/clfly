"""E512 -- the earning ledger: over every earned-versus-meter cell the corpus holds, the gain is ordered by the
meter's own level and not by the pass's accuracy.

The game line's central measurement is the **earned-versus-meter ablation**: a pass run with the payout as a
**meter** (`--loop-reward` alone) against the same pass with the map **paid** (`--loop-policy --loop-earn`), read as
the earned run's reward diagonal less the meter run's. `e511` read **three** such pairs -- `e500`'s learned,
two-trial pass at window **11**, its own six-trial knee at window **9** and `e507`'s chance, three-trial pass at
window **7** -- and concluded the gain is ordered by the **meter's own distance from the target** and not by the
pass's accuracy. Three points are not a curve and three points can be an accident.

**This unit reads every pair the corpus holds.** It globs `runs/`, finds every artifact that carries the payout,
pairs each **meter** run with every run on its own pass that carries the **earning** pair of flags, and reads the
paired contrast per arm. No training, no probe. Four claims, registered before this unit's pass over the corpus, each
with an explicit falsifier.

**The pairing rule, held to.** A **cell** is a pair of artifacts, one the **meter** and one the **earned** run, that

  * agree on **every** recorded `config` field except `loop_policy`, `loop_earn`, the ascent rate the earned run
    alone moves (`loop_earn_lr`, whose `None` is the run's own `--lr`), the output path (`json_out`) and the saved
    weights (`save_theta`), with a field recorded `null` on one side and `false` on the other carrying the corpus's
    own inertia -- `e500`'s, `e504`'s and `e511`'s inert rule;
  * agree on **every** field of the environment's draw;
  * carry a payout on both sides: the meter carries `loop_reward` and **neither** `loop_policy` nor `loop_earn`, the
    earned run carries `loop_reward` **and both** flags -- `--loop-earn` needs `--loop-policy` for the map and
    `--loop-reward` for the payout, so the paid side of the ablation is the two flags together -- and every arm of
    both sides carries a reward matrix to read the contrast on.

Every artifact that carries the payout is reported: the ones that pair are the ledger's cells, the ones that do not
are named with the reason, **so a reader can check the census rather than trust it**. The census **admits** a thin
pair: the **20**-replicate floor is LA1's own claim and not the pairing rule, so a cell under the floor belongs in
the ledger and fires the claim rather than disappearing from the census.

- **LA1 -- the census is bounded.** At least **5** cells over at least **4** distinct artifacts, each with at least
  **20** replicates on both sides. **Falsifier**: fewer cells, fewer distinct artifacts, or fewer replicates.
- **LA2 -- the gain is ordered by the meter's level.** Ordering the cells by the meter's own reward level -- its
  diagonal, whose sign is negative, so a **lower** level is a **further** meter, and the order runs from the level's
  top (the closest meter) to its bottom -- the earned run's gain over its meter is non-decreasing on at least **two
  of the three** arms. **Falsifier**: an arm with two cells inverted by more than the registered tolerance.
- **LA3 -- the accuracy does not order it.** Ordering the cells by their `naive` arm's accuracy diagonal instead, in
  the direction the closest meter sits in on `e511`'s three points (the highest accuracy first), the gain fails to be
  non-decreasing on at least **two of the three** arms. **Falsifier**: the gain non-decreasing under the accuracy
  ordering on two or more arms.
- **LA4 -- the pass is free everywhere.** In every cell, no arm's accuracy contrast between the earned and the meter
  run resolves at **two** sigma. **Falsifier**: a cell with an arm resolving.

**The pooling rule.** A cell contributes, per arm: the **meter's level** (the meter run's mean reward diagonal), the
**gain** (the earned run's mean reward diagonal less the meter run's, **paired** over the replicate seeds, with its
own sigma), its **accuracy** (the earned run's mean accuracy diagonal, with the paired contrast against the meter
run's and that contrast's sigma) and its **map distance** (the earned run's mean `policy_move`, the distance from the
identity the map was handed). The two ordering claims are read **per arm** -- three orderings, one per arm, each
counted on its own -- and an **arm is ordered** when no two of its cells whose keys differ are inverted, an inversion
being a pair in which the cell with the **higher** key carries the **larger** gain by more than the registered
tolerance **0.25**. That tolerance is the smallest difference this currency has been shown to carry: `e488`'s own
bar for the earning, itself read from `e485`'s diagonal-to-last-row gaps of **0.19** to **0.35**. A pair of cells
whose keys are **equal** is not compared, because the axis gives them no order, and every cell that ties another is
reported as the cell that ordering cannot place. LA4 is read cell by cell and arm by arm, on the paired contrast's
own sigma, and needs no ordering. A claim whose bar the ledger does not meet reports its falsifier as **FIRED**, and
a corpus that holds no cell at all **REFUSES** all four rather than inventing a number.

**What it can do beyond that.** It turns `e511`'s three points into the corpus's own ledger: the three points are
the ledger's first three and the ordering they named is read over every cell the corpus holds, including the ones
that were never put beside each other -- `e500`'s learned pass, `e501`'s three-trial pass at the same window, the
one-trial pass `e485`/`e488` read, `e502`'s action currency, `e504`'s ascent-rate sweep and `e507`'s and `e511`'s
passes -- and it names the arm on which the pass is not free.

**What it cannot do.** *The cells are the corpus's own and are not independent samples*: several share one world,
one draw and one seed stream -- `e498`'s meter run is the meter of **three** of the cells, so they are one execution
read against three earned runs and the ledger's **24** cell-arms are three arms repeated, not twenty-four pieces of
evidence. *And the arms and the payout are the corpus's own*: `naive`, `ewc-block` and `replay` are the corpus's
three, the payout is the environment's own state-matching target rule and the ascent is the corpus's, so nothing here
says what another arm set or another currency does.
*And a ledger is not a design*: each cell is one configuration executed once, so an ordering over cells is a reading
of those executions and not of the configurations, and the replicate counts and the pass lengths are what the corpus
happened to run. *And the cells at chance passes carry a reward whose scale differs from the learned ones*: the
meter's level runs about **-6** on the window-11 passes, about **-7.9** with the payout on the action and about
**-42** and **-47** on the chance passes, so the level the ordering is read over is a level the corpus did not
choose, and the largest gains are also the ones computed on the widest rewards. *And the ledger reads what already
happened*: it runs nothing, so a pass the corpus has not paid, a second world and a second seed stream are outside
it.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json
from experiments import e489_the_benchmark_has_an_episode as e489

ROOT = Path("runs")
ARMS = e489.ARMS
TAU = e489.TAU
#: the config fields a pair may differ in: the two flags of the paid side, the ascent rate the earned run alone
#: moves, and the run's own bookkeeping -- the output path and the saved weights
EXEMPT = ("loop_policy", "loop_earn", "loop_earn_lr", "json_out", "save_theta")
#: the two flags the paid side of the ablation carries, and the payout flag both sides carry
PAID = ("loop_policy", "loop_earn")
REWARD = "loop_reward"
MIN_CELLS = 5
MIN_ARTIFACTS = 4
MIN_REPS = 20
#: the tolerance an inversion is counted past: the smallest difference this currency has been shown to carry
#: (`e488`'s own bar of 0.25, read from `e485`'s diagonal-to-last-row gaps of 0.19 to 0.35)
TOL = 0.25
SIGMA = 2.0
ARMS_NEEDED = 2
PLACES = 4
CLAIMS = (
    ("LA1", f"the census is bounded, over at least {MIN_CELLS} cells and {MIN_ARTIFACTS} artifacts",
     "At least five cells over at least four distinct artifacts, each with at least twenty replicates on both sides",
     "falsifier: fewer cells, fewer distinct artifacts, or fewer replicates"),
    ("LA2", f"and the gain is ordered by the meter's level, on {ARMS_NEEDED} arms",
     "Ordering the cells per arm by that arm's meter level, from the level's top (the closest meter) to its bottom, "
     "the earned run's gain over its meter is non-decreasing on at least two of the three arms",
     "falsifier: an arm with two cells inverted by more than the registered tolerance"),
    ("LA3", f"and the accuracy does not order it, inverted on {ARMS_NEEDED} arms",
     "Ordering the cells by their naive arm's accuracy diagonal, highest first, the gain fails to be non-decreasing "
     "on at least two of the three arms",
     "falsifier: the gain non-decreasing under the accuracy ordering on two or more arms"),
    ("LA4", f"and the pass is free everywhere, below {SIGMA:.0f} sigma on every arm of every cell",
     "In every cell, no arm's accuracy contrast between the earned and the meter run resolves at two sigma",
     "falsifier: a cell with an arm resolving"),
)


def load(path) -> dict | None:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _inert(key: str, old, new) -> bool:
    """Whether a pair of recorded values is the corpus's own inertia rather than a difference the pair moves.

    Two rules, both the corpus's: the fields a paid pair is allowed to move (the two flags, the ascent rate the earned
    run alone moves, the output path and the saved weights), and the runner's own convention that a flag added after
    an artifact was written reads `null` there and `false` on the newer run.
    """
    if key in EXEMPT:
        return True
    return {old, new} == {None, False}


def _reps(doc: dict, arm: str) -> list:
    return ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []


def _paid(doc: dict, arm: str) -> bool:
    """Whether the arm's replicates carry the payout's own matrix -- the field is written on every run, so the
    matrix's diagonal is what says the world paid."""
    reps = _reps(doc, arm)
    if not reps:
        return False
    for r in reps:
        m = r.get("reward_retention")
        if not m or any(m[k][k] is None for k in range(3)):
            return False
    return True


def _level(doc: dict, arm: str) -> list:
    """The meter's own cells: its reward diagonal's mean per replicate."""
    return [statistics.fmean([r["reward_retention"][k][k] for k in range(3)]) for r in _reps(doc, arm)]


def _accuracy(doc: dict, arm: str) -> list:
    return [statistics.fmean(r["learned"]) for r in _reps(doc, arm)]


def _move(doc: dict, arm: str) -> list | None:
    """The map's distance from the identity, per replicate, or `None` where the run records no movement."""
    moves = [r.get("policy_move") for r in _reps(doc, arm)]
    if not moves or any(m is None for m in moves):
        return None
    return [float(m) for m in moves]


def _paired(a: list, b: list) -> dict:
    """The paired contrast of two per-replicate samples: its mean, its sem and its sigma."""
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _pass(cfg: dict) -> dict:
    """The pass a cell is read on: the episode's length, the label's trial and the window it leaves.

    The window is the drive steps between the label's cue and the read, `tau - 1 - i * (tau / N)`, which is what
    `e506` and `e510` pooled the ladder by. A run that records no episode is one trial of `tau` steps with the cue
    at step **0**, which the same formula reads as window **11** -- carried, with the derivation, rather than
    refused, because the window is a reading of the exercise and not of a claim.
    """
    episode, label_at = cfg.get("loop_episode"), cfg.get("loop_label_at")
    if label_at is None and cfg.get("loop_label_first"):
        label_at = 0
    one_trial = episode is None and label_at is None
    episode = episode or 1
    if label_at is None and not one_trial:
        return {"episode": episode, "label_at": None, "label_first": cfg.get("loop_label_first"),
                "trial_len": TAU // episode, "window": None, "one_trial": one_trial}
    label_at = 0 if one_trial else label_at
    trial_len = TAU // episode
    return {"episode": episode, "label_at": label_at, "label_first": cfg.get("loop_label_first"),
            "trial_len": trial_len, "window": (TAU - 1) - label_at * trial_len, "one_trial": one_trial}


def _against(mine: dict, theirs: dict) -> dict | None:
    """One run's config and draw against the other's, the inert rule applied to the config."""
    cfg, other = mine.get("config"), theirs.get("config")
    if not isinstance(cfg, dict) or not isinstance(other, dict):
        return None
    differing, inert = {}, {}
    for k in sorted(set(cfg) | set(other)):
        old, new = other.get(k), cfg.get(k)
        if old == new:
            continue
        (inert if _inert(k, old, new) else differing)[k] = [old, new]
    draw, other_draw = mine.get("env_draw") or {}, theirs.get("env_draw") or {}
    moved = {k: [other.get(k), cfg.get(k)] for k in PAID}
    draw_differ = {k: [other_draw.get(k), draw.get(k)] for k in sorted(set(draw) | set(other_draw))
                   if draw.get(k) != other_draw.get(k)}
    return {"compared": len(set(cfg) | set(other)), "inert": sorted(inert), "inert_fields": inert,
            "differing": differing, "moved": moved,
            "draw_fields": len(set(draw) | set(other_draw)), "draw_differing": draw_differ}


def _cell(meter: dict, earned: dict) -> dict | None:
    """One earned-versus-meter cell, or `None` where the two are not a pair of this ledger.

    The census **admits** a pair whose replicates are thin, because the replicate floor is LA1's claim and not the
    pairing rule: a cell under the floor belongs in the ledger and fires the claim rather than disappearing from the
    census. What a cell does need is a readable contrast, so an arm with no replicates or no reward matrix on either
    side is not a cell.
    """
    against = _against(earned, meter)
    if against is None or against["differing"] or against["draw_differing"]:
        return None
    arms = {}
    for a in ARMS:
        if not _reps(meter, a) or not _reps(earned, a) or not _paid(meter, a) or not _paid(earned, a):
            return None
        gain = _paired(_level(earned, a), _level(meter, a))
        acc = _paired(_accuracy(earned, a), _accuracy(meter, a))
        move = _move(earned, a)
        arms[a] = {
            "meter_level": statistics.fmean(_level(meter, a)),
            "earned_level": statistics.fmean(_level(earned, a)),
            "gain": gain["mean"], "gain_sigma": gain["sigma"], "gain_se": gain["se"],
            "accuracy": statistics.fmean(_accuracy(earned, a)),
            "accuracy_meter": statistics.fmean(_accuracy(meter, a)),
            "accuracy_change": acc["mean"], "accuracy_sigma": acc["sigma"],
            "map": None if move is None else statistics.fmean(move),
            "map_smallest": None if move is None else min(move),
            "map_above_zero": None if move is None else sum(1 for m in move if m > 0.0),
            "replicates": len(_reps(meter, a)),
        }
    cfg = earned.get("config") or {}
    return {"artifact": earned["artifact"], "meter": meter["artifact"],
            "pass": _pass(cfg), "earn_lr": cfg.get("loop_earn_lr"),
            "reward_on_action": bool(cfg.get("loop_reward_on_action")),
            "replicates": sorted({arms[a]["replicates"] for a in ARMS}),
            "pairing": {"compared": against["compared"], "inert": against["inert"],
                        "moved": against["moved"], "differing": against["differing"],
                        "draw_fields": against["draw_fields"], "draw_differing": against["draw_differing"]},
            "arms": arms,
            #: the accuracy ordering's own key: the `naive` arm's accuracy diagonal, one number per cell
            "naive_accuracy": arms["naive"]["accuracy"]}


def _ties(seq: list, key) -> dict:
    """Which cells an axis does not separate, and the value they tie at."""
    seen, out = {}, {}
    for c in seq:
        k = round(key(c), 12)
        seen.setdefault(k, []).append(c["artifact"])
    for k, names in seen.items():
        if len(names) > 1:
            for n in names:
                out[n] = {"value": k, "with": sorted(x for x in names if x != n)}
    return out


def _ordering(cells: list, arm: str, key, tol: float) -> dict:
    """One arm's ordering by ``key``: the separated pairs, the inversions past ``tol``, and the cells that tie.

    An inversion is a separated pair in which the cell with the **higher** key carries the **larger** gain by more
    than the tolerance. Pairs whose keys are equal are not compared -- the axis gives them no order -- and every cell
    that ties another is reported rather than placed. Beside the inversions the arm carries its **closest call**:
    the separated pair whose inversion is the largest one still inside the tolerance, which is the pair the
    tolerance and not the axis decides.
    """
    seq = sorted(cells, key=lambda c: -key(c))
    inversions, tolerated = [], []
    for i, x in enumerate(seq):
        for y in seq[i + 1:]:
            kx, ky = key(x), key(y)
            if kx == ky:
                continue
            gx, gy = x["arms"][arm]["gain"], y["arms"][arm]["gain"]
            if gx <= gy:
                continue
            row = {"closer": x["artifact"], "further": y["artifact"], "key": [round(kx, PLACES), round(ky, PLACES)],
                   "gain": [round(gx, PLACES), round(gy, PLACES)],
                   #: the gap is the two **published** gains' own difference, so a reader who subtracts the columns
                   #: of a finding's table gets the number the artifact carries
                   "gap": round(round(gx, PLACES) - round(gy, PLACES), PLACES)}
            if gx > gy + tol:
                inversions.append(row)
            else:
                tolerated.append(row)
    return {"sequence": [c["artifact"] for c in seq], "gains": [round(c["arms"][arm]["gain"], PLACES) for c in seq],
            "keys": [round(key(c), PLACES) for c in seq], "inversions": inversions, "tied": _ties(seq, key),
            "closest_call": (max(tolerated, key=lambda r: r["gap"]) if tolerated else None),
            "tolerated_pairs": len(tolerated)}


def orderings(cells: list, tol: float = TOL) -> dict:
    """Both registered orderings, per arm: by the meter's level, and by the naive arm's accuracy."""
    out = {"tolerance": tol, "by_level": {}, "by_accuracy": {}, "arms": list(ARMS)}
    for a in ARMS:
        out["by_level"][a] = _ordering(cells, a, lambda c, a=a: c["arms"][a]["meter_level"], tol)
        out["by_accuracy"][a] = _ordering(cells, a, lambda c: c["naive_accuracy"], tol)
    out["by_level_ordered"] = sorted(a for a in ARMS if not out["by_level"][a]["inversions"])
    out["by_level_inverted"] = sorted(a for a in ARMS if out["by_level"][a]["inversions"])
    out["by_accuracy_ordered"] = sorted(a for a in ARMS if not out["by_accuracy"][a]["inversions"])
    out["by_accuracy_inverted"] = sorted(a for a in ARMS if out["by_accuracy"][a]["inversions"])
    #: the cells an axis does not separate, pooled over the arms: a cell the level cannot place is left out of that
    #: ordering, and the reason is the cell it ties and the level they share
    out["left_out_of_level"] = sorted({n for a in ARMS for n, t in out["by_level"][a]["tied"].items()})
    out["left_out_of_accuracy"] = sorted({n for a in ARMS for n, t in out["by_accuracy"][a]["tied"].items()})
    out["resolving"] = [{"artifact": c["artifact"], "arm": a,
                         "change": round(c["arms"][a]["accuracy_change"], PLACES),
                         "sigma": round(c["arms"][a]["accuracy_sigma"], 2)}
                        for c in cells for a in ARMS if abs(c["arms"][a]["accuracy_sigma"]) >= SIGMA]
    return out


def reading(root: Path = ROOT) -> dict:
    """Every artifact that carries the payout, the cells they pair into, and the artifacts left out with a reason."""
    out = {"ok": True, "reason": None, "root": str(root), "cells": [], "artifacts": [], "left_out": [],
           "collapsed": 0, "candidates": [], "orderings": None,
           "spans": {"arms": list(ARMS), "tau": TAU, "exempt": list(EXEMPT), "paid": list(PAID),
                     "reward": REWARD, "min_cells": MIN_CELLS, "min_artifacts": MIN_ARTIFACTS,
                     "min_reps": MIN_REPS, "tolerance": TOL, "sigma": SIGMA, "arms_needed": ARMS_NEEDED,
                     "pass_formula": "window = (tau - 1) - label_at * (tau // episode)"}}
    try:
        skip = corpus.repeat_paths(root)
    except Exception as exc:                                  # pragma: no cover - the corpus's own rule
        return {**out, "ok": False, "reason": f"the corpus's repeat rule did not run: {exc}"}
    out["collapsed"] = len(skip)
    docs, seen = {}, []
    for path in sorted(Path(root).glob("*.json")):
        if path.name in skip:
            continue
        doc = load(path)
        if not isinstance(doc, dict) or not isinstance(doc.get("config"), dict):
            continue
        cfg = doc["config"]
        if not any(cfg.get(k) for k in (REWARD,) + PAID):
            continue
        doc["artifact"] = path.name
        docs[path.name] = doc
        seen.append(path.name)
    meters = sorted(n for n, d in docs.items()
                    if d["config"].get(REWARD) and not any(d["config"].get(k) for k in PAID))
    earned = sorted(n for n, d in docs.items()
                    if d["config"].get(REWARD) and all(d["config"].get(k) for k in PAID))
    rest = sorted(set(seen) - set(meters) - set(earned))
    out["candidates"] = {"payout": seen, "meters": meters, "earned": earned, "neither": rest}
    for n in rest:
        out["left_out"].append({"artifact": n, "why": "carries the payout or a flag but not the paid pair of flags, "
                                                      "so it is neither the meter nor the earning side of a cell"})
    out["attempts"] = len(meters) * len(earned)
    out["rejected"] = {}
    for m in meters:
        celled = set()
        for e in earned:
            cell = _cell(docs[m], docs[e])
            if cell is not None:
                celled.add(e)
                out["cells"].append(cell)
                continue
            against = _against(docs[e], docs[m])
            if against is None:
                why = "neither side records a config and a draw to compare"
            elif against["differing"]:
                why = "config"
            elif against["draw_differing"]:
                why = "draw"
            else:
                why = "no payout on an arm"
            out["rejected"].setdefault(why, []).append({"meter": m, "earned": e,
                                                        "differing": ({} if against is None
                                                                      else against["differing"])})
        if not celled:
            out["left_out"].append({"artifact": m, "why": "a meter run with no earned run on its own pass"})
    for e in earned:
        if not any(c["artifact"] == e for c in out["cells"]):
            out["left_out"].append({"artifact": e, "why": "an earned run that pairs with no meter run"})
    out["artifacts"] = sorted({c["artifact"] for c in out["cells"]} | {c["meter"] for c in out["cells"]})
    out["cells"].sort(key=lambda c: (c["meter"], c["artifact"]))
    out["orderings"] = orderings(out["cells"])
    return out


def judge(r: dict) -> list[dict]:
    """The four claims, each with the number it was measured at and its verdict."""
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the ledger could not be read"}
                for c in CLAIMS]
    cells = r["cells"]
    if not cells:
        return [{"id": c[0], "measured": "no cell", "verdict": "REFUSED -- runs/ holds no earned-versus-meter cell"}
                for c in CLAIMS]
    thin = [{"artifact": c["artifact"], "replicates": c["replicates"]} for c in cells
            if any(v < MIN_REPS for v in c["replicates"])]
    j1 = {"id": "LA1",
          "measured": f"**{len(cells)}** cells over **{len(r['artifacts'])}** artifacts, at replicates "
                      f"**{sorted({v for c in cells for v in c['replicates']})}**, out of "
                      f"**{len(r['candidates']['payout'])}** artifacts carrying the payout "
                      f"(**{len(r['candidates']['meters'])}** meters, **{len(r['candidates']['earned'])}** earned) and "
                      f"**{r['attempts']}** meter-by-earned attempts, with **{len(r['left_out'])}** artifacts left "
                      f"out and **{r['collapsed']}** second executions collapsed by the corpus's own rule",
          "verdict": f"MET -- the ledger is carried, {len(cells)} cells over {len(r['artifacts'])} artifacts, every "
                     f"cell at {MIN_REPS} replicates or more on both sides"
                     if (len(cells) >= MIN_CELLS and len(r["artifacts"]) >= MIN_ARTIFACTS and not thin) else
                     f"FALSIFIER FIRED -- {len(cells)} cells, {len(r['artifacts'])} artifacts, thin {thin[:4]}"}
    o = r["orderings"]
    ordered, inverted = o["by_level_ordered"], o["by_level_inverted"]
    lev = {a: {"cells": len(o["by_level"][a]["sequence"]), "inversions": len(o["by_level"][a]["inversions"]),
               "gains": o["by_level"][a]["gains"], "keys": o["by_level"][a]["keys"]} for a in ARMS}
    near = {a: (None if o["by_level"][a]["closest_call"] is None
                else {"gap": o["by_level"][a]["closest_call"]["gap"],
                      "closer": o["by_level"][a]["closest_call"]["closer"],
                      "further": o["by_level"][a]["closest_call"]["further"]}) for a in ARMS}
    j2 = {"id": "LA2",
          "measured": f"by the meter's level the arms are ordered on **{len(ordered)} of three** ({ordered}) and "
                      f"inverted on **{len(inverted)}** ({inverted}); per arm {lev}; the closest call, the largest "
                      f"inversion still inside the tolerance of {TOL}: **{near}**; the cells the level does not "
                      f"separate: **{o['left_out_of_level']}**",
          "verdict": f"MET -- the gain is non-decreasing in the meter's level on **{len(ordered)}** of three arms "
                     f"({ordered}), the inverted arms being {inverted} with "
                     f"{ {a: len(o['by_level'][a]['inversions']) for a in ARMS} } inversions"
                     if len(ordered) >= ARMS_NEEDED else
                     f"FALSIFIER FIRED -- ordered on {len(ordered)} of three ({ordered}); the inversions "
                     f"{ {a: o['by_level'][a]['inversions'] for a in inverted} }"}
    acc_ordered, acc_inverted = o["by_accuracy_ordered"], o["by_accuracy_inverted"]
    j3 = {"id": "LA3",
          "measured": f"by the naive arm's accuracy the arms are ordered on **{len(acc_ordered)} of three** "
                      f"({acc_ordered}) and inverted on **{len(acc_inverted)}** ({acc_inverted}); the accuracy keys "
                      f"**{o['by_accuracy'][ARMS[0]]['keys']}** with the gains on each arm "
                      f"**{ {a: o['by_accuracy'][a]['gains'] for a in ARMS} }**; the cells the accuracy does not "
                      f"separate: **{o['left_out_of_accuracy']}**",
          "verdict": f"MET -- the gain fails to be non-decreasing under the accuracy ordering on "
                     f"**{len(acc_inverted)}** of three arms ({acc_inverted})"
                     if len(acc_inverted) >= ARMS_NEEDED else
                     f"FALSIFIER FIRED -- the gain is non-decreasing under the accuracy ordering on "
                     f"{len(acc_ordered)} of three arms ({acc_ordered})"}
    resolving = o["resolving"]
    j4 = {"id": "LA4",
          "measured": f"**{len(resolving)}** of the **{len(cells) * len(ARMS)}** cell-arm accuracy contrasts resolve "
                      f"at two sigma: {resolving}",
          "verdict": f"MET -- no cell's accuracy contrast resolves at two sigma on any arm, over {len(cells)} cells "
                     f"and {len(cells) * len(ARMS)} cell-arms" if not resolving else
                     f"FALSIFIER FIRED -- the accuracy moves at two sigma in {resolving}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the earning ledger ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the corpus could not be read')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    cells = r["cells"]
    print(f"   {len(cells)} earned-versus-meter cells over {len(r['artifacts'])} artifacts, from "
          f"{len(r['candidates']['payout'])} artifacts carrying the payout, with "
          f"{len(r['left_out'])} entries left out and {r['collapsed']} second executions collapsed")
    if not cells:
        print("   runs/ holds no earned-versus-meter cell, so every claim is refused")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"\n   {'the earned run':<52} {'window':>7} {'arm':<10} {'meter level':>12} {'gain':>10} {'sigma':>7} "
          f"{'accuracy':>9} {'d acc':>9} {'sigma':>7} {'map':>8}")
    for c in cells:
        p = c["pass"]
        label = f"{c['artifact']}"
        for i, a in enumerate(ARMS):
            arm = c["arms"][a]
            head = label if i == 0 else ""
            print(f"   {head:<52} {'':>7} {a:<10} {arm['meter_level']:>12.4f} {arm['gain']:>+10.4f} "
                  f"{arm['gain_sigma']:>7.2f} {arm['accuracy']:>9.4f} {arm['accuracy_change']:>+9.4f} "
                  f"{arm['accuracy_sigma']:>7.2f} "
                  f"{('-' if arm['map'] is None else format(arm['map'], '8.4f')):>8}")
        print(f"   {'':<52} {str(p['window']):>7} episode {p['episode']} label_at {p['label_at']} "
              f"{'one trial' if p['one_trial'] else ''} earn_lr {c['earn_lr']} "
              f"reward_on_action {c['reward_on_action']} replicates {c['replicates']}")
    print("\n   the two orderings, per arm, at the registered tolerance " f"{r['orderings']['tolerance']}:")
    for name, key in (("by the meter's level", "by_level"), ("by the naive arm's accuracy", "by_accuracy")):
        print(f"   -- {name}")
        for a in ARMS:
            o = r["orderings"][key][a]
            print(f"      {a:<10} inversions {len(o['inversions']):>2}  keys {o['keys']}")
            print(f"      {'':<10} gains      {o['gains']}")
            for inv in o["inversions"]:
                print(f"      {'':<10} INVERSION closer {inv['closer'][:44]} ({inv['key'][0]}, {inv['gain'][0]}) "
                      f"> further {inv['further'][:44]} ({inv['key'][1]}, {inv['gain'][1]})")
    if r["orderings"]["left_out_of_level"]:
        print(f"   the cells the level does not separate: {r['orderings']['left_out_of_level']}")
    print("   the closest call of the level ordering, per arm -- the largest inversion still inside the tolerance:")
    for a in ARMS:
        row = r["orderings"]["by_level"][a]["closest_call"]
        print(f"      {a:<10} " + ("-" if row is None else
                                   f"gap {row['gap']:.4f}: {row['closer'][:40]} over {row['further'][:40]} "
                                   f"({row['gain'][0]} against {row['gain'][1]})"))
    if r["orderings"]["left_out_of_accuracy"]:
        print(f"   the cells the accuracy does not separate: {r['orderings']['left_out_of_accuracy']}")
    print("   the cell-arms the accuracy resolves at two sigma:")
    for row in r["orderings"]["resolving"]:
        print(f"      {row['artifact'][:52]:52} {row['arm']:<10} {row['change']:+.4f} at {row['sigma']:+.2f} sigma")
    print(f"   the {r['attempts']} meter-by-earned attempts, the ones that are not cells by reason:")
    for why, rows in sorted(r["rejected"].items()):
        print(f"      {why:<26} {len(rows):>3}  e.g. {rows[0]['meter'][:34]} vs {rows[0]['earned'][:34]} "
              f"{('' if not rows[0]['differing'] else sorted(rows[0]['differing']))}")
    print("   the artifacts left out of the ledger, with the reason:")
    for row in r["left_out"]:
        print(f"      {row['artifact'][:52]:52} {row['why']}")
    print("\n== the registered claims, LA1-LA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e511` read three of these pairs at the window curve's three points; this reads every pair the")
    print("    corpus holds)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--runs", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
