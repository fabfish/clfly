"""E378 -- the cue source at the tight step: does a better-fitted head recover the end of the window that matters.

`e377` closed a two-by-two on the **action** source at `cue@8` -- the last step `e368`'s curve says both channels
are alive on this draw -- and found the step size worth nothing there: **+0.0104 at 1.78 sigma** against **+0.1965
at 64.92 sigma** on a frozen body. So the action source at the tight end fails for the body's own reasons and no
head recovers it.

**That leaves the other source, which is the one a game can be played on.** `e374` trained the cue source at
`cue@8` and read **0.4368** -- above chance by **0.1868**, and earning the answer through the loop at **+0.1535 at
8.81 sigma** -- against **0.8399** at the wide step. So the tight end costs the cue source **0.4031**, and nothing in
the line says whether that is the margin or the head: that unit's run used the corpus's `lr = 3e-3`, and `e376`
showed the same step size leaves a head **0.1965** short at this very cell's world scale.

**This unit runs the cue source at `cue@8` with `e376`'s larger step**, which fills the fourth cell of the row and
asks the game's question directly: **is the tight end of the window playable once the head can fit?**

Five claims, registered before the new run's reading was opened.

- **Y1 -- one configuration at both comparisons.** Against `e374`'s cue-source run at this step the new run differs
  in `lr` alone; against `e372`'s cue-source run at `cue@0` every compared field agrees -- circuit, tasks and
  widths, basis, read-out, replicate count, seed stream, iteration budget, batch, the world's dimension, leak,
  coupling and mode, and the drive's source and its seven fields -- so the two steps are one configuration at two
  margins and only the cue's step is not in the compared list. **Falsifier**: any other field differing on either
  comparison.
- **Y2 -- and the licence: the channel is live at this step for this source.** `e368`'s curve reads the frozen cue
  source at `cue@8` at least **0.10** above chance with a world spread above zero. **Falsifier**: within **0.05** of
  chance or a world at rest. **REFUSED** when that artifact is absent.
- **Y3 -- and the step size helps this source too.** The new run's `naive` diagonal exceeds `e374`'s **0.4368** by
  at least **0.05**, paired over the twenty shared seeds. **Falsifier**: within **0.02**, which would say the head
  was not what the cue source was short of either. **Null**: between.
- **Y4 -- and the tight step still costs something.** The wide step's **0.8399** exceeds the new diagonal by at
  least **0.10**. **Falsifier**: within **0.05**, which would say the tight end is free once the head fits and the
  window's price is a fitting artefact at this source. **Null**: between **0.05** and **0.10** below. Y3 and Y4
  bracket the outcome the way `e374`'s pair did: the first says the head mattered, the second says the margin
  matters anyway.
- **Y5 -- and the answer is still earned.** Both arms' paired channel readings are at least **0.10** and positive at
  **2 sigma**. **Falsifier**: an arm below 0.10, at or below zero, or unresolved.

**What it can do beyond that.** With this run the row at the tight step is complete on both sources and both step
sizes: **cue** 0.4368 and X, **action** 0.2333 and 0.2437, against a probe of **0.8906** and **0.7617** on the
untrained bodies. That is the table a game has to be planned on, and it is read off four artifacts instead of being
assembled across four units with four different framings in them.

**What it cannot do.** *One lever at one value*, as in the two units before it: ten times the default is a direction
and not a dose. *One cell and one draw*: `cue@8` on this draw, whose boundary `e370` showed moves with the draw.
*And it does not say what the body did to the representation*: the trained body's weights are not in the artifact
unless a run saves them (`--save-theta`), so whether the cue source's diagonal falls because the world carries less
or because the head reads it worse is the unit this one points at, and it needs a run that keeps its body.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e371_the_game_the_agent_can_play import _sg, arm_reading, paired
from experiments.e376_the_heads_own_fitting import probe_cell

#: the run this unit made: the cue source at the tight step with the head's step size at `e376`'s
STEPPED = Path("runs/e378_earned_label_lr03_cue8_cuesource_20reps.json")
#: the same source and step at the corpus's step size, and the same source at the wide step
BASE = Path("runs/e374_earned_label_cue8_cuesource_20reps.json")
WIDE = Path("runs/e372_earned_label_cue0_cuesource_20reps.json")
CURVE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
SOURCE, STEP = "cue", 8
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COUPLING_SHA1 = "1b7d09f2b469"
REPLICATES = 20
SIGMA = 2.0
LEARNS = 0.10
FLAT = 0.05
STEPS_UP = 0.05
SAME = 0.02
STILL_COSTS = 0.10
CLAIMS = (
    ("Y1", "one configuration at both comparisons",
     "Against `e374`'s cue-source run at this step the new run differs in `lr` alone, and against `e372`'s "
     "cue-source run at the wide step it also differs in `lr` alone, that run carrying the corpus's step size, "
     "with every other compared field agreeing on both",
     "falsifier: any other field differing on either comparison"),
    ("Y2", f"and the channel is live at this step, {LEARNS:.2f} over chance",
     "`e368`'s curve reads the frozen cue source at cue@8 at least 0.10 above chance with a world spread above zero",
     "falsifier: within 0.05 of chance or a world at rest; refused when that artifact is absent"),
    ("Y3", f"and the step size helps this source too, by {STEPS_UP:.2f}",
     "The new `naive` diagonal exceeds `e374`'s 0.4368 by at least 0.05, paired over the shared seeds",
     f"falsifier: within {SAME:.2f}; null: between {SAME:.2f} and {STEPS_UP:.2f}"),
    ("Y4", f"and the tight step still costs, by {STILL_COSTS:.2f}",
     "The wide step's 0.8399 exceeds the new diagonal by at least 0.10",
     f"falsifier: within {FLAT:.2f}, which would make the window's price a fitting artefact at this source; null: "
     f"between {FLAT:.2f} and {STILL_COSTS:.2f} below"),
    ("Y5", f"and the answer is still earned, {LEARNS:.2f} at {SIGMA:.0f} sigma",
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
    if not run:
        return None
    out = dict(_facts(run))
    cfg = run.get("config") or {}
    out["lr"] = cfg.get("lr")
    out["batch"] = cfg.get("batch")
    return out


def reading(stepped_path: Path = STEPPED, base_path: Path = BASE, wide_path: Path = WIDE,
            curve: Path = CURVE) -> dict:
    stepped, base, wide = load(stepped_path), load(base_path), load(wide_path)
    runs = {"stepped": stepped, "base": base, "wide": wide}
    out = {"rows": {f"{k}_{a}": arm_reading(v, a) for k, v in runs.items() for a in ARMS},
           "facts": {k: facts_with_knobs(v) for k, v in runs.items()},
           "runs": {k: Path(v).name for k, v in (("stepped", stepped_path), ("base", base_path),
                                                 ("wide", wide_path))},
           "present": {k: v is not None for k, v in runs.items()},
           "ok": {k: v is not None and all(arm_reading(v, a).get("ok") for a in ARMS) for k, v in runs.items()},
           "expected_coupling_sha1": COUPLING_SHA1, "expected_replicates": REPLICATES,
           "probe": probe_cell(curve, SOURCE, STEP), "gain": None, "shortfall": None}
    if out["ok"]["stepped"] and out["ok"]["base"]:
        out["gain"] = paired(out["rows"][f"stepped_{NAIVE}"]["diagonal"], out["rows"][f"base_{NAIVE}"]["diagonal"])
    if out["ok"]["stepped"] and out["ok"]["wide"]:
        out["shortfall"] = out["rows"][f"wide_{NAIVE}"]["mean_diagonal"] - out["rows"][f"stepped_{NAIVE}"]["mean_diagonal"]
    return out


def judge(r: dict) -> list[dict]:
    rows, ok, present = r.get("rows") or {}, r.get("ok") or {}, r.get("present") or {}
    if not ok.get("stepped"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the stepped cue-source run is not on disk"}
                for c in CLAIMS]

    fs, fb, fw = r["facts"]["stepped"], r["facts"]["base"], r["facts"]["wide"]
    keys = ("lr", "batch") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)

    def _diff(a, b):
        if not a or not b:
            return {"missing": True}
        return {k: [a.get(k), b.get(k)] for k in keys if a.get(k) != b.get(k)}

    if not (present.get("base") and present.get("wide")):
        j1 = {"id": "Y1", "measured": f"the runs to compare against are `{r['runs']['base']}` "
                                      f"(present {bool(present.get('base'))}) and `{r['runs']['wide']}` "
                                      f"(present {bool(present.get('wide'))})",
              "verdict": "REFUSED -- a run this unit is compared with is absent"}
    else:
        vs_base, vs_wide = _diff(fs, fb), _diff(fs, fw)
        good = (list(vs_base) == ["lr"] and vs_base["lr"] == [0.03, 0.003]
                and list(vs_wide) == ["lr"] and vs_wide["lr"] == [0.03, 0.003]
                and fs.get("repeats") == REPLICATES and fs.get("world_coupling_sha1") == COUPLING_SHA1
                and fs.get("loop_cue_at") == STEP
                and rows[f"stepped_{NAIVE}"]["n"] == REPLICATES and rows[f"stepped_{REPLAY}"]["n"] == REPLICATES)
        lrs = [fb and fb.get("lr"), fs.get("lr"), fw and fw.get("lr")]
        steps = [fb and fb.get("loop_cue_at"), fs.get("loop_cue_at"), fw and fw.get("loop_cue_at")]
        j1 = {"id": "Y1", "measured": f"`{r['runs']['stepped']}` against `{r['runs']['base']}` differing {vs_base} "
                                      f"and against `{r['runs']['wide']}` differing {vs_wide}; learning rates "
                                      f"{lrs}, cue steps {steps}, iterations {fs.get('iters')}, coupling "
                                      f"{fs.get('world_coupling_sha1')}",
              "verdict": "MET -- one configuration at both comparisons" if good else
              f"FALSIFIER FIRED -- against the base run {vs_base}, against the wide one {vs_wide}"}

    pz = r.get("probe")
    if not pz:
        j2 = {"id": "Y2", "measured": "the curve has no cell for this step and source",
              "verdict": "REFUSED -- the artifact this unit's licence comes from is absent"}
    else:
        above = pz["accuracy"] - 0.25
        j2 = {"id": "Y2", "measured": f"`{pz['artifact']}` reads {SOURCE}@{STEP} at {pz['accuracy']:.4f}, "
                                      f"{above:+.4f} over a chance of 0.25, on a world with spread "
                                      f"{pz['world_sd']:.4f}",
              "verdict": f"MET -- the channel is live, {above:+.4f} over chance" if
              above >= LEARNS and pz["world_sd"] > 0.0 else
              f"FALSIFIER FIRED -- {above:+.4f} over chance on a world with spread {pz['world_sd']:.4f}"}

    naive = rows[f"stepped_{NAIVE}"]
    gain = r.get("gain") or {"delta": None}
    if gain.get("delta") is None:
        j3 = {"id": "Y3", "measured": "the paired comparison was not computable",
              "verdict": "REFUSED -- the two runs do not pair"}
    else:
        j3 = {"id": "Y3", "measured": f"the cue source with the step size at {fs.get('lr')} reads "
                                      f"{naive['mean_diagonal']:.4f} against {rows[f'base_{NAIVE}']['mean_diagonal']:.4f} "
                                      f"at the corpus's {fb.get('lr')}, so the larger step is worth "
                                      f"{gain['delta']:+.4f} on a sem of {gain['sem']:.4f} "
                                      f"({_sg(gain['sigma'])} sigma) over {gain['n']} paired replicates",
              "verdict": f"MET -- the step size helps this source too, by {gain['delta']:+.4f}" if
              gain["delta"] >= STEPS_UP else
              f"FALSIFIER FIRED -- the larger step is worth only {gain['delta']:+.4f}: the head was not what this "
              f"source was short of either" if gain["delta"] < SAME else
              f"NULL -- {gain['delta']:+.4f}, between {SAME:.2f} and {STEPS_UP:.2f}"}

    short = r.get("shortfall")
    if short is None:
        j4 = {"id": "Y4", "measured": "the wide-step run or the new diagonal is not available",
              "verdict": "REFUSED -- the comparison this claim makes is not computable"}
    else:
        j4 = {"id": "Y4", "measured": f"the wide step reads {rows[f'wide_{NAIVE}']['mean_diagonal']:.4f} and the "
                                      f"tight one {naive['mean_diagonal']:.4f}, so the margin still costs "
                                      f"{short:+.4f}",
              "verdict": f"MET -- the tight step still costs {short:.4f}" if short >= STILL_COSTS else
              f"FALSIFIER FIRED -- within {FLAT:.2f} of the wide step, {short:+.4f}: the window's price is a fitting "
              f"artefact at this source" if short <= FLAT else
              f"NULL -- short by {short:.4f}, between {FLAT:.2f} and {STILL_COSTS:.2f}"}

    detail = "; ".join(f"`{a}` {rows[f'stepped_{a}']['paired']['delta']:+.4f} at "
                       f"{_sg(rows[f'stepped_{a}']['paired']['sigma'])} sigma" for a in ARMS)
    weak = [a for a in ARMS if not (rows[f"stepped_{a}"]["paired"]["delta"] is not None
                                    and rows[f"stepped_{a}"]["paired"]["delta"] >= LEARNS
                                    and (rows[f"stepped_{a}"]["paired"]["sigma"] or 0) >= SIGMA)]
    j5 = {"id": "Y5", "measured": f"the stepped cue-source run's paired channel readings over {naive['n']} "
                                  f"replicates: {detail}",
          "verdict": "MET -- the answer is still earned, in both arms" if not weak else
          f"FALSIFIER FIRED -- the answer is not earned in {weak}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not (r.get("ok") or {}).get("stepped"):
        print("== the cue source at the tight step ==\n   REFUSED -- the stepped cue-source run is not on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the cue source at the tight step ==")
    print(f"   the source a game can be played on at cue@{STEP}, at two step sizes, against the same source at the "
          f"wide step")
    print(f"\n   {'run':>8} {'lr':>6} {'cue at':>7} {'arm':>7} {'diagonal':>9} {'forget':>8} {'channel':>9} "
          f"{'sigma':>6}")
    for key, row in r["rows"].items():
        which = key.split("_", 1)[0]
        print(f"   {which:>8} {str(r['facts'][which].get('lr')):>6} {str(r['facts'][which].get('loop_cue_at')):>7} "
              f"{row['arm']:>7} {row['mean_diagonal']:9.4f} {row['mean_forgetting']:8.4f} "
              f"{row['paired']['delta']:+9.4f} {_sg(row['paired']['sigma']):>6}")
    if r.get("probe"):
        print(f"   the closed-form probe on the untrained body in `{r['probe']['artifact']}` reads "
              f"{r['probe']['accuracy']:.4f} on a world with spread {r['probe']['world_sd']:.4f}")

    print("\n== the registered claims, Y1-Y5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e377` showed the action source at this step is lost to the body and not to the head; the cue")
    print("    source is the one a game can use, and this asks whether its own loss at the same step is the head)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stepped", type=Path, default=STEPPED)
    ap.add_argument("--base", type=Path, default=BASE)
    ap.add_argument("--wide", type=Path, default=WIDE)
    ap.add_argument("--curve", type=Path, default=CURVE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(stepped_path=args.stepped, base_path=args.base, wide_path=args.wide, curve=args.curve)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
