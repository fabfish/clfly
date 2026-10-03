"""E376 -- the head's own fitting: the same frozen body with a larger step size for the head.

`e375` froze the recurrent weights at `cue@8` and found the body's own training is what loses the reading
(**+0.2156 at 229.59 sigma**). It left the split it could not explain: a trained head on the frozen body reads
**0.4490** where a closed-form least-squares probe on the **same** frozen body reads **0.7617**, so of the **0.5284**
gap between the probe and the plastic body, **0.3127** is the head losing to a probe on features the two of them
read identically. It named the unit: *"whether a trained head can be made to match a closed-form probe on a frozen
body -- more iterations, a different head or a different optimizer."*

**The corpus's own head is a linear layer on exactly the probe's features.** With `--readout-from-world` the runner
sets every task's `readout_neurons` to `arange(loop_world_dims)`, so the head reads the world's eight numbers and
the probe is fitted on the same eight; with the body frozen neither can differ in what it is looking at. What
differs is how the eight-number map is fitted: the probe is one ridge least-squares solve, and the head is
`Linear(8, 4)` under **Adam at `lr = 3e-3` for 500 iterations** on 96 examples.

**And that is a step-size question the scale of this world makes sharp.** Adam moves a coordinate by about `lr` per
step, so 500 steps at `3e-3` can move the weights about **1.5**, and a logit on features of the size this world puts
out at `cue@8` -- a spread of **0.0478**, against **0.2029** at `cue@0` -- is then of order **0.2**. A head that
cannot leave the neighbourhood of its initialisation cannot be confident, and this unit moves the step size by ten
and asks whether the gap is where the steps were.

Five claims, registered before the new run's reading was opened.

- **V1 -- one configuration except the learning rate.** The new run agrees with `e375`'s on every shared field --
  circuit, tasks and widths, basis, read-out, replicate count, seed stream, iteration budget, the world's dimension,
  leak, coupling and mode, the cue's step, the drive's source and its seven fields, and both controllability
  flags -- differing in `lr` alone. **Falsifier**: any other field differing.
- **V2 -- and the licence: the world is live at this step, as `e368` recorded.** That artifact's curve reads the
  frozen action source at `cue@8` at least **0.10** above chance with a world spread above zero. **Falsifier**:
  within **0.05** of chance or a world at rest. **REFUSED** when that artifact is absent.
- **V3 -- and the head was short of steps.** The new run's frozen-body `naive` diagonal exceeds `e375`'s **0.4490**
  by at least **0.10**, paired over the twenty shared seeds. **Falsifier**: within **0.02**, which would say the
  step size is not what the head was short of. **Null**: between **0.02** and **0.10**.
- **V4 -- and it still does not reach the closed form.** The new diagonal remains at least **0.05** below the
  probe's **0.7617**. **Falsifier**: within **0.05** of it, which would say the corpus's head reaches a
  least-squares fit on identical features once its step size is right, and that the 0.3127 was an artefact of the
  default learning rate. **Null**: between **0.02** and **0.05** below. *This is the claim the unit exists for.*
- **V5 -- and the answer is still earned.** Both arms' paired channel readings are at least **0.10** and positive at
  **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved. A head that has simply been
  sharpened into reading a static body would show up here.

**What it can do beyond that.** The probe's reading on the **runner's own split** -- 96 train and 48 test, which is
what the head is trained and read on -- is reported beside `e368`'s cell, so the comparison is against a closed-form
fit at the same resolution and not only against the wider one, and if V4 fires then the corpus's *"training reads
less than a probe"* line acquires a step-size caveat that reaches back past this window.

**What it cannot do.** *One lever and one value of it*: ten times the default is a direction and not a dose, so a
resolved V3 says the step size matters and not where it stops mattering. *One cell and one draw*: `cue@8` on this
draw, whose world's spread is what makes the scale argument bite, so `cue@0` -- where the spread is four times
larger and the same 500 steps already reach above the probe -- is not measured here. *And it is the corpus's own
head*: a different parameterisation, a bias-only warm start or a closed-form read-out would be different
interventions, and this unit turns the one knob the runner exposes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e371_the_game_the_agent_can_play import _sg, arm_reading, paired

#: the run this unit made: the frozen body at `cue@8` with the head's step size ten times the corpus default
STEPPED = Path("runs/e376_earned_label_frozenbody_lr03_cue8_actionsource_20reps.json")
#: `e375`'s run at the corpus's own learning rate, and `e368`'s curve, which holds the probe's reading
BASE = Path("runs/e375_earned_label_frozenbody_cue8_actionsource_20reps.json")
CURVE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
SOURCE, STEP = "action", 8
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COUPLING_SHA1 = "5326f4a0edb4"
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
STEPS_UP = 0.10
SAME = 0.02
REACHES = 0.05
CLAIMS = (
    ("V1", "one configuration except the learning rate",
     "The new run and `e375`'s agree on every shared field -- including the iteration budget, the controllability "
     "flags and the drive's source and its seven fields -- differing in `lr` alone",
     "falsifier: any other field differing"),
    ("V2", f"and the world is live at this step, {LEARNS:.2f} over chance",
     "`e368`'s curve reads the frozen action source at cue@8 at least 0.10 above chance with a world spread above "
     "zero",
     "falsifier: within 0.05 of chance or a world at rest; refused when that artifact is absent"),
    ("V3", f"and the head was short of steps, by {STEPS_UP:.2f}",
     "The new frozen-body `naive` diagonal exceeds `e375`'s 0.4490 by at least 0.10, paired over the shared seeds",
     f"falsifier: within {SAME:.2f}; null: between {SAME:.2f} and {STEPS_UP:.2f}"),
    ("V4", f"and it still does not reach the closed form, by {REACHES:.2f} below",
     "The new diagonal remains at least 0.05 below the probe's 0.7617",
     f"falsifier: within {REACHES:.2f} of it, which would make the 0.3127 a step-size artefact; null: between "
     f"{SAME:.2f} and {REACHES:.2f} below"),
    ("V5", f"and the answer is still earned, {LEARNS:.2f} at {SIGMA:.0f} sigma",
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


def facts_with_knobs(run: dict | None) -> dict | None:
    """`e367`'s facts plus the three knobs this unit's manipulation has to hold or move."""
    if not run:
        return None
    out = dict(_facts(run))
    cfg = run.get("config") or {}
    out["lr"] = cfg.get("lr")
    out["batch"] = cfg.get("batch")
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
            "artifact": Path(path).name}


def reading(stepped_path: Path = STEPPED, base_path: Path = BASE, curve: Path = CURVE) -> dict:
    stepped, base = load(stepped_path), load(base_path)
    out = {"rows": {**{f"stepped_{a}": arm_reading(stepped, a) for a in ARMS},
                    **{f"base_{a}": arm_reading(base, a) for a in ARMS}},
           "facts": {"stepped": facts_with_knobs(stepped), "base": facts_with_knobs(base)},
           "runs": {"stepped": Path(stepped_path).name, "base": Path(base_path).name},
           "present": {"stepped": stepped is not None, "base": base is not None},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES,
           "probe": probe_cell(curve), "gain": None, "shortfall": None}
    out["ok"] = {"stepped": stepped is not None and all(out["rows"][f"stepped_{a}"].get("ok") for a in ARMS),
                 "base": base is not None and all(out["rows"][f"base_{a}"].get("ok") for a in ARMS)}
    if out["ok"]["stepped"] and out["ok"]["base"]:
        out["gain"] = paired(out["rows"][f"stepped_{NAIVE}"]["diagonal"], out["rows"][f"base_{NAIVE}"]["diagonal"])
    if out["ok"]["stepped"] and out["probe"]:
        out["shortfall"] = out["probe"]["accuracy"] - out["rows"][f"stepped_{NAIVE}"]["mean_diagonal"]
    return out


def judge(r: dict) -> list[dict]:
    rows, ok = r.get("rows") or {}, r.get("ok") or {}
    if not ok.get("stepped"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the stepped-head run is not on disk"}
                for c in CLAIMS]

    fs, fb = r["facts"]["stepped"], r["facts"]["base"]
    if not (r.get("present") or {}).get("base"):
        j1 = {"id": "V1", "measured": f"`{r['runs']['base']}` is absent, so there is no corpus-default run to "
                                      f"compare against",
              "verdict": "REFUSED -- the run this unit controls against is absent"}
    else:
        keys = ("lr", "batch", "frozen_body", "frozen_bias") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
        differ = {k: [fs.get(k), fb.get(k)] for k in keys if fs.get(k) != fb.get(k)}
        good = (list(differ) == ["lr"] and differ.get("lr") == [0.03, 0.003]
                and fs.get("frozen_body") is True and fs.get("repeats") == REPLICATES
                and fs.get("world_coupling_sha1") == COUPLING_SHA1 and fs.get("loop_cue_at") == STEP
                and rows[f"stepped_{NAIVE}"]["n"] == REPLICATES and rows[f"stepped_{REPLAY}"]["n"] == REPLICATES)
        j1 = {"id": "V1", "measured": f"`{r['runs']['stepped']}` against `{r['runs']['base']}`: learning rate "
                                      f"{fs.get('lr')} against {fb.get('lr')}, iterations {fs.get('iters')}, "
                                      f"batch {fs.get('batch')}, body frozen {fs.get('frozen_body')}, coupling "
                                      f"{fs.get('world_coupling_sha1')}, cue step {fs.get('loop_cue_at')}, fields "
                                      f"differing {differ}",
              "verdict": "MET -- one configuration except the learning rate" if good else
              f"FALSIFIER FIRED -- fields differ beyond `lr`: {differ}"}

    pz = r.get("probe")
    if not pz:
        j2 = {"id": "V2", "measured": "the curve has no cell for this step",
              "verdict": "REFUSED -- the artifact this unit's licence comes from is absent"}
    else:
        above = pz["accuracy"] - 0.25
        j2 = {"id": "V2", "measured": f"`{pz['artifact']}` reads {SOURCE}@{STEP} at {pz['accuracy']:.4f}, "
                                      f"{above:+.4f} over a chance of 0.25, on a world with spread "
                                      f"{pz['world_sd']:.4f}",
              "verdict": f"MET -- the world is live at this step, {above:+.4f} over chance" if
              above >= LEARNS and pz["world_sd"] > 0.0 else
              f"FALSIFIER FIRED -- {above:+.4f} over chance on a world with spread {pz['world_sd']:.4f}"}

    gain = r.get("gain") or {"delta": None}
    naive = rows[f"stepped_{NAIVE}"]
    if gain.get("delta") is None:
        j3 = {"id": "V3", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the two runs do not pair"}
    else:
        j3 = {"id": "V3", "measured": f"with the step size at {r['facts']['stepped'].get('lr')} the frozen body "
                                      f"reads {naive['mean_diagonal']:.4f} against {rows[f'base_{NAIVE}']['mean_diagonal']:.4f} "
                                      f"at the corpus's {r['facts']['base'].get('lr')}, so the larger step is worth "
                                      f"{gain['delta']:+.4f} on a sem of {gain['sem']:.4f} "
                                      f"({_sg(gain['sigma'])} sigma) over {gain['n']} paired replicates",
              "verdict": f"MET -- the head was short of steps, by {gain['delta']:+.4f}" if
              gain["delta"] >= STEPS_UP else
              f"FALSIFIER FIRED -- the larger step is worth only {gain['delta']:+.4f}: the step size is not what the "
              f"head was short of" if gain["delta"] < SAME else
              f"NULL -- {gain['delta']:+.4f}, between {SAME:.2f} and {STEPS_UP:.2f}"}

    short = r.get("shortfall")
    if short is None:
        j4 = {"id": "V4", "measured": "the probe's reading or the new diagonal is not available",
              "verdict": "REFUSED -- the comparison this claim makes is not computable"}
    else:
        j4 = {"id": "V4", "measured": f"the probe reads {r['probe']['accuracy']:.4f} and the stepped head "
                                      f"{naive['mean_diagonal']:.4f}, so the head is still short by "
                                      f"{short:+.4f}",
              "verdict": f"MET -- the head still does not reach the closed form, by {short:.4f}" if short >= REACHES
              else f"FALSIFIER FIRED -- the head reaches the closed form within {REACHES:.2f}, so the 0.3127 was a "
                   f"step-size artefact" if short <= SAME else
              f"NULL -- short by {short:.4f}, between {SAME:.2f} and {REACHES:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'stepped_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'stepped_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"stepped_{a}"]["paired"]["delta"] is not None
                                    and rows[f"stepped_{a}"]["paired"]["delta"] >= LEARNS
                                    and (rows[f"stepped_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j5 = {"id": "V5", "measured": f"the stepped head's paired channel readings over {naive['n']} replicates: "
                                  f"{detail}",
          "verdict": "MET -- the answer is still earned, in both arms" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not (r.get("ok") or {}).get("stepped"):
        print("== the head's own fitting ==\n   REFUSED -- the stepped-head run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the head's own fitting ==")
    print(f"   `{r['runs']['stepped']}` against `{r['runs']['base']}`, the same frozen body at the same cell with "
          f"the head's step size the only difference")
    print(f"\n   {'run':>8} {'lr':>6} {'arm':>7} {'final':>8} {'diagonal':>9} {'forget':>8} {'channel':>9} "
          f"{'sigma':>6}")
    for key, row in r["rows"].items():
        which = key.split("_", 1)[0]
        print(f"   {which:>8} {str(r['facts'][which].get('lr')):>6} {row['arm']:>7} {row['mean_final']:8.4f} "
              f"{row['mean_diagonal']:9.4f} {row['mean_forgetting']:8.4f} {row['paired']['delta']:+9.4f} "
              f"{_sg(row['paired']['sigma']):>6}")
    if r.get("probe"):
        print(f"   the closed-form probe on the same frozen body in `{r['probe']['artifact']}` reads "
              f"{r['probe']['accuracy']:.4f} on a world with spread {r['probe']['world_sd']:.4f}")

    print("\n== the registered claims, V1-V5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e375` froze the body and left the head short of a closed-form probe by 0.3127 on features the two")
    print("    read identically; this moves the corpus's default learning rate and asks where the steps were)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stepped", type=Path, default=STEPPED)
    ap.add_argument("--base", type=Path, default=BASE)
    ap.add_argument("--curve", type=Path, default=CURVE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(stepped_path=args.stepped, base_path=args.base, curve=args.curve)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
