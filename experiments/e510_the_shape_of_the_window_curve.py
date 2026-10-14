"""E510 -- the shape of the window curve: over every window the corpus holds, where the accuracy falls, where it
flattens, and how much of the fall is resolved.

`e505` moved the label's cue across a three-trial pass and called the result **a step and not a slope**; `e506` added
the four-trial pass, separated the label's **window** in drive steps from its **position** in the pass, and found a
knee at window **11** with a slope below it; `e509` added the six-trial pass and read its readings against the
windows the other three passes already carried. The window -- the drive steps between the label's cue and the read,
`11 - i * 12/N` for the label at trial `i` of a pass of `N` trials -- is now carried by **eleven placements over
four pass lengths**, and the corpus holds **six windows**, which order as **11**, **9**, **8**, **7**, **5** and
**3**. No unit has asked what the **shape** of that curve is: where it falls, where it flattens, and how much of the
fall is resolved. This unit reads every placement run on disk, pools each window's family, and characterises the
curve.

The eleven placements and the run each is read from (the window arithmetic is `(tau - 1) - at * (tau // trials)`):

  * window **11** --- `e495`'s two-trial label-first, `e497`'s three-trial label-first and `e506`'s four-trial
    label-first (three pass lengths);
  * window **9** --- `e509`'s six-trial label-at-1 (one pass length);
  * window **8** --- `e506`'s four-trial label-at-1 (one pass length);
  * window **7** --- `e505`'s three-trial label-at-1 and `e509`'s six-trial label-at-2 (two pass lengths);
  * window **5** --- `e493`'s two-trial label-last, `e506`'s four-trial label-at-2 and `e509`'s six-trial
    label-at-3 (three pass lengths);
  * window **3** --- `e505`'s three-trial label-at-2 (one pass length).

**The pooling rule, registered before the reading is opened.** A window's family is pooled by **replicate**: at
replicate `r` the family's value on an arm is the mean, over every placement in the family, of that placement's mean
accuracy diagonal at replicate `r`; the family's pooled accuracy is the mean of those per-replicate values over the
twenty replicate seeds, which for twenty-replicate placements is the same as the mean over every replicate of every
placement in the family. An **adjacent fall** between two neighbouring windows of the ladder is the per-replicate
difference of the two families' pooled values; its mean is the mean of those differences and its sigma is that mean
over the difference's own standard error across the twenty seeds; a fall is **resolved** when its mean is positive
and its sigma is at least **two** on **every** arm. A window carried by a single pass length has one placement, no
spread of its own, and is read as its placement's own mean. Every number below is pooled this way and by no other
rule.

Four claims, registered before any placement was pooled.

- **ZA1 -- the curve falls in the window and does not rise.** Ordering the windows from **11** down to **3**, the
  pooled accuracy of each window's family is non-increasing on at least **two** of the three arms. **Falsifier**:
  an arm whose pooled accuracy rises from a smaller window to a larger one by more than that window's own family
  spread. Read operationally: a **rise** is a pair of neighbouring windows in the ladder whose pooled accuracy is
  higher at the **smaller** window than at the **larger** one, the rise measured as that excess and the tolerance
  the family spread at the smaller window -- a window with a single placement taking the registered bound of
  **0.0312** as its tolerance, since it carries no scatter of its own. *It can fire: window **3** carries one
  placement and its family spread is zero, so any window-**5** value below window **3**'s is a rise with nothing
  to absorb it.*
- **ZA2 -- the fall is graded and not one step.** At least **two** of the adjacent-window falls are resolved at
  **two** sigma, and no single adjacent fall carries more than **half** of the total fall from window **11** to
  window **3**. **Falsifier**: fewer than two resolved adjacent falls, or one adjacent fall carrying more than
  half the total. The total fall is the pooled window-**11** family less the pooled window-**3** placement, per
  arm, and a fall's share is its mean over that total. *It can fire: `e506` called the drop from window **11** a
  knee, so if the step into window **9** carries most of the fall the curve is one step at the top and a flat tail
  below it, not a graded collapse.*
- **ZA3 -- the curve's floor is the chance band.** Every window at or below **7** -- windows **7**, **5** and
  **3** -- has a pooled accuracy within **0.10** of the four-class chance of **0.25** on every arm, while window
  **11** is at least **0.10** above it on every arm. **Falsifier**: a window at or below **7** more than **0.10**
  from chance, or a window-**11** arm less than **0.10** above it.
- **ZA4 -- the curve is a function of the window and not of the pass.** Within each window carried by more than one
  pass length -- windows **11**, **7** and **5** -- the family's spread is at most the registered **0.0312**, and
  the number of cues after the label varies by at least **two** within at least one window. **Falsifier**: a family
  wider than **0.0312**, or no window whose placements differ in the cues that follow the label.

**What it can do beyond that.** It reads the whole ladder in one pass and answers the shape question the earlier
units each left open: whether the fall from window **11** to window **3** is one step with a flat tail, or a graded
collapse in which no single neighbouring pair carries most of it. It reports the extra readings beside the claims --
the full pooled table, each family's spread, each adjacent fall's share and each fall's sigma.

**What it cannot do.** *Eleven placements and six windows are not a dense curve*: the ladder's six windows are
carried by eleven placements over four pass lengths, and the six-trial split alone admits windows **1**, **3**,
**5**, **7**, **9** and **11**, so window **1** is reached by no run and the spacing is uneven -- **11** to **9**
to **8** to **7** to **5** to **3**. *And a window's family is not an independent sample*: the pass lengths that
carry one window share the same world, the same draw and the same replicate seeds, so two placements at one window
are two readings of one configuration and a family spread is not a standard error. *And the position is not fully
separated from the window*: `e509`'s own nearest-neighbour test fired -- the six-trial label-at-2 (window **7**)
reads nearer the four-trial label-at-2 (window **5**) than its own window's three-trial placement -- so at window
**7** the step of the trial and the step of the cue-count cannot be told apart, and this unit reads the ladder by
window without settling that. *And the payout is not on these runs*: no placement command here carries
`--loop-reward`, so nothing is read against the world's currency. *And one read, one body, one budget and one seed
stream*: the accuracy diagonals are the corpus's own card setting at the trained heads, at one circuit, one budget
and `--seed0 0`, so a second world, a second stream and a paid reading are not in it.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e489_the_benchmark_has_an_episode as e489

ARMS = e489.ARMS
TAU = e489.TAU
EPISODE = e489.EPISODE
CHANCE = e489.CHANCE
#: every placement the corpus holds: the key, the pass's length in trials, the 0-based trial index of the cue the
#: label names, and the run on disk it is read from
PLACEMENTS = (
    ("two_at0", 2, 0, Path("runs/e495_earned_label_episode2_labelfirst_20reps.json")),
    ("two_at1", 2, 1, Path("runs/e493_earned_label_episode2_modelread_20reps.json")),
    ("three_at0", 3, 0, Path("runs/e497_earned_label_episode3_labelfirst_20reps.json")),
    ("three_at1", 3, 1, Path("runs/e505_label_at1_episode3_20reps.json")),
    ("three_at2", 3, 2, Path("runs/e505_label_at2_episode3_20reps.json")),
    ("four_at0", 4, 0, Path("runs/e506_label_at0_episode4_20reps.json")),
    ("four_at1", 4, 1, Path("runs/e506_label_at1_episode4_20reps.json")),
    ("four_at2", 4, 2, Path("runs/e506_label_at2_episode4_20reps.json")),
    ("six_at1", 6, 1, Path("runs/e509_label_at1_episode6_20reps.json")),
    ("six_at2", 6, 2, Path("runs/e509_label_at2_episode6_20reps.json")),
    ("six_at3", 6, 3, Path("runs/e509_label_at3_episode6_20reps.json")),
)
#: the ladder: every window the corpus holds, ordered from the largest to the smallest
LADDER = (11, 9, 8, 7, 5, 3)
#: the four-class chance a placement at or below the knee is read against
FLOOR_WINDOW = 7
#: how far inside the chance band a floor window's family must sit, and how far above it window 11 must sit
BAND = 0.10
#: the registered same-window bound, which is the largest spread a same-window family on disk carries (window
#: 11's own, `e506` and `e509` printing it as 0.0312), held as the exact value its replicates give
SPREAD = 0.03125
#: a fall is resolved at this sigma on every arm; the arms a claim needs; the resolved falls a claim needs
SIGMA = 2.0
ARMS_NEEDED = 2
FALLS_NEEDED = 2
#: no single adjacent fall may carry more than this share of the whole fall
HALF = 0.5
PLACES = 4


def window(trials: int, at: int) -> int:
    """The drive steps between the label's cue and the read at the pass's last step.

    The pass is twelve steps and trial ``at`` of a pass of ``trials`` trials opens at step ``at * (tau // trials)``,
    so its window is ``tau - 1 - at * (tau // trials)`` -- the pass's length and the trial's length move together,
    and a step of window is not separated from a step of trial here.
    """
    return (TAU - 1) - at * (TAU // trials)


def cues_after(trials: int, at: int) -> int:
    """The number of cues that follow the label's cue before the read: the pass's trials beyond the label's."""
    return trials - 1 - at


#: each placement's window in drive steps, grouped by window so a window carried by more than one pass length is
#: one family, and the cues that follow the label at each placement
WINDOW = {key: window(trials, at) for key, trials, at, _ in PLACEMENTS}
CUES = {key: cues_after(trials, at) for key, trials, at, _ in PLACEMENTS}
GROUPS = {w: [k for k, _, _, _ in PLACEMENTS if WINDOW[k] == w] for w in LADDER}
#: the placements each claim reads: ZA1 and ZA2 read the whole ladder, ZA3 the floor and the largest window, and
#: ZA4 the windows carried by more than one pass length
ALL = tuple(k for k, _, _, _ in PLACEMENTS)
FLOOR_NEED = tuple(k for k, _, _, _ in PLACEMENTS if WINDOW[k] == LADDER[0] or WINDOW[k] <= FLOOR_WINDOW)
MULTI = tuple(k for k, _, _, _ in PLACEMENTS if len(GROUPS[WINDOW[k]]) >= 2)
CLAIMS = (
    ("ZA1", "the curve falls in the window and does not rise",
     "Ordering the windows from 11 down to 3, the pooled accuracy of each window's family is non-increasing on at "
     "least two of the three arms",
     "falsifier: an arm whose pooled accuracy rises from a smaller window to a larger one by more than that "
     "window's own family spread"),
    ("ZA2", f"the fall is graded and not one step, over {FALLS_NEEDED} resolved falls",
     "At least two of the adjacent-window falls are resolved at two sigma, and no single adjacent fall carries "
     "more than half of the total fall from window 11 to window 3",
     "falsifier: fewer than two resolved adjacent falls, or one adjacent fall carrying more than half the total"),
    ("ZA3", f"the curve's floor is the chance band, within {BAND:.2f} of {CHANCE:.2f}",
     "Every window at or below 7 has a pooled accuracy within 0.10 of the four-class chance of 0.25 on every arm, "
     "while window 11 is at least 0.10 above it on every arm",
     "falsifier: a window at or below 7 more than 0.10 from chance, or a window-11 arm within 0.10 of it"),
    ("ZA4", f"the curve is a function of the window and not of the pass, inside {SPREAD:.4f}",
     "Within each window carried by more than one pass length, the family's spread is at most the registered "
     "0.0312, and the number of cues after the label varies by at least two within at least one window",
     "falsifier: a family wider than 0.0312, or no window whose placements differ in the cues that follow the "
     "label"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path) -> dict | None:
    """One run's per-arm reading: each arm's per-replicate accuracy diagonal and its last rows."""
    if path is None:
        return None
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    got = {}
    for arm in ARMS:
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps:
            return None
        got[arm] = {"replicates": len(reps),
                    "accuracy_diagonal": [statistics.fmean(r["learned"]) for r in reps],
                    "accuracy_last": [statistics.fmean(r["final_per_task"]) for r in reps]}
    return {"artifact": Path(path).name, "arms": got, "config": doc.get("config") or {},
            "env_draw": doc.get("env_draw") or {}}


def _series(rolls: dict, keys, arm: str) -> list[float]:
    """A family's pooled series on one arm: at each replicate, the mean over the family's placements.

    This is the registered pooling rule and the only way a family is read here. The replicate count is the shortest
    the family's placements carry, so a placement with fewer replicates truncates rather than pads.
    """
    here = [rolls[k]["arms"][arm]["accuracy_diagonal"] for k in keys]
    n = min(len(s) for s in here)
    return [statistics.fmean(s[i] for s in here) for i in range(n)]


def _mean(rolls: dict, key: str, arm: str) -> float:
    return statistics.fmean(rolls[key]["arms"][arm]["accuracy_diagonal"])


def _contrast(x: list[float], y: list[float]) -> dict:
    """The paired difference of two pooled series over the replicate seeds, with its own sigma."""
    d = [a - b for a, b in zip(x, y)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _tol(spread: dict, w: int) -> float:
    """The tolerance a rise against the window is read with: the family spread at the window that rose.

    A window carried by a single pass length has no scatter of its own to absorb a rise, so the registered bound is
    its tolerance -- which is stated rather than hidden.
    """
    if str(w) in spread:
        return max(spread[str(w)].values())
    return SPREAD


def _assemble(rolls: dict) -> dict:
    """The reading from the rolls: the pooled table, the family spreads, the adjacent falls and their shares.

    A run that is absent is recorded as absent rather than refused here, so each claim refuses on its own input: the
    whole ladder is ZA1's and ZA2's, the floor and the largest window are ZA3's, and the multi-pass-length windows
    are ZA4's.
    """
    present = {k: v for k, v in rolls.items() if v is not None}
    absent = [k for k, v in rolls.items() if v is None]
    diag = {k: ({a: round(_mean(present, k, a), PLACES) for a in ARMS} if k in present else None)
            for k, _, _, _ in PLACEMENTS}
    family, family_series = {}, {}
    for w in LADDER:
        keys = GROUPS[w]
        if all(k in present for k in keys):
            family[str(w)] = {a: round(statistics.fmean(_series(present, keys, a)), PLACES) for a in ARMS}
            family_series[str(w)] = {a: _series(present, keys, a) for a in ARMS}
    spread = {}
    for w in LADDER:
        keys = GROUPS[w]
        if len(keys) >= 2 and all(k in present for k in keys):
            spread[str(w)] = {a: max(_mean(present, k, a) for k in keys)
                              - min(_mean(present, k, a) for k in keys) for a in ARMS}
    fall = {}
    for a_, b_ in zip(LADDER, LADDER[1:]):
        if str(a_) in family_series and str(b_) in family_series:
            fall[f"{a_}->{b_}"] = {a: _contrast(family_series[str(a_)][a], family_series[str(b_)][a])
                                   for a in ARMS}
    if str(LADDER[0]) in family_series and str(LADDER[-1]) in family_series:
        total = {a: statistics.fmean(family_series[str(LADDER[0])][a])
                 - statistics.fmean(family_series[str(LADDER[-1])][a]) for a in ARMS}
    else:
        total = {}
    share = {pair: {a: (fall[pair][a]["mean"] / total[a] if total.get(a) else 0.0) for a in ARMS}
             for pair in fall} if total else {}
    resolved = {pair: bool(all(fall[pair][a]["mean"] > 0.0 and fall[pair][a]["sigma"] >= SIGMA for a in ARMS))
                for pair in fall}
    cues_range = {str(w): [min(CUES[k] for k in GROUPS[w]), max(CUES[k] for k in GROUPS[w])] for w in LADDER}
    return {"ok": True, "reason": None, "placements": present,
            "spans": {
                "arms": list(ARMS), "chance": CHANCE, "band": BAND, "sigma": SIGMA,
                "arms_needed": ARMS_NEEDED, "falls_needed": FALLS_NEEDED, "half": HALF,
                "bound": SPREAD, "floor_window": FLOOR_WINDOW, "ladder": list(LADDER),
                "tau": TAU, "episode": EPISODE, "replicates": sorted(
                    {v["replicates"] for roll in present.values() for v in roll["arms"].values()}),
                "absent": absent, "windows": dict(WINDOW), "cues": dict(CUES),
                "groups": {str(w): list(GROUPS[w]) for w in LADDER}, "cues_range": cues_range,
                "accuracy_diagonal": diag,
                "family": family,
                "spread": {w: {a: round(v, PLACES) for a, v in s.items()} for w, s in spread.items()},
                "fall": {pair: {a: {kk: round(vv, PLACES) if isinstance(vv, float) else vv
                                    for kk, vv in c.items()} for a, c in arms.items()}
                         for pair, arms in fall.items()},
                "total": {a: round(v, PLACES) for a, v in total.items()},
                "share": {pair: {a: round(v, PLACES) for a, v in arms.items()} for pair, arms in share.items()},
                "resolved": resolved,
            }}


def reading(paths: dict | None = None) -> dict:
    """Every placement's roll, pooled into the window table, the family spreads and the adjacent falls.

    ``paths`` overrides the run each placement is read from, so a caller can drive the reading on synthetic rolls
    without the corpus on disk; it defaults to the eleven placement runs registered above.
    """
    chosen = {key: path for key, _, _, path in PLACEMENTS} if paths is None else dict(paths)
    rolls = {key: _roll(chosen.get(key)) for key, _, _, _ in PLACEMENTS}
    return _assemble(rolls)


def _missing(rolls: dict, keys) -> list[str]:
    return [k for k in keys if k not in rolls]


def _nonincreasing(values: list[float]) -> bool:
    return all(values[i] >= values[i + 1] - 1e-12 for i in range(len(values) - 1))


def _rises(family: dict, spread: dict, arm: str) -> list[dict]:
    """Every neighbouring pair whose pooled accuracy is higher at the smaller window than the larger one.

    The rise is the excess of the smaller window's family over the larger window's, and it is a **win** only when
    it exceeds the smaller window's own family spread (the registered bound where the family is a single placement).
    """
    out = []
    for a_, b_ in zip(LADDER, LADDER[1:]):
        if str(a_) not in family or str(b_) not in family:
            continue
        excess = family[str(b_)][arm] - family[str(a_)][arm]
        if excess > _tol(spread, b_) + 1e-12:
            out.append({"arm": arm, "larger": a_, "smaller": b_, "excess": round(excess, PLACES),
                        "tol": round(_tol(spread, b_), PLACES)})
    return out


def judge(r: dict) -> list[dict]:
    rolls = r["placements"]
    s = r["spans"]
    fam, spread = s["family"], s["spread"]
    #: ZA1 -- the curve falls in the window and does not rise
    if _missing(rolls, ALL):
        j1 = {"id": "ZA1", "measured": f"the ladder is missing {_missing(rolls, ALL)}",
              "verdict": "REFUSED -- a placement the ladder reads is absent, so the families are not pooled and "
                         "the curve is not ordered"}
    else:
        falling = [a for a in ARMS if _nonincreasing([fam[str(w)][a] for w in LADDER])]
        rises = [x for a in ARMS for x in _rises(fam, spread, a)]
        j1 = {"id": "ZA1",
              "measured": "the pooled ladder by arm "
                          + "; ".join(f"{a} " + " > ".join(f"{fam[str(w)][a]:.4f}" for w in LADDER)
                                      for a in ARMS)
                          + f", non-increasing on **{len(falling)}** of three arms, with **{len(rises)}** rises "
                            f"past a window's own family spread ({rises})",
              "verdict": f"MET -- the curve falls in the window: every family is non-increasing down the ladder on "
                         f"{len(falling)} of three arms and no rise clears its window's own family spread"
                         if (len(falling) >= ARMS_NEEDED and not rises) else
                         f"FALSIFIER FIRED -- non-increasing on {len(falling)} of three arms and rises {rises}"}
    #: ZA2 -- the fall is graded and not one step
    if _missing(rolls, ALL):
        j2 = {"id": "ZA2", "measured": f"the ladder is missing {_missing(rolls, ALL)}",
              "verdict": "REFUSED -- an adjacent fall's two families are not both on disk, so the falls are not "
                         "resolved and their shares are not taken"}
    else:
        res = [pair for pair, ok in s["resolved"].items() if ok]
        widest = max(((pair, a, s["share"][pair][a]) for pair in s["share"] for a in ARMS),
                     key=lambda x: x[2], default=(None, None, 0.0))
        over = bool(widest[0]) and widest[2] > HALF + 1e-9
        j2 = {"id": "ZA2",
              "measured": f"the adjacent falls at their sigmas "
                          + "; ".join(f"{pair} " + ", ".join(f"{a} {s['fall'][pair][a]['mean']:+.4f} at "
                                                             f"{s['fall'][pair][a]['sigma']:+.2f} sigma"
                                                             for a in ARMS) for pair in s["fall"])
                          + f"; **{len(res)}** of {len(s['fall'])} resolved on all three arms ({res}); the shares "
                            f"of the total fall "
                          + "; ".join(f"{pair} " + ", ".join(f"{a} {s['share'][pair][a]:.3f}" for a in ARMS)
                                      for pair in s["share"])
                          + f"; the widest share is **{widest[2]:.4f}** ({widest[1]} the {widest[0]} fall)",
              "verdict": f"MET -- the fall is graded: {len(res)} adjacent falls resolved on all three arms and no "
                         f"one fall carries more than half the total" if (len(res) >= FALLS_NEEDED and not over)
                         else f"FALSIFIER FIRED -- {len(res)} resolved falls against the bar of {FALLS_NEEDED}, "
                              f"and the widest share is {widest[2]:.4f} against the bar of {HALF:.2f}"}
    #: ZA3 -- the curve's floor is the chance band
    if _missing(rolls, FLOOR_NEED):
        j3 = {"id": "ZA3", "measured": f"the floor or the largest window is missing {_missing(rolls, FLOOR_NEED)}",
              "verdict": "REFUSED -- a floor window or the window-11 family is not on disk, so the chance band is "
                         "not taken"}
    else:
        floor = [w for w in LADDER if w <= FLOOR_WINDOW]
        out_of = [(w, a, round(fam[str(w)][a], PLACES)) for w in floor for a in ARMS
                  if abs(fam[str(w)][a] - CHANCE) > BAND + 1e-9]
        top = {a: round(fam[str(LADDER[0])][a] - CHANCE, PLACES) for a in ARMS}
        low_top = [a for a in ARMS if top[a] < BAND - 1e-9]
        j3 = {"id": "ZA3",
              "measured": "the floor families " + "; ".join(
                  f"window {w} " + ", ".join(f"{a} {fam[str(w)][a]:.4f}" for a in ARMS) for w in floor)
                          + f" against a chance of {CHANCE:.2f} with a band of {BAND:.2f}, "
                            f"**{len(out_of)}** arm-windows outside the band ({out_of}); window "
                          f"{LADDER[0]}'s arms above chance by {top} with **{len(low_top)}** under the band "
                          f"({low_top})",
              "verdict": f"MET -- the curve's floor is the chance band: every window at or below "
                         f"{FLOOR_WINDOW} within {BAND:.2f} of {CHANCE:.2f} on every arm and window "
                         f"{LADDER[0]} at least {BAND:.2f} above it on every arm"
                         if (not out_of and not low_top) else
                         f"FALSIFIER FIRED -- {len(out_of)} arm-windows outside the chance band ({out_of}) and "
                         f"{len(low_top)} window-{LADDER[0]} arms inside it ({low_top})"}
    #: ZA4 -- the curve is a function of the window and not of the pass
    if _missing(rolls, MULTI):
        j4 = {"id": "ZA4", "measured": f"a multi-pass-length window is missing {_missing(rolls, MULTI)}",
              "verdict": "REFUSED -- a window carried by more than one pass length is not on disk, so its family's "
                         "spread is not taken"}
    else:
        families = {w: list(GROUPS[w]) for w in LADDER if len(GROUPS[w]) >= 2}
        wide = [(str(w), a, round(spread[str(w)][a], PLACES)) for w in families for a in ARMS
                if spread[str(w)][a] > SPREAD + 1e-9]
        varying = [str(w) for w in families if s["cues_range"][str(w)][1] - s["cues_range"][str(w)][0] >= 2]
        j4 = {"id": "ZA4",
              "measured": f"the multi-pass-length windows { {str(w): families[w] for w in families} } with spreads "
                          f"{ {w: s['spread'][w] for w in s['spread']} } against the registered bound of "
                          f"**{SPREAD:.4f}** (**{len(wide)}** arm-families over it, {wide}); the cues after the "
                          f"label range { {str(w): s['cues_range'][str(w)] for w in families} }, with "
                          f"**{len(varying)}** window(s) varying by at least two ({varying})",
              "verdict": f"MET -- the curve is a function of the window and not of the pass: every multi-pass-length "
                         f"family inside {SPREAD:.4f} and {len(varying)} window(s) varying in the cues after the "
                         f"label" if (not wide and varying) else
                         f"FALSIFIER FIRED -- {len(wide)} arm-families over the registered bound ({wide}) and "
                         f"{len(varying)} windows varying in the cues after the label ({varying})"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the shape of the window curve ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an input is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   `e505` called the curve a step and not a slope, `e506` found a knee at window 11 and `e509` added the")
    print("   six-trial pass; this reads every placement on disk and pools each window's family, so the curve is")
    print("   read over eleven placements and six windows -- 11, 9, 8, 7, 5 and 3")
    s = r["spans"]
    print(f"\n   {'window':>6}  {'family':<34} {'cues':>6} " + "  ".join(f"{a:>9}" for a in ARMS)
          + f"  {'spread':>20}")
    for w in LADDER:
        keys = s["groups"][str(w)]
        fam = s["family"].get(str(w))
        cues = s["cues_range"][str(w)]
        name = ",".join(keys)
        cells = "  ".join(f"{fam[a]:>9.4f}" for a in ARMS) if fam else "  ".join(f"{'-':>9}" for _ in ARMS)
        spr = s["spread"].get(str(w))
        sprt = ("  ".join(f"{spr[a]:.4f}" for a in ARMS) if spr else "- (a single pass length)")
        print(f"   {w:>6}  {name:<34} {cues[0]}-{cues[1]:<2} " + cells + f"  {sprt:>20}")
    print(f"\n   the total fall from window {LADDER[0]} to window {LADDER[-1]}: "
          + ", ".join(f"{a} {s['total'].get(a, 0.0):.4f}" for a in ARMS))
    print("   the adjacent falls, their sigmas and their share of the total:")
    for pair in s["fall"]:
        print(f"      {pair:>7}: " + ", ".join(
            f"{a} {s['fall'][pair][a]['mean']:+.4f} at {s['fall'][pair][a]['sigma']:+.2f} sigma "
            f"({s['share'][pair][a]:.3f})" for a in ARMS)
            + ("  [resolved on all arms]" if s["resolved"].get(pair) else ""))
    print("\n== the registered claims, ZA1-ZA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e505`, `e506` and `e509` read the curve at three windows, four and six; this reads its shape)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
