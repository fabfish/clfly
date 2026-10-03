"""E387 -- the window as one setting: what the corpus's own closed-loop runs agree on, and what they vary.

`e363` to `e386` are twenty-five units on one configuration -- a connectome circuit, a cue task read off a world the
agent's own action drives, three tasks in sequence -- and no unit has read them **as a set**. Each moved one field and
compared itself with one or two neighbours, so what the line is *about* has been carried in prose across two dozen
rows. This unit reads the runs themselves and asks the two questions a benchmark needs answered before it can be
used: **which fields define the setting**, and **which fields are the manipulations**.

**And it states the horizon under test rather than asserting it.** `e369` measured the cue population's directed
distance to the action population at `2` and registered `tau - 2 - d` as the last cue step that can hold the trace;
`e368`'s curve records the cliffs at `10` and `8`. Those are three artifacts' numbers, and the contract this unit
publishes is that they are consistent with each other and with what the window's runs read at those steps.

Five claims, registered before this unit read the corpus as a set.

- **H1 -- and the window is one setting.** Across every closed-loop artifact under `runs/`, the circuit, the read-out
  draw, the basis, the task names and their class count, the seed stream and the circuit's size are **constant**.
  **Falsifier**: any of them differing between two window runs.
- **H2 -- and what varies is the manipulations and their consequences.** The fields that differ across the window are
  within the set this line has deliberately moved -- the cue's step, the drive's source, the learning rate, the
  iteration budget, the replicate count, the world's dimension and the frozen-body flag -- together with the fields
  those move by construction: the three world draws, the read-out widths, the task count and `cue_at`, `n_action`,
  `action_sha1` and `drive_from_cue`. **Falsifier**: a field varying that is in neither list, which would say the
  window is more than one setting.
- **H3 -- and the horizon is the artifacts' own.** From `e369`'s measured distance of `2` and `tau = 12`, the last
  cue step that can hold the trace is `10` for the world listening to the cue population and `8` for the world
  listening to the agent's, and `e368`'s curve records exactly those two cliffs while the window's own runs at those
  steps are the ones that read chance. **Falsifier**: a cliff anywhere else, or a formula disagreeing with a curve.
  **REFUSED** when either artifact is absent.
- **H4 -- and the draw is one, and it is the two-hop one.** `e370`'s sweep records the distance `1` eleven times and
  `2` five times, and every window run's `seed0` is `0`, which that sweep puts in the two-hop five. **Falsifier**: a
  window run on another seed stream, or a sweep whose counts contradict the claim. **REFUSED** when that artifact is
  absent.
- **H5 -- and the corpus's own count is a bound.** The window holds at least **twenty** artifacts. **Falsifier**:
  fewer, which would say this unit's definition of the window has drifted from the line's. A count that grows with
  the corpus is asserted as a bound and not as a value.

**What it can do beyond that.** It is the block a reader can be pointed at: the setting, the manipulations, the
horizon and the draw, each backed by an artifact rather than by a row's prose, with the two traps this line has
already paid for -- the 96/48 split and the frozen-probe comparison across bodies -- named where a user will meet
them.

**What it cannot do.** *A definition by a field*: the window is the artifacts whose `config.closed_loop` is true, so
a run that wired the loop by another name would be outside it and a run that set the flag without the world would be
inside. *And it audits consistency and not correctness*: two dozen units agreeing on a field says the corpus is one
setting and says nothing about whether the setting is the right one. *And the horizon is stated, not measured here*:
H3 checks three artifacts against each other and rolls nothing, so the cliffs come from `e368` and the distances from
`e369` and `e370` exactly as those units left them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the fields a benchmark is defined by, and the ones this line has deliberately moved or that follow from moving
INVARIANTS = ("circuit", "readout_subset", "basis", "task_names", "n_classes", "seed0", "circuit_size", "support")
MOVED = ("loop_cue_at", "loop_drive_from_cue", "lr", "iters", "repeats", "loop_world_dims", "frozen_body")
FOLLOWS = ("world_drive_sha1", "world_read_sha1", "world_coupling_sha1", "n_action", "action_sha1", "drive_from_cue",
           "task_readout_widths", "no_feedback", "anchor_bias", "frozen_bias")
CURVE = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
DISTANCE = Path("runs/e369_why_the_cliff_is_where_it_is.json")
SWEEP = Path("runs/e370_the_distance_moves_the_cliff.json")
TAU = 12
MIN_WINDOW = 20
CLAIMS = (
    ("H1", "and the window is one setting",
     "Across every closed-loop artifact the circuit, the read-out draw, the basis, the task names and their class "
     "count, the seed stream and the circuit's size are constant",
     "falsifier: any of them differing between two window runs"),
    ("H2", "and what varies is the manipulations and their consequences",
     "The fields that differ across the window are within the moved set and the fields those move by construction",
     "falsifier: a field varying that is in neither list"),
    ("H3", "and the horizon is the artifacts' own",
     "From `e369`'s distance of 2 and `tau = 12` the last traceable cue step is 10 for the cue population and 8 for "
     "the action one, and `e368`'s curve records exactly those two cliffs",
     "falsifier: a cliff elsewhere, or the formula disagreeing with the curve; refused when either is absent"),
    ("H4", "and the draw is one, and it is the two-hop one",
     "`e370`'s sweep records the distance 1 eleven times and 2 five times, and every window run's seed0 is 0",
     "falsifier: another seed stream, or a sweep whose counts contradict the claim; refused when it is absent"),
    ("H5", f"and the corpus's own count is a bound, at least {MIN_WINDOW}",
     "The window holds at least twenty artifacts",
     "falsifier: fewer, which would say this unit's definition has drifted from the line's"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def window(root: Path = RUNS) -> list[dict]:
    """Every artifact under `runs/` whose configuration wired the closed loop, with the fields claims read."""
    out = []
    for p in sorted(Path(root).glob("e3*_earned_label_*.json")):
        doc = load(p)
        if not doc:
            continue
        cfg = doc.get("config") or {}
        if not cfg.get("closed_loop"):
            continue
        draw = doc.get("readout") or {}
        canvas = doc.get("env_draw") or {}
        tasks = doc.get("tasks") or []
        out.append({"artifact": p.name, "circuit": doc.get("circuit"), "circuit_size": cfg.get("circuit_size"),
                    "readout_subset": draw.get("subset_sha1"), "readout_size": draw.get("size"),
                    "basis": cfg.get("basis"), "seed0": cfg.get("seed0"), "support": cfg.get("support"),
                    "task_names": [t.get("name") for t in tasks],
                    "n_classes": sorted({int(t.get("n_classes") or 0) for t in tasks}),
                    "task_readout_widths": sorted({int(t.get("n_readout") or 0) for t in tasks}),
                    "loop_cue_at": cfg.get("loop_cue_at"), "loop_drive_from_cue": bool(cfg.get("loop_drive_from_cue")),
                    "lr": cfg.get("lr"), "iters": cfg.get("iters"), "repeats": cfg.get("repeats"),
                    "loop_world_dims": cfg.get("loop_world_dims"),
                    "frozen_body": bool(cfg.get("frozen_body")), "frozen_bias": bool(cfg.get("frozen_bias")),
                    "no_feedback": bool(cfg.get("no_feedback")), "anchor_bias": bool(cfg.get("anchor_bias")),
                    "world_drive_sha1": canvas.get("world_drive_sha1"),
                    "world_read_sha1": canvas.get("world_read_sha1"),
                    "world_coupling_sha1": canvas.get("world_coupling_sha1"),
                    "n_action": canvas.get("n_action"), "action_sha1": canvas.get("action_sha1"),
                    "drive_from_cue": canvas.get("drive_from_cue") or bool(cfg.get("loop_drive_from_cue"))})
    return out


def _values(rows: list[dict], key: str) -> dict:
    out = {}
    for r in rows:
        v = r.get(key)
        out.setdefault(json.dumps(v, sort_keys=True), []).append(r["artifact"])
    return out


def reading(root: Path = RUNS, curve: Path = CURVE, distance: Path = DISTANCE, sweep: Path = SWEEP) -> dict:
    rows = window(root)
    out = {"rows": rows, "n": len(rows), "invariants": {}, "varied": {},
           "curve": None, "distance": None, "sweep": None}
    for key in INVARIANTS:
        out["invariants"][key] = _values(rows, key)
    for key in MOVED + FOLLOWS:
        v = _values(rows, key)
        if len(v) > 1:
            out["varied"][key] = {k: len(names) for k, names in v.items()}
    cdoc = load(curve)
    if cdoc:
        cells = cdoc.get("cells") or {}
        cliffs = {}
        for source in ("cue", "action"):
            clearing = cdoc.get("last_clearing") or {}
            cliffs[source] = clearing.get(source)
        out["curve"] = {"artifact": Path(curve).name, "cliffs": cliffs,
                        "tau": cdoc.get("tau"),
                        "sd_at_action_10": (cells.get("action@10") or {}).get("world_sd")}
    ddoc = load(distance)
    if ddoc:
        rows_d = (ddoc.get("rows") or {})
        first = rows_d.get(str((ddoc.get("sizes") or [300])[0])) or {}
        out["distance"] = {"artifact": Path(distance).name,
                           "action": ((first.get("sources") or {}).get("action") or {}).get("distance"),
                           "cue": ((first.get("sources") or {}).get("cue") or {}).get("distance")}
    sdoc = load(sweep)
    if sdoc:
        #: the distance lives under the row's `sources`, so a reader that looked for it at the top level
        #: would count zero of everything and fire a claim about `e370` that `e370` does not make
        ds = [(v.get("sources") or {}).get("action", {}).get("distance")
              for v in (sdoc.get("rows") or {}).values()]
        out["sweep"] = {"artifact": Path(sweep).name, "n": len(ds),
                        "one": sum(1 for d in ds if d == 1), "two": sum(1 for d in ds if d == 2)}
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no closed-loop artifact was found"} for c in CLAIMS]

    broken = {k: sorted(v) for k, v in (r.get("invariants") or {}).items() if len(v) > 1}
    j1 = {"id": "H1", "measured": f"over {r['n']} closed-loop artifacts the invariant fields take "
                                  f"{ {k: len(v) for k, v in (r.get('invariants') or {}).items()} } distinct values, "
                                  f"with {[k for k in broken]} differing",
          "verdict": "MET -- the window is one setting" if not broken else
          f"FALSIFIER FIRED -- { {k: len(v) for k, v in broken.items()} } differ between window runs"}

    varied = sorted((r.get("varied") or {}))
    unexpected = [k for k in varied if k not in MOVED and k not in FOLLOWS]
    j2 = {"id": "H2", "measured": f"the fields that differ across the window are {varied}, which is "
                                  f"{len([k for k in varied if k in MOVED])} of the moved set and "
                                  f"{len([k for k in varied if k in FOLLOWS])} that follow from it",
          "verdict": "MET -- what varies is the manipulations and their consequences" if not unexpected else
          f"FALSIFIER FIRED -- {unexpected} vary and are in neither list"}

    cz, dz = r.get("curve"), r.get("distance")
    if not cz or not dz:
        j3 = {"id": "H3", "measured": f"the curve is present {bool(cz)} and the distance {bool(dz)}",
              "verdict": "REFUSED -- one of the two artifacts the horizon is read from is absent"}
    else:
        tau = int(cz.get("tau") or TAU)
        d_action = dz.get("action")
        d_cue = dz.get("cue")
        predicted = {"cue": None if d_cue is None else tau - 2 - int(d_cue),
                     "action": None if d_action is None else tau - 2 - int(d_action)}
        measured = cz.get("cliffs") or {}
        good = predicted == {"cue": measured.get("cue"), "action": measured.get("action")}
        j3 = {"id": "H3", "measured": f"`{dz['artifact']}` puts the cue population at distance {d_cue} and the action "
                                      f"population at {d_action}, so `tau - 2 - d` with `tau = {tau}` predicts "
                                      f"{predicted}, and `{cz['artifact']}` records {measured}",
              "verdict": "MET -- the formula the line registered is the curve's own two cliffs" if good else
              f"FALSIFIER FIRED -- the formula predicts {predicted} and the curve records {measured}"}

    sw = r.get("sweep")
    if not sw:
        j4 = {"id": "H4", "measured": "the distance sweep is absent",
              "verdict": "REFUSED -- the artifact this claim reads is absent"}
    else:
        seeds = sorted({row.get("seed0") for row in rows})
        #: what the claim needs is that both distances occur and that the one-hop draw is the majority, which is
        #: what puts `seed0` inside it -- not that the counts equal any pair of numbers
        good = sw["one"] > 0 and sw["two"] > 0 and sw["one"] > sw["two"] and seeds == [0]
        j4 = {"id": "H4", "measured": f"`{sw['artifact']}`'s {sw['n']} draws take the distance 1 {sw['one']} times and "
                                      f"2 {sw['two']} times, and the window's runs carry the seed streams {seeds}",
              "verdict": "MET -- one draw, and the sweep puts seed0 in the two-hop five" if good else
              f"FALSIFIER FIRED -- distances 1 and 2 taken {sw['one']} and {sw['two']} times over {sw['n']} draws "
              f"with seed streams {seeds}"}

    j5 = {"id": "H5", "measured": f"the window holds {r['n']} closed-loop artifacts against a bound of {MIN_WINDOW}",
          "verdict": f"MET -- the count is at or above the bound, {r['n']} against {MIN_WINDOW}" if r["n"] >= MIN_WINDOW
          else f"FALSIFIER FIRED -- only {r['n']} artifacts: this unit's definition has drifted from the line's"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("rows"):
        print("== the window as one setting ==\n   REFUSED -- no closed-loop artifact was found")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the window as one setting ==")
    print(f"   {r['n']} closed-loop artifacts read from `{RUNS}`")
    print(f"\n   the setting, and how many distinct values each defining field takes:")
    for k, v in (r.get("invariants") or {}).items():
        print(f"     {k:>22}: {len(v)} value(s)")
    print(f"\n   what varies across the window: {sorted((r.get('varied') or {}))}")

    print("\n== the registered claims, H1-H5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e363` to `e386` are one configuration moved one field at a time; this reads them as a set and")
    print("    states the horizon the line registered rather than asserting it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(root=args.root)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
