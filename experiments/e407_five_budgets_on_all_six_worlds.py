"""E407 -- five budgets on all six worlds: where the ordering comes back.

`e405` found the draw's ordering already there after one update -- the card's world the maximum of the six -- and
`e406` found it gone after two, with the card's world fourth and its agreement with the far end falling from 0.69 to
0.43. Both registered the same gap: the budgets between two and five hundred were not measured on the six worlds.
This unit measures two of them, **five** and **twenty**, so the six worlds carry five budgets each: 1, 2, 5, 20 and
500. Five claims, registered before any of the new runs' readings was opened.

- **AJ1 -- and only the cue population moved, at both new budgets.** Over the six five-update runs and the six
  twenty-update runs every recorded field takes **one** value except the cue seed and the runner's plumbing.
  **Falsifier**: any other field varying.
- **AJ2 -- and the card's world is back on top by twenty.** Its twenty-update reading is the **largest** of the six.
  **Falsifier**: any other world above it. *The card's world is first at one update and fourth at two; whether the
  recovery it shows at five hundred has begun by twenty is the question this budget is for.*
- **AJ3 -- and the ordering at twenty agrees with the far end.** The rank correlation between the six worlds'
  twenty-update readings and their five-hundred-update ones is at least **0.8**. **Falsifier**: below **0.6**, which
  would say the re-establishment happens later than twenty. **Null**: between.
- **AJ4 -- and at five the card's world is still not first.** Its five-update reading is **not** the largest of the
  six. **Falsifier**: it is, which would say the ordering never left. *`e385` measured the card's own trajectory
  falling to its floor at five updates before recovering, so the prediction is that at five it is still on the way
  down; a fired falsifier would say the card's world leads at every budget and `e406`'s reshuffle was one step's
  arithmetic.*
- **AJ5 -- and the initial reading does not move.** Across the six worlds at both new budgets the connectome's own
  reading of task 0 has a spread of at most **0.05**. **Falsifier**: over **0.10**. **Null**: between.

**What it can do beyond that.** With `e405` and `e406` it gives the six worlds a five-point ordering series, so the
question changes from *"is the ordering there at the start"* to *"when is it re-established"*, and the answer is
bounded by the budgets sampled rather than by the two ends.

**What it cannot do.** *Two more budgets are two*: the ordering between five and twenty and between twenty and five
hundred is not sampled. *And the series is six worlds wide*: the four engine redraws are not run at any of these
budgets. *And one arm and one rate*: the 3e-3 `naive` bodies only. *And a probe is not a mechanism.*
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
#: the budgets this unit adds, and the two `e405`/`e406` already rolled
NEW = (5, 20)
#: the six worlds and, for each, the run and weights at every budget
WORLDS = {
    "card": {"cueseed": None,
             "runs": {1: (Path("runs/e405_earned_label_card_iters1_20reps.json"), Path("runs/e405_theta_card")),
                      2: (Path("runs/e406_earned_label_card_iters2_20reps.json"), Path("runs/e406_theta_card")),
                      5: (Path("runs/e407_earned_label_card_iters5_20reps.json"), Path("runs/e407_theta_card_5")),
                      20: (Path("runs/e407_earned_label_card_iters20_20reps.json"), Path("runs/e407_theta_card_20")),
                      500: (Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), Path("runs/e380_theta"))}},
    "cue3": {"cueseed": 3,
             "runs": {1: (Path("runs/e405_earned_label_cue3_iters1_20reps.json"), Path("runs/e405_theta_cue3")),
                      2: (Path("runs/e406_earned_label_cue3_iters2_20reps.json"), Path("runs/e406_theta_cue3")),
                      5: (Path("runs/e407_earned_label_cue3_iters5_20reps.json"), Path("runs/e407_theta_cue3_5")),
                      20: (Path("runs/e407_earned_label_cue3_iters20_20reps.json"), Path("runs/e407_theta_cue3_20")),
                      500: (Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
                            Path("runs/e398_theta_cue3_iters500"))}},
    "cue9": {"cueseed": 9,
             "runs": {1: (Path("runs/e405_earned_label_cue9_iters1_20reps.json"), Path("runs/e405_theta_cue9")),
                      2: (Path("runs/e406_earned_label_cue9_iters2_20reps.json"), Path("runs/e406_theta_cue9")),
                      5: (Path("runs/e407_earned_label_cue9_iters5_20reps.json"), Path("runs/e407_theta_cue9_5")),
                      20: (Path("runs/e407_earned_label_cue9_iters20_20reps.json"), Path("runs/e407_theta_cue9_20")),
                      500: (Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
                            Path("runs/e399_theta_cue9_iters500"))}},
    "cue14": {"cueseed": 14,
              "runs": {1: (Path("runs/e405_earned_label_cue14_iters1_20reps.json"), Path("runs/e405_theta_cue14")),
                       2: (Path("runs/e406_earned_label_cue14_iters2_20reps.json"), Path("runs/e406_theta_cue14")),
                       5: (Path("runs/e407_earned_label_cue14_iters5_20reps.json"),
                           Path("runs/e407_theta_cue14_5")),
                       20: (Path("runs/e407_earned_label_cue14_iters20_20reps.json"),
                            Path("runs/e407_theta_cue14_20")),
                       500: (Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
                             Path("runs/e399_theta_cue14_iters500"))}},
    "cue1": {"cueseed": 1,
             "runs": {1: (Path("runs/e405_earned_label_cue1_iters1_20reps.json"), Path("runs/e405_theta_cue1")),
                      2: (Path("runs/e406_earned_label_cue1_iters2_20reps.json"), Path("runs/e406_theta_cue1")),
                      5: (Path("runs/e407_earned_label_cue1_iters5_20reps.json"), Path("runs/e407_theta_cue1_5")),
                      20: (Path("runs/e407_earned_label_cue1_iters20_20reps.json"), Path("runs/e407_theta_cue1_20")),
                      500: (Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
                            Path("runs/e398_theta_cue1_iters500"))}},
    "cue6": {"cueseed": 6,
             "runs": {1: (Path("runs/e405_earned_label_cue6_iters1_20reps.json"), Path("runs/e405_theta_cue6")),
                      2: (Path("runs/e406_earned_label_cue6_iters2_20reps.json"), Path("runs/e406_theta_cue6")),
                      5: (Path("runs/e407_earned_label_cue6_iters5_20reps.json"), Path("runs/e407_theta_cue6_5")),
                      20: (Path("runs/e407_earned_label_cue6_iters20_20reps.json"), Path("runs/e407_theta_cue6_20")),
                      500: (Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"),
                            Path("runs/e401_theta_cue6_iters500"))}},
}
BUDGETS = (1, 2, 5, 20, 500)
KEEPS = 0.8
RESHUFFLES = 0.6
STABLE = 0.05
UNSTABLE = 0.10
CLAIMS = (
    ("AJ1", "and only the cue population moved, at both new budgets",
     "Over the six five-update and the six twenty-update runs every recorded field takes one value except the cue "
     "seed and the runner's plumbing",
     "falsifier: any other field varying"),
    ("AJ2", "and the card's world is back on top by twenty",
     "Its twenty-update reading is the largest of the six",
     "falsifier: any other world above it"),
    ("AJ3", f"and the ordering at twenty agrees with the far end, at {KEEPS:.1f}",
     "The rank correlation between the six worlds' twenty-update readings and their five-hundred-update ones is at "
     "least 0.8",
     f"falsifier: below {RESHUFFLES:.1f}; null: between"),
    ("AJ4", "and at five the card's world is still not first",
     "Its five-update reading is not the largest of the six",
     "falsifier: it is"),
    ("AJ5", f"and the initial reading does not move, within {STABLE:.2f}",
     "Across the six worlds at both new budgets the connectome's own reading of task 0 has a spread of at most 0.05",
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


def reading(worlds: dict = WORLDS, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "worlds": {}, "budgets": list(BUDGETS), "arm": arm, "reps": reps}
    for name, spec in worlds.items():
        entry = {"cueseed": spec["cueseed"], "budgets": {}}
        for b, (run, theta) in spec["runs"].items():
            doc = load(run)
            if not doc:
                return {**out, "ok": False, "reason": f"world {name} at {b} updates: the artifact is absent"}
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
    order = list(out["worlds"])
    readings = {b: [out["worlds"][n]["budgets"][b]["body_task_0"] for n in order] for b in BUDGETS}
    initials = [out["worlds"][n]["budgets"][b]["initial_task_0"] for n in order for b in BUDGETS]
    out["spread"] = {str(b): max(readings[b]) - min(readings[b]) for b in BUDGETS}
    out["spread"]["initial"] = max(initials) - min(initials)
    out["correlation_with_far"] = {str(b): _spearman(readings[b], readings[500]) for b in BUDGETS}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"} for c in CLAIMS]
    #: a loaded artifact's budget keys are strings, so they are normalised here rather than at every use
    r = {**r, "worlds": {n: {**w, "budgets": {int(k): v for k, v in w["budgets"].items()}}
                         for n, w in r["worlds"].items()}}
    bad = {}
    for b in NEW:
        keys = sorted({k for w in r["worlds"].values() for k in w["budgets"][b]["settings"]})
        varying = sorted(k for k in keys
                         if len({json.dumps(w["budgets"][b]["settings"].get(k))
                                 for w in r["worlds"].values()}) > 1)
        allowed = {"cue_seed", "json_out", "save_theta"}
        off = [k for k in varying if k not in allowed]
        if off or "cue_seed" not in varying:
            bad[b] = {"beyond the cue seed": off, "the cue seed varies": "cue_seed" in varying}
    j1 = {"id": "AJ1", "measured": f"at the two new budgets {NEW} the varying configuration fields are "
                                   f"{ {b: sorted({k for w in r['worlds'].values() for k in w['budgets'][b]['settings'] if len({json.dumps(w['budgets'][b]['settings'].get(k)) for w in r['worlds'].values()}) > 1}) for b in NEW} }",
          "verdict": f"MET -- one configuration at both budgets of {list(NEW)}, with the cue population the only "
                     f"thing that moves" if not bad else f"FALSIFIER FIRED -- {bad}"}

    twos = {n: w["budgets"][20]["body_task_0"] for n, w in r["worlds"].items()}
    top = max(twos, key=lambda n: twos[n])
    j2 = {"id": "AJ2", "measured": f"the twenty-update readings are "
                                   f"{ {n: round(v, 4) for n, v in sorted(twos.items(), key=lambda kv: -kv[1])} }",
          "verdict": "MET -- the card's world is back on top by twenty" if top == "card" else
          f"FALSIFIER FIRED -- {top} reads above the card's world at twenty updates"}

    rho = r["correlation_with_far"]["20"]
    j3 = {"id": "AJ3", "measured": f"the rank correlation between the six worlds' twenty-update readings and their "
                                   f"five-hundred-update ones is {rho:+.3f}, and the same correlation at the other "
                                   f"budgets is { {k: round(v, 3) for k, v in r['correlation_with_far'].items()} }",
          "verdict": f"MET -- the ordering at twenty agrees with the far end, {rho:+.3f}" if rho >= KEEPS else
          f"FALSIFIER FIRED -- {rho:+.3f}: the re-establishment is later than twenty" if rho < RESHUFFLES else
          f"NULL -- {rho:+.3f}, between {RESHUFFLES:.1f} and {KEEPS:.1f}"}

    fives = {n: w["budgets"][5]["body_task_0"] for n, w in r["worlds"].items()}
    fivetop = max(fives, key=lambda n: fives[n])
    j4 = {"id": "AJ4", "measured": f"the five-update readings are "
                                   f"{ {n: round(v, 4) for n, v in sorted(fives.items(), key=lambda kv: -kv[1])} }",
          "verdict": "MET -- the card's world is still not first at five updates" if fivetop != "card" else
          f"FALSIFIER FIRED -- the card's world is first at five updates too, so it leads at every budget sampled"}

    spread = r["spread"]["initial"]
    j5 = {"id": "AJ5", "measured": f"the connectome's own readings over the six worlds at both new budgets are "
                                   f"{sorted({round(w['budgets'][b]['initial_task_0'], 4) for w in r['worlds'].values() for b in NEW})}, a spread of {spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {STABLE:.2f}" if spread <= STABLE else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > UNSTABLE else
          f"NULL -- {spread:.4f}, between {STABLE:.2f} and {UNSTABLE:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== five budgets on all six worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== five budgets on all six worlds ==")
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

    print("\n== the registered claims, AJ1-AJ5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e405` and `e406` put the six worlds at one, two and five hundred updates and registered that the")
    print("    budgets between were not measured; this adds two of them)")
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
