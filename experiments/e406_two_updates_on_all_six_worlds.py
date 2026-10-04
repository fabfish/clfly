"""E406 -- two updates on all six worlds: does the order the first step established survive the second?

`e405` ran all six measured worlds for exactly one update and found the draw's ordering **already there**: the card's
world's one-update reading is the highest of the six, the six span 0.0604 where they span 0.3104 at five hundred, and
the two orderings agree at a rank correlation of 0.69. It registered the next measurement: *"`e384`'s series puts the
card's world at 0.6792, 0.5917 and 0.5750 for one, two and three updates, so the second step costs it twenty times
the first -- whether the six worlds' order survives **that** is the next measurement."*

**This unit runs the second step on all six.** Six two-update runs against their one-update and five-hundred-update
bodies, all through the same probe. Five claims, registered before any of the new runs' readings was opened.

- **AI1 -- and only the cue population moved, at a budget of two.** Over the six two-update runs every recorded field
  takes **one** value except the cue seed and the runner's own plumbing. **Falsifier**: any other field varying.
- **AI2 -- and the order survives the second step.** The six worlds' two-update readings order the worlds the way
  their one-update readings do, at a rank correlation of at least **0.8**. **Falsifier**: below **0.6**, which would
  say the second step -- the one that costs the card's world twenty times the first -- reshuffles them. **Null**:
  between.
- **AI3 -- and the card's world is still the outlier.** Its two-update reading is the **largest** of the six.
  **Falsifier**: any other world above it.
- **AI4 -- and the initial reading does not move.** Across the six worlds the connectome's own reading has a spread
  of at most **0.05**. **Falsifier**: over **0.10**. **Null**: between.
- **AI5 -- and the separation is still growing.** The six two-update readings span **more** than the one-update span
  of **0.0604** and **less** than the five-hundred-update span of **0.3104**. **Falsifier**: at or below the
  one-update span, which would say the second step closes what the first opened, or at or above the five-hundred
  span, which would say the separation is made in two steps and not over five hundred. **REFUSED** when `e405`'s
  artifact is absent.

**What it can do beyond that.** With `e405` it says whether the first step's ordering is **one step's** or the
trajectory's: if the second step keeps it, then the draw's ranking of the worlds is a property of the training from
its beginning; if it reshuffles them, then the first step's agreement with the far end was a coincidence of one
step's arithmetic.

**What it cannot do.** *Two updates are two updates*: three, five and twenty are not measured. *And the ordering is
against six worlds*: the four engine redraws are not run here. *And one arm and one rate*: the 3e-3 `naive` bodies
only. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e379_what_the_body_did import NAIVE, TAU  # noqa: F401  (the same instrument)
from experiments.e380_what_the_training_built import setup as setup_wide
from experiments.e382_when_the_world_loses_it import one_budget

REPS = 20
#: the six worlds: the one-update run `e405` wrote, this unit's two-update run, and the five-hundred-update one
WORLDS = {
    "card": {"cueseed": None,
             "one": (Path("runs/e405_earned_label_card_iters1_20reps.json"), Path("runs/e405_theta_card")),
             "two": (Path("runs/e406_earned_label_card_iters2_20reps.json"), Path("runs/e406_theta_card")),
             "far": (Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), Path("runs/e380_theta"))},
    "cue3": {"cueseed": 3,
             "one": (Path("runs/e405_earned_label_cue3_iters1_20reps.json"), Path("runs/e405_theta_cue3")),
             "two": (Path("runs/e406_earned_label_cue3_iters2_20reps.json"), Path("runs/e406_theta_cue3")),
             "far": (Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
                     Path("runs/e398_theta_cue3_iters500"))},
    "cue9": {"cueseed": 9,
             "one": (Path("runs/e405_earned_label_cue9_iters1_20reps.json"), Path("runs/e405_theta_cue9")),
             "two": (Path("runs/e406_earned_label_cue9_iters2_20reps.json"), Path("runs/e406_theta_cue9")),
             "far": (Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
                     Path("runs/e399_theta_cue9_iters500"))},
    "cue14": {"cueseed": 14,
              "one": (Path("runs/e405_earned_label_cue14_iters1_20reps.json"), Path("runs/e405_theta_cue14")),
              "two": (Path("runs/e406_earned_label_cue14_iters2_20reps.json"), Path("runs/e406_theta_cue14")),
              "far": (Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
                      Path("runs/e399_theta_cue14_iters500"))},
    "cue1": {"cueseed": 1,
             "one": (Path("runs/e405_earned_label_cue1_iters1_20reps.json"), Path("runs/e405_theta_cue1")),
             "two": (Path("runs/e406_earned_label_cue1_iters2_20reps.json"), Path("runs/e406_theta_cue1")),
             "far": (Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
                     Path("runs/e398_theta_cue1_iters500"))},
    "cue6": {"cueseed": 6,
             "one": (Path("runs/e405_earned_label_cue6_iters1_20reps.json"), Path("runs/e405_theta_cue6")),
             "two": (Path("runs/e406_earned_label_cue6_iters2_20reps.json"), Path("runs/e406_theta_cue6")),
             "far": (Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"),
                     Path("runs/e401_theta_cue6_iters500"))},
}
#: `e405`'s artifact, which carries the one-update and five-hundred-update spans this unit's is read against
PREVIOUS = Path("runs/e405_one_update_on_all_six_worlds.json")
ONE_SPAN, FAR_SPAN = 0.0604, 0.3104
KEEPS = 0.8
RESHUFFLES = 0.6
STABLE = 0.05
UNSTABLE = 0.10
CLAIMS = (
    ("AI1", "and only the cue population moved, at a budget of two",
     "Over the six two-update runs every recorded field takes one value except the cue seed and the runner's plumbing",
     "falsifier: any other field varying"),
    ("AI2", f"and the order survives the second step, at {KEEPS:.1f}",
     "The six worlds' two-update readings order them the way their one-update readings do, at a rank correlation of "
     "at least 0.8",
     f"falsifier: below {RESHUFFLES:.1f}; null: between"),
    ("AI3", "and the card's world is still the outlier",
     "Its two-update reading is the largest of the six",
     "falsifier: any other world above it"),
    ("AI4", f"and the initial reading does not move, within {STABLE:.2f}",
     "Across the six worlds the connectome's own reading of task 0 has a spread of at most 0.05",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
    ("AI5", "and the separation is still growing",
     f"The six two-update readings span more than the one-update span of {ONE_SPAN:.4f} and less than the "
     f"five-hundred-update span of {FAR_SPAN:.4f}",
     "falsifier: at or below the one-update span, or at or above the five-hundred span; refused when `e405`'s "
     "artifact is absent"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    for r, i in enumerate(order):
        ranks[i] = float(r)
    return ranks


def _spearman(a: list[float], b: list[float]) -> float:
    ra, rb = _rank(a), _rank(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def _budget(ctx, run: Path, theta: Path, arm: str, reps: int) -> dict | None:
    doc = load(run)
    if not doc:
        return None
    got = one_budget(doc, theta, ctx, arm=arm, reps=reps)
    if not got.get("ok"):
        return None
    cell = got["cell"]
    return {"artifact": run.name, "iters": (doc.get("config") or {}).get("iters"),
            "initial_task_0": statistics.fmean(cell[("initial", 0)]),
            "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
            "settings": dict(doc.get("config") or {})}


def reading(worlds: dict = WORLDS, previous: Path = PREVIOUS, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "worlds": {}, "previous": None, "arm": arm, "reps": reps}
    for name, spec in worlds.items():
        got = {b: _budget(ctx, spec[b][0], spec[b][1], arm, reps) for b in ("one", "two", "far")}
        if any(v is None for v in got.values()):
            return {**out, "ok": False, "reason": f"world {name}: one of its three runs or its weights is absent"}
        out["worlds"][name] = {"cueseed": spec["cueseed"], **got}
    prev = load(previous)
    out["previous"] = ({"artifact": Path(previous).name,
                        "one_span": float((prev.get("spread") or {}).get("one")),
                        "far_span": float((prev.get("spread") or {}).get("far"))} if prev else None)
    ones = [w["one"]["body_task_0"] for w in out["worlds"].values()]
    twos = [w["two"]["body_task_0"] for w in out["worlds"].values()]
    fars = [w["far"]["body_task_0"] for w in out["worlds"].values()]
    initials = [w["two"]["initial_task_0"] for w in out["worlds"].values()]
    out["spread"] = {"one": max(ones) - min(ones), "two": max(twos) - min(twos), "far": max(fars) - min(fars),
                     "initial": max(initials) - min(initials)}
    out["correlation_one_two"] = _spearman(ones, twos)
    out["correlation_two_far"] = _spearman(twos, fars)
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"} for c in CLAIMS]
    keys = sorted({k for w in r["worlds"].values() for k in w["two"]["settings"]})
    varying = sorted(k for k in keys
                     if len({json.dumps(w["two"]["settings"].get(k)) for w in r["worlds"].values()}) > 1)
    allowed = {"cue_seed", "json_out", "save_theta"}
    bad1 = [k for k in varying if k not in allowed] + ([] if "cue_seed" in varying else ["the cue seed does not vary"])
    j1 = {"id": "AI1", "measured": f"over the six two-update runs {len(varying)} of {len(keys)} configuration fields "
                                   f"vary: {varying}",
          "verdict": "MET -- one configuration at a budget of two, with the cue population the only thing that moves"
          if not bad1 else f"FALSIFIER FIRED -- {bad1} varies as well"}

    rho = r["correlation_one_two"]
    j2 = {"id": "AI2", "measured": f"the rank correlation between the six worlds' one-update and two-update readings "
                                   f"is {rho:+.3f}, and between their two-update and five-hundred-update readings "
                                   f"{r['correlation_two_far']:+.3f}",
          "verdict": f"MET -- the order survives the second step, {rho:+.3f}" if rho >= KEEPS else
          f"FALSIFIER FIRED -- {rho:+.3f}: the second step reshuffles the six" if rho < RESHUFFLES else
          f"NULL -- {rho:+.3f}, between {RESHUFFLES:.1f} and {KEEPS:.1f}"}

    twos = {n: w["two"]["body_task_0"] for n, w in r["worlds"].items()}
    top = max(twos, key=lambda n: twos[n])
    j3 = {"id": "AI3", "measured": f"the two-update readings are "
                                   f"{ {n: round(v, 4) for n, v in sorted(twos.items(), key=lambda kv: -kv[1])} }",
          "verdict": "MET -- the card's world is still the outlier after two updates" if top == "card" else
          f"FALSIFIER FIRED -- {top} reads above the card's world after two updates"}

    spread = r["spread"]["initial"]
    j4 = {"id": "AI4", "measured": f"the six worlds' connectome readings are "
                                   f"{[round(w['two']['initial_task_0'], 4) for w in r['worlds'].values()]}, a spread "
                                   f"of {spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {STABLE:.2f}" if spread <= STABLE else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
          f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}

    two_span = r["spread"]["two"]
    if not r["previous"]:
        j5 = {"id": "AI5", "measured": "`e405`'s artifact is not on disk", "verdict": "REFUSED"}
    else:
        #: the previous artifact's own spans, so the comparison is against its numbers and not against constants
        one_span = r["previous"]["one_span"] or ONE_SPAN
        far_span = r["previous"]["far_span"] or FAR_SPAN
        good5 = one_span < two_span < far_span
        j5 = {"id": "AI5", "measured": f"the six two-update readings span {two_span:.4f} against the one-update span "
                                       f"{one_span:.4f} and the five-hundred-update span {far_span:.4f}",
              "verdict": f"MET -- the separation is still growing, {two_span:.4f} between {one_span:.4f} and "
                         f"{far_span:.4f}" if good5 else
              f"FALSIFIER FIRED -- {two_span:.4f} is not between {one_span:.4f} and {far_span:.4f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== two updates on all six worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== two updates on all six worlds ==")
    print(f"   the six measured worlds' bodies after 1, 2 and 500 updates, {r['reps']} replicates on the `{r['arm']}` "
          f"arm, read through the same probe")
    print(f"\n   {'world':>7} {'cue seed':>9} {'initial':>9} {'body@1':>9} {'body@2':>9} {'body@500':>10}")
    for name in sorted(r["worlds"], key=lambda n: r["worlds"][n]["two"]["body_task_0"], reverse=True):
        w = r["worlds"][name]
        print(f"   {name:>7} {str(w['cueseed']):>9} {w['two']['initial_task_0']:9.4f} "
              f"{w['one']['body_task_0']:9.4f} {w['two']['body_task_0']:9.4f} {w['far']['body_task_0']:10.4f}")

    print("\n== the registered claims, AI1-AI5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e405` found the draw's ordering already there after one update and registered that the second step")
    print("    costs the card's world twenty times the first; this asks whether the order survives it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(reps=args.reps)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
