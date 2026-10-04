"""E405 -- one update on all six worlds: where in the training the worlds separate.

`e404` closed the third screen -- the annotation table -- and registered the direction that now looks strongest:
*"the **training** itself, since `e396` measured that the draw is invisible before the weights move and worth a third
of the reading after."* The cheapest place to look inside the training is its first step. `e384` measured that one
update costs the card's world **0.0083** at the wide step, so the wide step's first step is **mild** -- where the
tight step's whole loss happens in one update (`e382`). This unit asks whether that mildness is the world's or the
step's, by running all six measured worlds for exactly **one** update and putting their one-update readings against
their five-hundred-update ones. Five claims, registered before any of the new runs' readings was opened.

- **AH1 -- and only the cue population moved, at a budget of one.** Over the six one-update runs every recorded field
  takes **one** value except the cue's fingerprint and the cue seed. **Falsifier**: any other field varying, which
  would make the comparison below a comparison of configurations.
- **AH2 -- and the first update is mild on every world.** Each one-update body reads task 0 within **0.05** of its
  own connectome reading. **Falsifier**: any more than **0.10** away, which would say the wide step's first update
  collapses a world after all and `e384`'s 0.0083 was the card's draw. **Null**: between.
- **AH3 -- and the worlds separate later.** The six one-update readings span at most **0.05** while the same six
  worlds' five-hundred-update readings span at least **0.20**. **Falsifier**: a one-update span over **0.10**, or a
  five-hundred-update span under **0.15**. *This is the unit's own prediction: the draw is nearly invisible at one
  update and a third of the reading at five hundred, so the separation is made **by** the training and not by the
  draw's starting point.*
- **AH4 -- and the initial reading does not move.** Across the six worlds the connectome's own reading of task 0 has a
  spread of at most **0.05**. **Falsifier**: over **0.10**. **Null**: between.
- **AH5 -- and the one that recovers is not distinguished at one update.** The card's world's one-update reading lies
  inside the range the five failing worlds' one-update readings span. **Falsifier**: outside it. *`e396` found the
  card's world the only one of ten that keeps the cue at five hundred updates; if it were also the outlier at one
  update, the draw would be doing the work.*

**What it can do beyond that.** It localises the whole line's separation to a stretch of the training: if the six
worlds are one band after a single update and two groups after five hundred, then no property of the draw can be the
answer, because the draw is the same at both ends -- and the six screens this line has run are explained rather than
merely empty.

**What it cannot do.** *One update is one update*: the separation could be made in the second step or the hundredth,
and only the two ends are measured. *And the worlds are six of ten*: four engine redraws are not run here, so the
band is six wide and not ten. *And one arm and one rate*: the 3e-3 `naive` bodies only, where `e383` showed the tight
end's collapse at two rates. *And a probe is not a mechanism.*
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
#: the six worlds and the two runs each one is read from: the body after one update and the body after five hundred
WORLDS = {
    "card": {"cueseed": None,
             "one": (Path("runs/e405_earned_label_card_iters1_20reps.json"), Path("runs/e405_theta_card")),
             "far": (Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), Path("runs/e380_theta"))},
    "cue3": {"cueseed": 3,
             "one": (Path("runs/e405_earned_label_cue3_iters1_20reps.json"), Path("runs/e405_theta_cue3")),
             "far": (Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
                     Path("runs/e398_theta_cue3_iters500"))},
    "cue9": {"cueseed": 9,
             "one": (Path("runs/e405_earned_label_cue9_iters1_20reps.json"), Path("runs/e405_theta_cue9")),
             "far": (Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
                     Path("runs/e399_theta_cue9_iters500"))},
    "cue14": {"cueseed": 14,
              "one": (Path("runs/e405_earned_label_cue14_iters1_20reps.json"), Path("runs/e405_theta_cue14")),
              "far": (Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
                      Path("runs/e399_theta_cue14_iters500"))},
    "cue1": {"cueseed": 1,
             "one": (Path("runs/e405_earned_label_cue1_iters1_20reps.json"), Path("runs/e405_theta_cue1")),
             "far": (Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
                     Path("runs/e398_theta_cue1_iters500"))},
    "cue6": {"cueseed": 6,
             "one": (Path("runs/e405_earned_label_cue6_iters1_20reps.json"), Path("runs/e405_theta_cue6")),
             "far": (Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"),
                     Path("runs/e401_theta_cue6_iters500"))},
}
MILD = 0.05
COLLAPSED = 0.10
ONE_SPAN = 0.05
FAR_SPAN = 0.20
CLAIMS = (
    ("AH1", "and only the cue population moved, at a budget of one",
     "Over the six one-update runs every recorded field takes one value except the cue's fingerprint and the cue seed",
     "falsifier: any other field varying"),
    ("AH2", f"and the first update is mild on every world, within {MILD:.2f}",
     "Each one-update body reads task 0 within 0.05 of its own connectome reading",
     f"falsifier: any more than {COLLAPSED:.2f} away; null: between"),
    ("AH3", f"and the worlds separate later, within {ONE_SPAN:.2f} at one and {FAR_SPAN:.2f} at five hundred",
     "The six one-update readings span at most 0.05 while their five-hundred-update readings span at least 0.20",
     f"falsifier: a one-update span over {COLLAPSED:.2f}, or a five-hundred-update span under 0.15"),
    ("AH4", f"and the initial reading does not move, within {MILD:.2f}",
     "Across the six worlds the connectome's own reading of task 0 has a spread of at most 0.05",
     f"falsifier: over {COLLAPSED:.2f}; null: between"),
    ("AH5", "and the one that recovers is not distinguished at one update",
     "The card's world's one-update reading lies inside the range the five failing worlds' one-update readings span",
     "falsifier: outside it"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


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
            "cue_sha1": (doc.get("env_draw") or {}).get("cue_sha1"),
            "cue_seed": (doc.get("config") or {}).get("cue_seed"),
            "settings": {k: v for k, v in ((doc.get("config") or {}).items())}}


def reading(worlds: dict = WORLDS, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "worlds": {}, "arm": arm, "reps": reps}
    for name, spec in worlds.items():
        one = _budget(ctx, spec["one"][0], spec["one"][1], arm, reps)
        far = _budget(ctx, spec["far"][0], spec["far"][1], arm, reps)
        if one is None or far is None:
            return {**out, "ok": False, "reason": f"world {name}: one of its two runs or its weights is absent"}
        out["worlds"][name] = {"cueseed": spec["cueseed"], "one": one, "far": far,
                               "one_gain": one["body_task_0"] - one["initial_task_0"],
                               "far_gain": far["body_task_0"] - far["initial_task_0"]}
    ones = [w["one"]["body_task_0"] for w in out["worlds"].values()]
    fars = [w["far"]["body_task_0"] for w in out["worlds"].values()]
    initials = [w["one"]["initial_task_0"] for w in out["worlds"].values()]
    out["spread"] = {"one": max(ones) - min(ones), "far": max(fars) - min(fars),
                     "initial": max(initials) - min(initials)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"} for c in CLAIMS]
    #: the six one-update runs' configuration keys, and how many values each takes
    keys = sorted({k for w in r["worlds"].values() for k in w["one"]["settings"]})
    values = {k: sorted({json.dumps(w["one"]["settings"].get(k)) for w in r["worlds"].values()}) for k in keys}
    varying = sorted(k for k, v in values.items() if len(v) > 1)
    #: the plumbing the runner writes into its own namespace is not a setting -- `json_out` and `save_theta` name
    #: where this run's artifact and weights went
    allowed = {"cue_seed", "json_out", "save_theta"}
    bad1 = [k for k in varying if k not in allowed] + (
        [] if "cue_seed" in varying else ["the cue seed does not vary"])
    j1 = {"id": "AH1", "measured": f"over the six one-update runs {len(varying)} of {len(keys)} configuration fields "
                                   f"vary: {varying}",
          "verdict": "MET -- one configuration at a budget of one, with the cue population the only thing that moves"
          if not bad1 else f"FALSIFIER FIRED -- {bad1} varies as well"}

    away = {n: round(w["one_gain"], 4) for n, w in r["worlds"].items() if abs(w["one_gain"]) > MILD}
    worst = max((abs(w["one_gain"]) for w in r["worlds"].values()), default=0.0)
    j2 = {"id": "AH2", "measured": f"the six one-update gains are "
                                   f"{ {n: round(w['one_gain'], 4) for n, w in r['worlds'].items()} }, the largest "
                                   f"at {worst:.4f}",
          "verdict": f"MET -- the first update is mild on every world, the largest cost {worst:.4f}" if not away else
          f"FALSIFIER FIRED -- {away} is more than {MILD:.2f} away" if worst > COLLAPSED else
          f"NULL -- {worst:.4f}, between {MILD:.2f} and {COLLAPSED:.2f}"}

    one_span, far_span = r["spread"]["one"], r["spread"]["far"]
    good3 = one_span <= ONE_SPAN and far_span >= FAR_SPAN
    j3 = {"id": "AH3", "measured": f"the six one-update readings span {one_span:.4f} and their five-hundred-update "
                                   f"readings span {far_span:.4f}",
          "verdict": f"MET -- the worlds are one band at one update and two groups at five hundred, {one_span:.4f} "
                     f"against {far_span:.4f}" if good3 else
          f"FALSIFIER FIRED -- {one_span:.4f} at one update and {far_span:.4f} at five hundred"}

    spread = r["spread"]["initial"]
    j4 = {"id": "AH4", "measured": f"the six worlds' connectome readings are "
                                   f"{[round(w['one']['initial_task_0'], 4) for w in r['worlds'].values()]}, a spread "
                                   f"of {spread:.4f}",
          "verdict": f"MET -- the initial reading does not move, within {MILD:.2f}" if spread <= MILD else
          f"FALSIFIER FIRED -- a spread of {spread:.4f}" if spread > COLLAPSED else
          f"NULL -- {spread:.4f}, between {MILD:.2f} and {COLLAPSED:.2f}"}

    losers = [w["one"]["body_task_0"] for n, w in r["worlds"].items() if n != "card"]
    card = r["worlds"]["card"]["one"]["body_task_0"]
    good5 = min(losers) <= card <= max(losers)
    j5 = {"id": "AH5", "measured": f"the card's world's one-update reading is {card:.4f} against the five failing "
                                   f"worlds' {[round(v, 4) for v in sorted(losers)]}",
          "verdict": "MET -- the one that recovers is not distinguished at one update" if good5 else
          f"FALSIFIER FIRED -- {card:.4f} is outside the failing worlds' range at one update"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== one update on all six worlds ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== one update on all six worlds ==")
    print(f"   the six measured worlds' bodies after 1 update and after 500, {r['reps']} replicates on the "
          f"`{r['arm']}` arm, read through the same probe")
    print(f"\n   {'world':>7} {'cue seed':>9} {'initial':>9} {'body@1':>9} {'gain@1':>9} {'body@500':>10} {'gain@500':>10}")
    for name in sorted(r["worlds"], key=lambda n: r["worlds"][n]["far_gain"]):
        w = r["worlds"][name]
        print(f"   {name:>7} {str(w['cueseed']):>9} {w['one']['initial_task_0']:9.4f} "
              f"{w['one']['body_task_0']:9.4f} {w['one_gain']:9.4f} {w['far']['body_task_0']:10.4f} "
              f"{w['far_gain']:10.4f}")

    print("\n== the registered claims, AH1-AH5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e404` closed the third screen and named the training as what was left; the cheapest place in it")
    print("    is the first step, which `e384` measured as mild at the wide step for the card's world)")
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
