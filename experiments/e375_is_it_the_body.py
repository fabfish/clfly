"""E375 -- is it the body: the same step with the recurrent weights frozen, so only the head can move.

`e374` trained both drive sources at `cue@8` -- the last step `e368`'s curve says both channels are alive on this
draw -- and found a reversal it could not explain: the **frozen** action source's world reads **0.7617** there, and
the **plastic** body trained on the same cell reads **0.2333**, which is chance. It reported the candidate account
rather than claiming it: *"at `cue@8` the world's last update is the only one whose drive can carry the cue, so the
body must hold the symbol in its action population at exactly one time step and the gradient reaches it through
exactly one step, while a probe fitted on the frozen population exploits a representation that is already there and
that nothing in the trainer's objective asks to survive."*

**That account makes a prediction this unit can test with one run.** If the readable representation is destroyed by
the body's own training, then **freezing the body** -- the corpus's own diagnostic, `--frozen-body`, which stops the
gradient at the head and leaves the recurrent weights at their connectome initialisation -- should recover what the
probe read, with the same optimizer, the same iteration budget and the same twenty seeds. If instead the frozen body
also reads chance, then the representation a closed-form probe exploits is not reachable by a trained head either,
and the account is wrong in the direction of the probe's own advantage.

Five claims, registered before the new run's reading was opened.

- **U1 -- one configuration except the body.** The frozen-body run and `e374`'s plastic run at the same step and the
  same drive source agree on every shared field -- circuit, tasks and widths, basis, read-out, replicate count, seed
  stream, iteration budget, the world's dimension, leak, coupling and mode, the cue's step and the source's seven
  fields -- differing in `frozen_body` alone. **Falsifier**: any other field differing.
- **U2 -- and the licence: the world is live at this step, as `e368` recorded.** That artifact's curve reads the
  frozen action source at `cue@8` at least **0.10** above chance with a world spread above zero. **Falsifier**:
  within **0.05** of chance or a world at rest. **REFUSED** when that artifact is absent.
- **U3 -- and a frozen body still trains.** The frozen-body run's `naive` diagonal is at least **0.10** above
  chance. **Falsifier**: within **0.05** of chance, which would say a trained head cannot use the representation a
  least-squares probe reads off the same frozen body, and would refute the account rather than support it.
- **U4 -- and it is the body's own training that loses it.** The frozen-body diagonal exceeds `e374`'s plastic one
  (**0.2333**) by at least **0.10**, paired over the twenty shared seeds. **Falsifier**: within **0.05**, which
  would say the body's plasticity is not what the reading turns on. **Null**: between. *This is the claim the unit
  exists for.*
- **U5 -- and the answer is earned with the body frozen.** Both arms' paired channel readings are at least **0.10**
  and positive at **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved. Without this the
  frozen body could be reading the cue through the network rather than through the loop the task is about.

**What it can do beyond that.** The three numbers the account needed -- the probe on the frozen body (**0.7617**,
`e368`), the plastic body trained (**0.2333**, `e374`) and this run -- separate "the representation is not there"
from "the representation was there and training removed it", and only the second supports the account. The probe's
own reading is reported beside the frozen body's trained one and not claimed against it, since a closed-form probe
and a trained head are different instruments fitted on the same body.

**What it cannot do.** *One cell and one draw*: `cue@8` on this draw, so nothing here says whether a frozen body
recovers the probe at other steps, and `e370` showed the boundary moves with the draw. *And freezing is a
diagnostic*: `--frozen-body` stops the gradient at the head, so a frozen-body run is not a method but a question
about what the plastic one would have done with the same budget -- and a positive answer here is evidence that the
body's training matters, not a demonstration of which representation the probe is using. *And the probe is not
paired*: its 0.7617 is one roll of 512 examples against twenty replicates.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e371_the_game_the_agent_can_play import _sg, arm_reading, paired

#: the run this unit made: the same cell as `e374`'s action-source run, with the recurrent weights frozen
FROZEN_BODY = Path("runs/e375_earned_label_frozenbody_cue8_actionsource_20reps.json")
#: `e374`'s plastic run at the same step and source, and `e368`'s curve, which holds the probe's own reading
PLASTIC = Path("runs/e374_earned_label_cue8_actionsource_20reps.json")
CURVE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
SOURCE, STEP = "action", 8
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COUPLING_SHA1 = "5326f4a0edb4"
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
RECOVERS = 0.10
CARRIES = 0.10
CLAIMS = (
    ("U1", "one configuration except the body",
     "The frozen-body run and the plastic run at the same step and source agree on every shared field, differing in "
     "`frozen_body` alone",
     "falsifier: any other field differing"),
    ("U2", f"and the world is live at this step, {LEARNS:.2f} over chance",
     "`e368`'s curve reads the frozen action source at cue@8 at least 0.10 above chance with a world spread above "
     "zero",
     "falsifier: within 0.05 of chance or a world at rest; refused when that artifact is absent"),
    ("U3", f"and a frozen body still trains, {LEARNS:.2f} over chance",
     "The frozen-body run's `naive` diagonal is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("U4", f"and it is the body's own training that loses it, by {RECOVERS:.2f}",
     "The frozen-body diagonal exceeds the plastic one by at least 0.10, paired over the shared seeds",
     f"falsifier: within {FLAT:.2f}; null: between {FLAT:.2f} and {RECOVERS:.2f}"),
    ("U5", f"and the answer is earned with the body frozen, {CARRIES:.2f} at {SIGMA:.0f} sigma",
     "Both arms' paired channel readings are at least 0.10 and positive at 2 sigma",
     "falsifier: an arm below 0.10, at or below zero, or unresolved"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def facts_with_body(run: dict | None) -> dict | None:
    """`e367`'s facts plus the two controllability fields, which is what this unit's manipulation moves."""
    if not run:
        return None
    out = dict(_facts(run))
    cfg = run.get("config") or {}
    out["frozen_body"] = bool(cfg.get("frozen_body"))
    out["frozen_bias"] = bool(cfg.get("frozen_bias"))
    return out


def probe_cell(path: Path = CURVE, source: str = SOURCE, step: int = STEP):
    doc = load(path)
    if not doc:
        return None
    cell = (doc.get("cells") or {}).get(f"{source}@{step}")
    if not cell:
        return None
    return {"accuracy": float(cell["accuracy"]), "world_sd": float(cell["world_sd"]),
            "trial_range": float(cell.get("trial_range", 0.0)), "artifact": Path(path).name}


def reading(frozen_path: Path = FROZEN_BODY, plastic_path: Path = PLASTIC, curve: Path = CURVE) -> dict:
    frozen, plastic = load(frozen_path), load(plastic_path)
    out = {"rows": {**{f"frozen_{a}": arm_reading(frozen, a) for a in ARMS},
                    **{f"plastic_{a}": arm_reading(plastic, a) for a in ARMS}},
           "facts": {"frozen": facts_with_body(frozen), "plastic": facts_with_body(plastic)},
           "runs": {"frozen": Path(frozen_path).name, "plastic": Path(plastic_path).name},
           "present": {"frozen": frozen is not None, "plastic": plastic is not None},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES,
           "probe": probe_cell(curve), "recovery": None}
    out["ok"] = {"frozen": frozen is not None and all(out["rows"][f"frozen_{a}"].get("ok") for a in ARMS),
                 "plastic": plastic is not None and all(out["rows"][f"plastic_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["frozen"] and out["ok"]["plastic"]:
        out["recovery"] = paired(out["rows"][f"frozen_{NAIVE}"]["diagonal"], out["rows"][f"plastic_{NAIVE}"]["diagonal"])
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("frozen"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the frozen-body run is not on disk"}
                for c in CLAIMS]

    ff, fp = r["facts"]["frozen"], r["facts"]["plastic"]
    if not (r.get("present") or {}).get("plastic"):
        j1 = {"id": "U1", "measured": f"`{r['runs']['plastic']}` is absent, so there is no plastic run to compare "
                                      f"against",
              "verdict": "REFUSED -- the run this unit controls against is absent"}
    else:
        keys = ("frozen_bias", "frozen_body") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
        differ = {k: [ff.get(k), fp.get(k)] for k in keys if ff.get(k) != fp.get(k)}
        good = (list(differ) == ["frozen_body"] and differ.get("frozen_body") == [True, False]
                and ff.get("world_coupling_sha1") == COUPLING_SHA1 and ff.get("loop_cue_at") == STEP
                and ff.get("repeats") == REPLICATES
                and rows[f"frozen_{NAIVE}"]["n"] == REPLICATES and rows[f"frozen_{REPLAY}"]["n"] == REPLICATES)
        j1 = {"id": "U1", "measured": f"`{r['runs']['frozen']}` against `{r['runs']['plastic']}`: cue step "
                                      f"{ff.get('loop_cue_at')}, iterations {ff.get('iters')}, circuit "
                                      f"{ff.get('circuit_size')}, {ff.get('repeats')} replicates at seed0 "
                                      f"{ff.get('seed0')}, basis {ff.get('basis')}, coupling "
                                      f"{ff.get('world_coupling_sha1')}, fields differing {differ}",
              "verdict": "MET -- one configuration except the body" if good else
              f"FALSIFIER FIRED -- fields differ beyond `frozen_body`: {differ}"}

    pz = r.get("probe")
    if not pz:
        j2 = {"id": "U2", "measured": "the curve has no cell for this step",
              "verdict": "REFUSED -- the artifact this unit's licence comes from is absent"}
    else:
        above = pz["accuracy"] - 0.25
        j2 = {"id": "U2", "measured": f"`{pz['artifact']}` reads {SOURCE}@{STEP} at {pz['accuracy']:.4f}, "
                                      f"{above:+.4f} over a chance of 0.25, on a world with spread "
                                      f"{pz['world_sd']:.4f}",
              "verdict": f"MET -- the world is live at this step, {above:+.4f} over chance" if
              above >= LEARNS and pz["world_sd"] > 0.0 else
              f"FALSIFIER FIRED -- {above:+.4f} over chance on a world with spread {pz['world_sd']:.4f}"}

    naive = rows[f"frozen_{NAIVE}"]
    learned = naive["mean_diagonal"] - naive["chance"]
    j3 = {"id": "U3", "measured": f"the frozen-body `{NAIVE}` diagonal is {naive['mean_diagonal']:.4f} against a "
                                  f"chance of {naive['chance']:.2f}, {learned:+.4f} above it, over {naive['n']} "
                                  f"replicates",
          "verdict": f"MET -- a frozen body still trains, {learned:+.4f} over chance" if learned >= LEARNS else
          f"FALSIFIER FIRED -- only {learned:+.4f} above chance: a trained head cannot use what a probe reads off "
          f"the same frozen body, which refutes the account" if learned < FLAT else
          f"NULL -- {learned:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    rec = r.get("recovery") or {"delta": None}
    if rec.get("delta") is None:
        j4 = {"id": "U4", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the two runs do not pair"}
    else:
        j4 = {"id": "U4", "measured": f"the frozen body reads {naive['mean_diagonal']:.4f} and the plastic body "
                                      f"{rows[f'plastic_{NAIVE}']['mean_diagonal']:.4f}, so freezing the recurrent "
                                      f"weights is worth {rec['delta']:+.4f} on a sem of {rec['sem']:.4f} "
                                      f"({_sg(rec['sigma'])} sigma) over {rec['n']} paired replicates",
              "verdict": f"MET -- the body's own training is what loses the reading, by {rec['delta']:+.4f}" if
              rec["delta"] >= RECOVERS else
              f"FALSIFIER FIRED -- freezing the body is worth only {rec['delta']:+.4f}: plasticity is not what the "
              f"reading turns on" if rec["delta"] < FLAT else
              f"NULL -- {rec['delta']:+.4f}, between {FLAT:.2f} and {RECOVERS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'frozen_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'frozen_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"frozen_{a}"]["paired"]["delta"] is not None
                                    and rows[f"frozen_{a}"]["paired"]["delta"] >= CARRIES
                                    and (rows[f"frozen_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j5 = {"id": "U5", "measured": f"the frozen body's paired channel readings over {naive['n']} replicates: {detail}",
          "verdict": "MET -- the answer is earned with the body frozen, in both arms" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not (r.get("ok") or {}).get("frozen"):
        print("== is it the body ==\n   REFUSED -- the frozen-body run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== is it the body ==")
    print(f"   `{r['runs']['frozen']}` against `{r['runs']['plastic']}`, the same cell with the recurrent weights "
          f"frozen and left to the head")
    print(f"\n   {'body':>8} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for key, row in r["rows"].items():
        print(f"   {key.split('_', 1)[0]:>8} {row['arm']:>7} {row['mean_final']:8.4f} {row['mean_diagonal']:9.4f} "
              f"{row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")
    if r.get("probe"):
        print(f"   the probe on the frozen body in `{r['probe']['artifact']}` reads {r['probe']['accuracy']:.4f} on "
              f"a world with spread {r['probe']['world_sd']:.4f} (reported)")

    print("\n== the registered claims, U1-U5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e374` found the frozen action source's world readable at 0.7617 where the plastic body trained to")
    print("    chance, and named the candidate account; this freezes the body and asks whether it holds)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frozen", type=Path, default=FROZEN_BODY)
    ap.add_argument("--plastic", type=Path, default=PLASTIC)
    ap.add_argument("--curve", type=Path, default=CURVE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(frozen_path=args.frozen, plastic_path=args.plastic, curve=args.curve)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
