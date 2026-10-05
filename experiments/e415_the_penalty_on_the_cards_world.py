"""E415 -- the penalty on the card's world: the buffer beats the penalty on both axes at eleven sigma, on a second substrate.

`e411` and `e413` measured the corpus's `naive`/`replay` pair on the six worlds and both registered the same gap: *"the
penalty arms are absent from this cell"*, so the reading a continual-learning benchmark exists to make -- the buffer
against the penalty -- could not be made on the earned-label world. Thread (a) of the programme's own list names it:
whether `e276`'s replay-over-penalty result survives on another substrate.

**This unit reads the cell that carries all three.** `e356` rolled the card's world at five hundred iterations with
**`naive`, `ewc-block` and `replay`** in one run and twenty replicates, and `e355` rolled the same cell at five
replicates with the matched random control `ewc-block-rand` beside them. No training, no probe. Five claims,
registered before this unit's pass over either artifact.

- **AP1 -- and the cell is carried, and it is the card's world.** One artifact carries all three arms at **20**
  replicates, and its circuit, read-out draw, cue draw, action draw, task list, iteration budget and penalty strength
  equal the card's world's `e380`. **Reported difference**: `e380` records the world as coupled and this artifact
  carries no such field, so its world is the **uncoupled** rule that predates `e359`. **Falsifier**: any shared field
  differing; **REFUSED** when either artifact is absent.
- **AP2 -- and the buffer beats the penalty on accuracy.** Paired over the twenty shared seeds, `replay` minus
  `ewc-block` is at least **0.10**. **Falsifier**: below **0.05**; **null**: between.
- **AP3 -- and on forgetting too.** The same pair, on mean forgetting, is at least **0.15** in the buffer's favour.
  **Falsifier**: below **0.10**; **null**: between. *AP2 and AP3 together are the unit's own prediction: `e276` found
  replay over penalty at twelve sigma on the overlap suite, and if the result is the aid's and not the suite's, it
  holds on the closed-loop earned-label world as well.*
- **AP4 -- and the penalty is not worth the naive arm here.** `ewc-block` minus `naive` on accuracy is at most
  **zero**. **Falsifier**: at or above **+0.05**, which would say the penalty buys accuracy on this substrate.
- **AP5 -- and the block basis is not distinguished from its matched control.** On the five-replicate cell,
  `ewc-block` minus `ewc-block-rand` is within **0.05** on both axes. **Falsifier**: above **0.10** on either axis.

**What it can do beyond that.** It closes the gap `e411`, `e413` and `e414` all registered, and it answers thread (a):
on the closed-loop earned-label world at five hundred iterations the buffer is worth **+0.1764** of final accuracy at
**11.50 sigma** and **0.2521** less forgetting at **11.65 sigma** against the basis-matched penalty, while the penalty
itself is **not resolved** against the naive arm on either axis (-1.95 sigma and -1.51 sigma). So the ordering
`e276` found is the aid's and not the overlap suite's.

**What it cannot do.** *One world and one penalty strength*: the card's world at `lam = 1.0` with `ewc-block`, so the
`lam` ladder and the diagonal penalty (`ewc`) are not in this cell. *And the world's rule is not the card's*: the
artifact predates the coupling `e359` added, so what is measured is the buffer against the penalty on the earned-label
world's **uncoupled** rule. *And the control has five replicates*: AP5 is a bound and not a resolution. *And the
metric is the corpus's*: `mean_forgetting` is the retention matrix's diagonal minus its last row, which `e305` showed
cannot see the part an arm never learned.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the cell that carries all three arms at twenty replicates, the same cell at five with the matched control, and the
#: card's world's own two-arm run for the draw comparison
CELL20 = Path("runs/e356_earned_label_r32_20reps.json")
CELL5 = Path("runs/e355_earned_label_r32_5reps.json")
REFERENCE = Path("runs/e380_earned_label_cue0_actionsource_20reps.json")
#: the draws that make the cell the card's world, and the fields the two artifacts are compared on
SHARED = ("circuit", "readout", "tasks")
DRAW_FIELDS = ("cue_sha1", "action_sha1", "world_read_sha1", "world_drive_sha1")
CONFIG_FIELDS = ("circuit_size", "iters", "lr", "lam", "replay_per_task", "replay_batch", "train", "test", "classes",
                 "support", "basis", "closed_loop", "loop_cue_at", "readout_from_world")
CONTRASTS = (("replay", "ewc-block"), ("ewc-block", "naive"), ("replay", "naive"))
N_TASKS = 3
MIN_REPS = 20
BIG = 0.10
BIG_FIRES = 0.05
CUT = 0.15
CUT_FIRES = 0.10
PENALTY_BAR = 0.0
PENALTY_FIRES = 0.05
CONTROL_BAR = 0.05
CONTROL_FIRES = 0.10
CLAIMS = (
    ("AP1", f"and the cell is carried, at least {MIN_REPS} replicates and all three arms",
     "One artifact carries `naive`, `ewc-block` and `replay` at twenty replicates, and its circuit, read-out draw, "
     "cue draw, action draw, tasks, budget and penalty strength equal the card's world's `e380`",
     "falsifier: any shared field differing; refused when either artifact is absent"),
    ("AP2", f"and the buffer beats the penalty on accuracy, {BIG:.2f}",
     "Paired over the twenty shared seeds, replay minus ewc-block on final accuracy is at least 0.10",
     f"falsifier: below {BIG_FIRES:.2f}; null: between"),
    ("AP3", f"and on forgetting too, {CUT:.2f}",
     "The same pair, on mean forgetting, is at least 0.15 in the buffer's favour",
     f"falsifier: below {CUT_FIRES:.2f}; null: between"),
    ("AP4", "and the penalty is not worth the naive arm here",
     "ewc-block minus naive on final accuracy is at most zero",
     f"falsifier: at or above {PENALTY_FIRES:+.2f}"),
    ("AP5", f"and the block basis is not distinguished from its matched control, {CONTROL_BAR:.2f}",
     "On the five-replicate cell, ewc-block minus ewc-block-rand is within 0.05 on both axes",
     f"falsifier: above {CONTROL_FIRES:.2f} on either axis"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _arm(doc: dict, arm: str) -> dict | None:
    reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
    if not reps:
        return None
    return {"replicates": len(reps),
            "final_accuracy": statistics.fmean([r["final_accuracy"] for r in reps]),
            "mean_forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
            "accuracy": [r["final_accuracy"] for r in reps],
            "forgetting": [r["mean_forgetting"] for r in reps]}


def _paired(a: dict, b: dict, key: str) -> dict:
    xs, ys = a[key], b[key]
    n = min(len(xs), len(ys))
    dif = [xs[i] - ys[i] for i in range(n)]
    mean = statistics.fmean(dif)
    se = (statistics.stdev(dif) / n ** 0.5) if n > 1 else float("nan")
    return {"n": n, "difference": mean, "se": se, "sigma": (mean / se if se else float("nan"))}


def _draws(doc: dict) -> dict:
    ed = doc.get("env_draw") or {}
    return {k: ed.get(k) for k in DRAW_FIELDS}


def _config(doc: dict) -> dict:
    cfg = doc.get("config") or {}
    return {k: cfg.get(k) for k in CONFIG_FIELDS}


def reading(cell20: Path = CELL20, cell5: Path = CELL5, reference: Path = REFERENCE) -> dict:
    out = {"ok": True, "reason": None, "arms": {}, "contrasts": {}, "cell": {}, "control": {}, "world": {}}
    a = load(cell20)
    if not a:
        return {**out, "ok": False, "reason": f"{cell20} is absent"}
    ref = load(reference)
    if not ref:
        return {**out, "ok": False, "reason": f"{reference} is absent, so the cell cannot be placed on the card's world"}
    arms = {}
    for arm in ("naive", "ewc-block", "replay"):
        got = _arm(a, arm)
        if not got:
            return {**out, "ok": False, "reason": f"{cell20} carries no {arm} arm"}
        arms[arm] = got
    out["arms"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("accuracy", "forgetting")} for k, v in arms.items()}
    for x, y in CONTRASTS:
        out["contrasts"][f"{x}_minus_{y}"] = {"accuracy": _paired(arms[x], arms[y], "accuracy"),
                                              "forgetting": _paired(arms[x], arms[y], "forgetting")}
    same = {k: (a.get(k) == ref.get(k)) for k in SHARED}
    same.update({f"env_draw.{k}": (_draws(a).get(k) == _draws(ref).get(k)) for k in DRAW_FIELDS})
    same.update({f"config.{k}": (_config(a).get(k) == _config(ref).get(k)) for k in CONFIG_FIELDS})
    out["cell"] = {"artifact": Path(cell20).name, "reference": Path(reference).name, "same": same,
                   "replay_minus_ewc_block": out["contrasts"]["replay_minus_ewc-block"],
                   "coupling_recorded": "world_coupled" in (ref.get("env_draw") or {}),
                   "coupling_in_this_artifact": "world_coupled" in (a.get("env_draw") or {})}
    b = load(cell5)
    if b:
        pen, rnd = _arm(b, "ewc-block"), _arm(b, "ewc-block-rand")
        if pen and rnd:
            out["control"] = {"artifact": Path(cell5).name, "replicates": pen["replicates"],
                              "accuracy": _paired(pen, rnd, "accuracy"), "forgetting": _paired(pen, rnd, "forgetting")}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- an artifact the reading needs is absent"}
                for c in CLAIMS]
    same = r["cell"]["same"]
    differ = {k: v for k, v in same.items() if not v}
    thin = {k: v["replicates"] for k, v in r["arms"].items() if v["replicates"] < MIN_REPS}
    j1 = {"id": "AP1",
          "measured": f"`{r['cell']['artifact']}` carries {sorted(r['arms'])} at "
                      f"{sorted(v['replicates'] for v in r['arms'].values())} replicates, and it agrees with "
                      f"`{r['cell']['reference']}` on {len(same) - len(differ)} of {len(same)} shared fields"
                      + (f", differing on {sorted(differ)}" if differ else "")
                      + ("; the coupling is recorded in the card's world's run and not in this artifact"
                         if (r["cell"]["coupling_recorded"] and not r["cell"]["coupling_in_this_artifact"]) else ""),
          "verdict": f"MET -- the cell is carried with all three arms over {len(same)} shared fields, and its world "
                     f"predates the coupling" if (not differ and not thin) else
                     f"FALSIFIER FIRED -- {differ or {'replicates': thin}}"}
    c2 = r["contrasts"]["replay_minus_ewc-block"]["accuracy"]
    j2 = {"id": "AP2",
          "measured": f"paired over {c2['n']} seeds, replay minus ewc-block on accuracy is {c2['difference']:+.4f} "
                      f"(se {c2['se']:.4f}, {c2['sigma']:+.2f} sigma)",
          "verdict": f"MET -- the buffer beats the penalty on accuracy by {c2['difference']:+.4f} at "
                     f"{c2['sigma']:.2f} sigma" if c2["difference"] >= BIG else
                     f"FALSIFIER FIRED -- {c2['difference']:+.4f} is under the bar" if c2["difference"] < BIG_FIRES else
                     f"NULL -- {c2['difference']:+.4f}, between {BIG_FIRES:.2f} and {BIG:.2f}"}
    c3 = r["contrasts"]["replay_minus_ewc-block"]["forgetting"]
    cut = -c3["difference"]
    j3 = {"id": "AP3",
          "measured": f"the same pair on mean forgetting is {c3['difference']:+.4f}, so the buffer forgets less by "
                      f"{cut:+.4f} (se {c3['se']:.4f}, {c3['sigma']:+.2f} sigma)",
          "verdict": f"MET -- the buffer forgets less by {cut:+.4f} at {abs(c3['sigma']):.2f} sigma" if cut >= CUT else
                     f"FALSIFIER FIRED -- the cut is {cut:+.4f}" if cut < CUT_FIRES else
                     f"NULL -- the cut is {cut:+.4f}, between {CUT_FIRES:.2f} and {CUT:.2f}"}
    c4 = r["contrasts"]["ewc-block_minus_naive"]["accuracy"]
    j4 = {"id": "AP4",
          "measured": f"paired over {c4['n']} seeds, ewc-block minus naive on accuracy is {c4['difference']:+.4f} "
                      f"(se {c4['se']:.4f}, {c4['sigma']:+.2f} sigma)",
          "verdict": f"MET -- the penalty is worth {c4['difference']:+.4f} against the naive arm, which is not a gain"
                     if c4["difference"] <= PENALTY_BAR else
                     f"FALSIFIER FIRED -- the penalty gains {c4['difference']:+.4f} on this substrate"}
    ctl = r.get("control") or {}
    if not ctl:
        j5 = {"id": "AP5", "measured": f"`{CELL5.name}` is absent or carries no such pair", "verdict": "REFUSED"}
    else:
        da, df = ctl["accuracy"]["difference"], ctl["forgetting"]["difference"]
        j5 = {"id": "AP5",
              "measured": f"on {ctl['replicates']} replicates, ewc-block minus its matched random control is "
                          f"{da:+.4f} on accuracy and {df:+.4f} on forgetting",
              "verdict": f"MET -- the block basis is not distinguished from its matched control on either axis"
                         if (abs(da) <= CONTROL_BAR and abs(df) <= CONTROL_BAR) else
                         f"FALSIFIER FIRED -- {da:+.4f} and {df:+.4f} against a bar of {CONTROL_BAR:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the penalty on the card's world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'an artifact is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"   `{r['cell']['artifact']}`, twenty replicates, against `{r['cell']['reference']}`")
    print(f"\n   {'arm':>10} {'n':>3} {'final acc':>10} {'mean forgetting':>16}")
    for arm in ("naive", "ewc-block", "replay"):
        a = r["arms"][arm]
        print(f"   {arm:>10} {a['replicates']:3d} {a['final_accuracy']:10.4f} {a['mean_forgetting']:16.4f}")
    print(f"\n   the paired contrasts:")
    for name, pair in r["contrasts"].items():
        print(f"   {name:>22}: accuracy {pair['accuracy']['difference']:+.4f} "
              f"({pair['accuracy']['sigma']:+.2f} sigma), forgetting {pair['forgetting']['difference']:+.4f} "
              f"({pair['forgetting']['sigma']:+.2f} sigma)")
    ctl = r.get("control") or {}
    if ctl:
        print(f"   matched control `{ctl['artifact']}` at {ctl['replicates']} replicates: accuracy "
              f"{ctl['accuracy']['difference']:+.4f}, forgetting {ctl['forgetting']['difference']:+.4f}")
    print("\n== the registered claims, AP1-AP5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e411`, `e413` and `e414` all registered the same gap -- the penalty arms are absent from the six")
    print("    worlds' runs; this reads the cell of the card's world that carries one)")
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
