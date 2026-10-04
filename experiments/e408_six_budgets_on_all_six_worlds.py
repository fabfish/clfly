"""E408 -- six budgets on all six worlds: the four hundred and eighty updates between twenty and five hundred.

`e407` gave the six measured worlds five budgets each and found the ordering's agreement with the far end running
0.657, 0.429, 0.600, 0.829 and 1.000 -- so it dips at two updates, is more than half restored by five and is above
the 0.8 bar by twenty. It registered what that leaves: *"twenty to five hundred is four hundred and eighty updates
and holds the whole jump from a span of 0.0750 to 0.3104. Whether that widening is gradual or in steps is not
measured."*

**This unit puts a budget inside that stretch.** **One hundred** updates on all six worlds, so the series is 1, 2, 5,
20, 100 and 500. Five claims, registered before any of the new runs' readings was opened.

- **AK1 -- and only the cue population moved, at a hundred.** Over the six hundred-update runs every recorded field
  takes **one** value except the cue seed and the runner's plumbing. **Falsifier**: any other field varying.
- **AK2 -- and the card's world is still on top there.** Its hundred-update reading is the **largest** of the six.
  **Falsifier**: any other world above it. *It is first at one, five, twenty and five hundred and fourth at exactly
  one budget -- two -- so a hundred is the fifth budget where the world that recovers has to hold the lead.*
- **AK3 -- and the ordering there still agrees with the far end.** The rank correlation between the six worlds'
  hundred-update readings and their five-hundred-update ones is at least **0.8**. **Falsifier**: below **0.6**;
  **NULL**: between.
- **AK4 -- and the widening has begun by a hundred.** The six worlds' span at a hundred updates exceeds their span at
  twenty, which `e407` measured as **0.0750**. **Falsifier**: at or below it, which would say the fourfold widening
  happens after a hundred and not inside the stretch this unit is sampling. **REFUSED** when `e407`'s artifact is
  absent.
- **AK5 -- and the initial reading does not move.** Across the six worlds at a hundred updates the connectome's own
  reading of task 0 has a spread of at most **0.05**. **Falsifier**: over **0.10**. **Null**: between.

**What it can do beyond that.** With `e405` to `e407` the six worlds now carry a six-point ordering series and a
six-point spread series, so the two things that change over training -- the ranking of the worlds and the width of the
band they occupy -- are both sampled inside the stretch that held the largest change in either.

**What it cannot do.** *One more budget is one*: the stretch from a hundred to five hundred is four hundred updates
and is still the widest gap in the series. *And the series is six worlds wide*: the four engine redraws are not run at
any budget. *And one arm and one rate*: the 3e-3 `naive` bodies only. *And a probe is not a mechanism.*
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
DRIVEN = ("action_sha1", "feedback_sha1", "world_drive_sha1", "world_read_sha1", "world_coupling_sha1")
#: the budget this unit adds, and the five `e405` to `e407` already rolled
NEW = (100,)
BUDGETS = (1, 2, 5, 20, 100, 500)
SEEDS = {"card": None, "cue1": 1, "cue3": 3, "cue6": 6, "cue9": 9, "cue14": 14}
#: where the five earlier budgets' runs live, unit by unit
EARLIER = {1: "e405", 2: "e406", 5: "e407", 20: "e407"}
#: and the five-hundred-update bodies, which are the far point's
FAR = {
    "card": (Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), Path("runs/e380_theta")),
    "cue1": (Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"), Path("runs/e398_theta_cue1_iters500")),
    "cue3": (Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"), Path("runs/e398_theta_cue3_iters500")),
    "cue6": (Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"), Path("runs/e401_theta_cue6_iters500")),
    "cue9": (Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"), Path("runs/e399_theta_cue9_iters500")),
    "cue14": (Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
              Path("runs/e399_theta_cue14_iters500")),
}
#: `e407`'s artifact, which carries the span at twenty this unit's is measured against
PREVIOUS = Path("runs/e407_five_budgets_on_all_six_worlds.json")
SPAN_AT_TWENTY = 0.0750
KEEPS = 0.8
RESHUFFLES = 0.6
STABLE = 0.05
UNSTABLE = 0.10
CLAIMS = (
    ("AK1", "and only the cue population moved, at a hundred",
     "Over the six hundred-update runs every recorded field takes one value except the cue seed and the runner's "
     "plumbing",
     "falsifier: any other field varying"),
    ("AK2", "and the card's world is still on top there",
     "Its hundred-update reading is the largest of the six",
     "falsifier: any other world above it"),
    ("AK3", f"and the ordering there still agrees with the far end, at {KEEPS:.1f}",
     "The rank correlation between the six worlds' hundred-update readings and their five-hundred-update ones is at "
     "least 0.8",
     f"falsifier: below {RESHUFFLES:.1f}; null: between"),
    ("AK4", "and the widening has begun by a hundred",
     "The six worlds' span at a hundred updates exceeds their span at twenty, 0.0750",
     "falsifier: at or below it; refused when `e407`'s artifact is absent"),
    ("AK5", f"and the initial reading does not move, within {STABLE:.2f}",
     "Across the six worlds at a hundred updates the connectome's own reading of task 0 has a spread of at most 0.05",
     f"falsifier: over {UNSTABLE:.2f}; null: between"),
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


def run_for(name: str, budget: int) -> tuple[Path, Path]:
    """The artifact and the weights of one world at one budget, named the way the unit that rolled it named them."""
    if budget == 500:
        return FAR[name]
    if budget in EARLIER:
        unit = EARLIER[budget]
        #: `e405` and `e406` named their weights by world alone; `e407` added the budget
        tail = "" if budget in (1, 2) else f"_{budget}"
        return (Path(f"runs/{unit}_earned_label_{name}_iters{budget}_20reps.json"),
                Path(f"runs/{unit}_theta_{name}{tail}"))
    return (Path(f"runs/e408_earned_label_{name}_iters{budget}_20reps.json"),
            Path(f"runs/e408_theta_{name}_{budget}"))


def reading(budgets=BUDGETS, seeds: dict = SEEDS, previous: Path = PREVIOUS, arm: str = NAIVE,
            reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "worlds": {}, "budgets": list(budgets), "previous": None, "arm": arm,
           "reps": reps}
    for name, cueseed in seeds.items():
        entry = {"cueseed": cueseed, "budgets": {}}
        for b in budgets:
            run, theta = run_for(name, b)
            doc = load(run)
            if not doc:
                return {**out, "ok": False, "reason": f"world {name} at {b} updates: {run} is absent"}
            got = one_budget(doc, theta, ctx, arm=arm, reps=reps)
            if not got.get("ok"):
                return {**out, "ok": False, "reason": f"world {name} at {b} updates: {got['reason']}"}
            cell = got["cell"]
            entry["budgets"][b] = {
                "artifact": run.name, "iters": (doc.get("config") or {}).get("iters"),
                "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                "body_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                "draw": {f: (doc.get("env_draw") or {}).get(f) for f in ("cue_sha1",) + DRIVEN},
                "settings": dict(doc.get("config") or {})}
        out["worlds"][name] = entry
    prev = load(previous)
    out["previous"] = ({"artifact": Path(previous).name,
                        "span_at_twenty": float((prev.get("spread") or {}).get("20"))} if prev else None)
    order = list(out["worlds"])
    readings = {b: [out["worlds"][n]["budgets"][b]["body_task_0"] for n in order] for b in budgets}
    initials = [out["worlds"][n]["budgets"][b]["initial_task_0"] for n in order for b in budgets]
    out["spread"] = {str(b): max(readings[b]) - min(readings[b]) for b in budgets}
    out["spread"]["initial"] = max(initials) - min(initials)
    out["correlation_with_far"] = {str(b): _spearman(readings[b], readings[500]) for b in budgets}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"} for c in CLAIMS]
    #: a loaded artifact's budget keys are strings, so they are normalised here rather than at every use
    r = {**r, "worlds": {n: {**w, "budgets": {int(k): v for k, v in w["budgets"].items()}}
                         for n, w in r["worlds"].items()}}
    b = NEW[0]
    keys = sorted({k for w in r["worlds"].values() for k in w["budgets"][b]["settings"]})
    varying = sorted(k for k in keys
                     if len({json.dumps(w["budgets"][b]["settings"].get(k)) for w in r["worlds"].values()}) > 1)
    allowed = {"cue_seed", "json_out", "save_theta"}
    off = [k for k in varying if k not in allowed]
    j1 = {"id": "AK1", "measured": f"at a budget of {b} the varying configuration fields are {varying} of {len(keys)}",
          "verdict": f"MET -- one configuration at a budget of {b}, with the cue population the only thing that moves"
          if not off and "cue_seed" in varying else
          f"FALSIFIER FIRED -- {off or 'the cue seed does not vary'}"}

    hundred = {n: w["budgets"][b]["body_task_0"] for n, w in r["worlds"].items()}
    top = max(hundred, key=lambda n: hundred[n])
    j2 = {"id": "AK2", "measured": f"the hundred-update readings are "
                                   f"{ {n: round(v, 4) for n, v in sorted(hundred.items(), key=lambda kv: -kv[1])} }",
          "verdict": f"MET -- the card's world is still on top at a hundred" if top == "card" else
          f"FALSIFIER FIRED -- {top} reads above the card's world at a hundred updates"}

    rho = r["correlation_with_far"][str(b)]
    j3 = {"id": "AK3", "measured": f"the rank correlation between the six worlds' hundred-update readings and their "
                                   f"five-hundred-update ones is {rho:+.3f}, and the whole series with the far end is "
                                   f"{ {k: round(v, 3) for k, v in r['correlation_with_far'].items()} }",
          "verdict": f"MET -- the ordering at a hundred agrees with the far end, {rho:+.3f}" if rho >= KEEPS else
          f"FALSIFIER FIRED -- {rho:+.3f}" if rho < RESHUFFLES else
          f"NULL -- {rho:+.3f}, between {RESHUFFLES:.1f} and {KEEPS:.1f}"}

    span = r["spread"][str(b)]
    if not r["previous"]:
        j4 = {"id": "AK4", "measured": "`e407`'s artifact is not on disk", "verdict": "REFUSED"}
    else:
        twenty = r["previous"]["span_at_twenty"] or SPAN_AT_TWENTY
        j4 = {"id": "AK4", "measured": f"the six worlds span {span:.4f} at a hundred updates against {twenty:.4f} at "
                                       f"twenty, and the whole spread series is "
                                       f"{ {k: round(v, 4) for k, v in r['spread'].items() if k != 'initial'} }",
              "verdict": f"MET -- the widening has begun by a hundred, {span:.4f} against {twenty:.4f}" if
                         span > twenty else
              f"FALSIFIER FIRED -- {span:.4f} is not above the span at twenty, so the widening happens later"}

    spread = r["spread"]["initial"]
    j5 = {"id": "AK5", "measured": f"the connectome's own readings over the six worlds at a hundred updates are "
                                   f"{sorted({round(w['budgets'][b]['initial_task_0'], 4) for w in r['worlds'].values()})}, "
                                   f"a spread of {spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {STABLE:.2f}" if spread <= STABLE else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
          f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== six budgets on all six worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== six budgets on all six worlds ==")
    print(f"   the six measured worlds at {list(BUDGETS)} updates, {r['reps']} replicates on the `{r['arm']}` arm, "
          f"read through the same probe")
    print(f"\n   {'world':>7} {'cue seed':>9} " + " ".join(f"{str(b) + '@':>9}" for b in BUDGETS))
    for n in sorted(r["worlds"], key=lambda x: -r["worlds"][x]["budgets"][500]["body_task_0"]):
        w = r["worlds"][n]
        print(f"   {n:>7} {str(w['cueseed']):>9} " +
              " ".join(f"{w['budgets'][b]['body_task_0']:9.4f}" for b in BUDGETS))
    print(f"\n   the span at each budget: { {b: round(r['spread'][str(b)], 4) for b in BUDGETS} }")
    print(f"   the rank correlation with the far end: "
          f"{ {b: round(r['correlation_with_far'][str(b)], 3) for b in BUDGETS} }")

    print("\n== the registered claims, AK1-AK5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e407` gave the six worlds five budgets and registered that whether the fourfold widening from twenty")
    print("    to five hundred is gradual or in steps was not measured; this puts a hundred inside the stretch)")
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
