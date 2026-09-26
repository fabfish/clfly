"""E261 -- the three-replicate floor `e259` extrapolated to, measured from the three-replicate runs that were on disk.

`e259` turned `e76`'s detection floors into the statement a null needs, and its four registered claims stand: the
sixteen-replicate run could have seen the effect it replaced (3.32 sigma), the line's three figures need budgets
differing by 55x, and the `side` one was never detectable while the other two are excluded at better than 3 sigma.
What it added *beside* them -- in its third section and in the programme table's status cell -- is a second corollary:

    at n = 3 the three floors are 0.059, 0.075 and 0.100 against published effects of 0.0069, 0.0648 and 0.0718,
    so two of the line's three figures were published below their own detection floor

and that column could only be built one way: by scaling the **sixteen**-replicate sem with `sem ~ 1/sqrt(n)`, which
the same module's P4 flagged as an assumption. **The runs that would check it are on disk.** `e28` is the `side` run
at three replicates and `e31` the `cell_class` one; each is its powered re-run's configuration with `repeats`
changed, and the pair of them reconstructs the published cross-rung figure from its own replicate lists as
**+0.07176 at 2.134 sigma** against the published **+0.0718 at 2.13** -- which is how they are identified here.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **R1 -- the extrapolated floor is not the measured one.** Every floor `e259` scaled to three replicates is above
  the floor the three-replicate run itself gives: **0.05901 against 0.02891** (`side`), **0.07459 against 0.04900**
  (`cell_class`) and **0.09979 against 0.06725** (the cross-rung) -- factors of 2.04, 1.52 and 1.48. The mechanism is
  in the two runs the line has at both budgets: their floors differ by **1.131** (`side`) and **1.517**
  (`cell_class`) where the scaling predicts `sqrt(16/3) = 2.309`, because the three-replicate sd is 0.49x and 0.66x
  the sixteen-replicate one. **Falsifier**: any extrapolated floor within 20% of the measured one.
- **R2 -- and that flips one figure, not none.** Against their own floors the three published magnitudes read
  **0.239** (`side`, below), **1.323** (`cell_class`, above) and **1.068** (cross-rung, above), so `e259`'s "two of
  the line's three figures were published below their own detection floor" holds for **one**. **Falsifier**: two or
  more of the three at or below their own measured floor.
- **R3 -- the largest budget this line has run is 144 paired replicates, on another cell.** `e178` (cs 300 /
  support 80 / lambda 1.0) is a matched pair over **144** replicates, 7.39 h, reading **0.28 sigma**. Its
  configuration is not the published figures', so it cannot re-test them, but it fixes the largest budget the line
  has paid for at 144 where `e259`'s ladder stops at 40. **Falsifier**: no `basis` artifact above 40 paired
  replicates.

The price is REPORTED and not claimed: 219.5 replicates cost 40.5 h at the `side` configuration's own rate, 26.2 h at
the `cell_class` one's, and 11.3 h at the cs-300 lambda-1.0 rate, against the corpus's largest single run of 7.39 h.

**What it cannot do**: it leaves `e259`'s four claims alone -- they are about the sixteen-replicate column and stand
as read; the three-replicate runs are *configurations* matched to their re-runs field by field, not the same process
(`e31` ran two arms where `e46` ran three), so the comparison holds only for the fields the matched pair uses; the
measured floors carry their own sampling noise, which at three replicates is large (the sd ratio 0.49 is well inside
an F-test at 15 and 2 degrees of freedom), so R1 says the extrapolation is not supported rather than that a different
law holds; and the corpus is scanned for the largest budget, so a run outside `runs/` is invisible.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

#: Each published figure and the runs that carry it: name -> (three-replicate runs, sixteen-replicate run).
RUNGS = {"side": (("runs/e28_side_lam0.1.json",), "runs/e60_side_lam0.1_16reps.json"),
         "cell_class": (("runs/e31_methodlist_check.json",), "runs/e46_c2b_powered.json")}
#: The cross-rung figure is the difference of the two rungs' matched pairs, so it is reconstructed, not read.
CROSS = "side - cell_class"
#: `e259`'s power statement, which carries the floors this module checks.
POWER = Path("runs/e259_c2b_null_power.json")
#: The largest matched pair the corpus carries -- a `side` rung at another cell.
BIG = "runs/e178_rung_side_cs300_144reps.json"
#: The fields two runs of one configuration are free to differ in; `methods` is reported, not ignored.
FREE = ("json_out", "repeats")
SCALING = math.sqrt(16 / 3)
CLAIMS = (
    ("R1", "the extrapolated three-replicate floor is not the measured one",
     "Every floor `e259` scaled to three replicates is above the floor that run itself gives, by a factor of 1.48 to "
     "2.04",
     "falsifier: any extrapolated floor within 20% of the measured one"),
    ("R2", "and that flips one figure rather than none",
     "Against their own measured floors the three published magnitudes read below, above and above, so `e259`'s two "
     "of three is one of three",
     "falsifier: two or more of the three at or below their own measured floor"),
    ("R3", "the largest budget this line has run is 144 paired replicates, on another cell",
     "The corpus carries a matched pair over more than 40 replicates, so the ladder `e259` scaled does not stop at "
     "the largest budget the line has paid for",
     "falsifier: no `basis` artifact above 40 paired replicates"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def diffs(d: dict, metric: str = "final_accuracy") -> list[float]:
    """One run's matched pair per replicate: the biological basis minus its size-matched random one."""
    blk = d["methods"]
    return [a[metric] - b[metric] for a, b in zip(blk["ewc-block"]["replicates"],
                                                  blk["ewc-block-rand"]["replicates"])]


def stats(dl: list[float]) -> dict:
    n = len(dl)
    mean = sum(dl) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in dl) / (n - 1)) if n > 1 else float("nan")
    sem = sd / math.sqrt(n)
    return {"n": n, "delta": mean, "sd": sd, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf"),
            "floor": 2.0 * sem}


def config_diff(ca: dict, cb: dict) -> tuple[list[tuple], bool]:
    """The fields two runs of one configuration may not differ in, and whether only the budget does."""
    keys = sorted(set(ca) | set(cb))
    differ = [(k, ca.get(k), cb.get(k)) for k in keys if ca.get(k) != cb.get(k)]
    hard = [d for d in differ if d[0] not in FREE + ("methods",)]
    return differ, not hard


def largest_budget(root: Path = Path("runs")) -> list[dict]:
    """Every artifact in the corpus that carries a `basis` run, by paired replicate count."""
    out = []
    for path in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        cfg = (d or {}).get("config") or {}
        blk = (d.get("methods") or {})
        blk = blk.get("ewc-block") if isinstance(blk, dict) else None
        if "basis" not in cfg or not isinstance(blk, dict) or "replicates" not in blk:
            continue
        out.append({"artifact": Path(path).name, "basis": cfg.get("basis"), "cell": cfg.get("circuit_size"),
                    "support": cfg.get("support"), "lam": cfg.get("lam"), "n": len(blk["replicates"]),
                    "seconds": duration_seconds(d)})
    return sorted(out, key=lambda r: -r["n"])


def measured(runs: dict, figures: dict) -> list[dict]:
    """Each published figure with the floor its own three-replicate run gives."""
    out = []
    for name in ("side", "cell_class"):
        three, _sixteen = runs.get(name, (None, None))
        fig = figures.get(name)
        if three is None or fig is None:
            continue
        out.append({"figure": name, "published": abs(fig["published_effect"]), "sem": three["sem"],
                    "floor": three["floor"], "ratio": abs(fig["published_effect"]) / three["floor"],
                    "e259_floor": fig["floors"]["3"]})
    s3, c3 = runs.get("side", (None, None))[0], runs.get("cell_class", (None, None))[0]
    fig = figures.get(CROSS)
    if s3 is not None and c3 is not None and fig is not None:
        cross = [a - b for a, b in zip(s3["per_replicate"], c3["per_replicate"])]
        st = stats(cross)
        st.update(published=abs(fig["published_effect"]), ratio=abs(fig["published_effect"]) / st["floor"],
                  e259_floor=fig["floors"]["3"], per_replicate=cross)
        out.append(dict(st, figure=CROSS))
    return out


def judge(runs: dict, rows: list[dict], big: dict | None, largest: list[dict]) -> list[dict]:
    out: list[dict] = []

    over = [f"{r['figure']}: {r['e259_floor']:.5f} against {r['floor']:.5f} = {r['e259_floor'] / r['floor']:.2f}x"
            for r in rows]
    ok1 = bool(rows) and all(r["e259_floor"] / r["floor"] > 1.2 for r in rows)
    out.append({"id": "R1", "measured": "; ".join(over) or "no three-replicate run on disk",
                "verdict": "MET -- the extrapolated floors are all above the measured ones" if ok1 else
                           "FALSIFIER FIRED -- an extrapolated floor is within 20% of the measured one"})

    ratios = [f"{r['figure']}: {r['ratio']:.3f}" for r in rows]
    below = [r["figure"] for r in rows if r["ratio"] < 1]
    out.append({"id": "R2", "measured": f"published magnitude against its own floor -- " + "; ".join(ratios)
                + f"; below its own floor: {below or 'none'}",
                "verdict": f"MET -- {len(rows) - len(below)} of {len(rows)} are above their own floor" if len(below) < 2
                else f"FALSIFIER FIRED -- {len(below)} are below their own floor"})

    if big is None:
        out.append({"id": "R3", "measured": BIG, "verdict": "REFUSED -- the largest-budget artifact is not on disk"})
    else:
        top = largest[0] if largest else {}
        out.append({"id": "R3", "measured": f"the corpus's largest `basis` budget is n = {top.get('n')} "
                                            f"({top.get('artifact')}); e178 reads {big['delta']:+.5f} = "
                                            f"{big['sigma']:.2f} sigma, floor {big['floor']:.5f}",
                    "verdict": "MET -- the largest budget is above the 40 the ladder stops at"
                    if (top.get("n") or 0) > 40 else
                    "FALSIFIER FIRED -- nothing in the corpus runs a basis contrast above 40 replicates"})
    return out


def report(runs: dict, rows: list[dict], big: dict | None, largest: list[dict], diff_report: dict) -> int:
    figures = {r["figure"]: r for r in rows}
    print("== each published figure and the floor its own three-replicate run gives ==")
    for name in ("side", "cell_class"):
        three, sixteen = runs.get(name, (None, None))
        if three is None or sixteen is None:
            print(f"   {name}: missing one of the two budgets")
            continue
        print(f"\n   {name}   (fields differing between its two budgets: {diff_report.get(name, ([['?']], True))[0]})")
        for tag, st in (("n = 3 ", three), ("n = 16", sixteen)):
            print(f"      {tag}  delta {st['delta']:+.5f}  sem {st['sem']:.6f}  sd {st['sd']:.6f}  "
                  f"sigma {st['sigma']:.3f}  floor {st['floor']:.5f}")
        print(f"      floor ratio {three['floor'] / sixteen['floor']:.3f}   scaling predicts {SCALING:.3f}   "
              f"sd ratio {three['sd'] / sixteen['sd']:.3f}")
    if CROSS in figures:
        c = figures[CROSS]
        print(f"\n   {CROSS}   (reconstructed from the two runs' replicate lists)")
        print(f"      n = {c['n']}  delta {c['delta']:+.5f}  sem {c['sem']:.6f}  sigma {c['sigma']:.3f}  "
              f"floor {c['floor']:.5f}   per replicate {[round(x, 5) for x in c['per_replicate']]}")
        print(f"      the published figure was 0.0718 at 2.13 sigma: the reconstruction gives {c['delta']:+.5f} "
              f"at {c['sigma']:.2f}, which is how these two runs are identified as its rungs")

    print("\n== the published magnitude against its own measured floor, and against e259's scaled one ==")
    for r in rows:
        print(f"   {r['figure']:18} published {r['published']:.4f}  measured floor {r['floor']:.5f} "
              f"({r['ratio']:.3f}x)  e259's floor {r['e259_floor']:.5f} ({r['published'] / r['e259_floor']:.3f}x)")

    print("\n== the largest budgets the corpus carries (every artifact with a `basis` run) ==")
    for r in largest[:8]:
        per = (r["seconds"] / r["n"]) if r["seconds"] and r["n"] else float("nan")
        print(f"   n = {r['n']:4d}  {r['basis']:<14} cs {r['cell']}/sup {r['support']}/lam {r['lam']}  "
              f"{per:7.1f} s per replicate  {r['artifact']}")
    if big is not None:
        print(f"\n   the largest is {big['n']} replicates: delta {big['delta']:+.5f} = {big['sigma']:.2f} sigma "
              f"against a floor of {big['floor']:.5f}")

    print("\n== the price of the budget e259's power statement asks for (219.5 replicates), REPORTED ==")
    for name, (_three, sixteen) in runs.items():
        if sixteen is not None:
            print(f"   {name:<11} {sixteen['per_replicate_s']:7.1f} s per replicate -> "
                  f"{219.5 * sixteen['per_replicate_s'] / 3600:6.1f} h")
    if big is not None:
        print(f"   {'e178 rate':<11} {big['per_replicate']:7.1f} s per replicate -> "
              f"{219.5 * big['per_replicate'] / 3600:6.1f} h (another cell)")

    print("\n== the registered claims, R1-R3 ==")
    j = judge(runs, rows, big, largest)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (e259's four claims are untouched: they are about the sixteen-replicate column, and this module checks")
    print("    only the n = 3 column it extrapolated to beside them)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    power = load(POWER)
    if power is None:
        raise SystemExit(f"need {POWER} -- e259's power statement is what carries the floors under test")
    figures = {f["figure"]: f for f in power["figures"]}
    runs, diff_report = {}, {}
    for name, (three_paths, sixteen_path) in RUNGS.items():
        three, sixteen = [], None
        for path in three_paths:
            d = load(path)
            if d is not None:
                three.append(dict(stats(diffs(d)), per_replicate=diffs(d), artifact=Path(path).name,
                                  seconds=duration_seconds(d), config=d["config"]))
        d = load(sixteen_path)
        if d is not None:
            sixteen = dict(stats(diffs(d)), artifact=Path(sixteen_path).name, seconds=duration_seconds(d),
                           config=d["config"])
            sixteen["per_replicate_s"] = (duration_seconds(d) or float("nan")) / sixteen["n"]
        three = three[0] if three else None
        runs[name] = (three, sixteen)
        if three is not None and sixteen is not None:
            differ, ok = config_diff(three["config"], sixteen["config"])
            diff_report[name] = ([[k, str(a), str(b)] for k, a, b in differ], ok)

    big = load(BIG)
    if big is not None:
        big = stats(diffs(big))
        big["per_replicate"] = (duration_seconds(load(BIG)) or float("nan")) / big["n"]
    largest = largest_budget()
    rows = measured(runs, figures)

    if args.json_out:
        write_json(args.json_out, {"power": str(POWER), "scaling_prediction": SCALING,
                                   "config_check": {k: {"differing_fields": v[0], "only_the_budget_differs": v[1]}
                                                    for k, v in diff_report.items()},
                                   "runs": {n: {"n3": runs[n][0], "n16": runs[n][1]} for n in runs},
                                   "measured_floors": rows,
                                   "largest_budget": largest[:12],
                                   "e178_side_144": big,
                                   "claims": judge(runs, rows, big, largest)})
        print(f"wrote {args.json_out}")
    return report(runs, rows, big, largest, diff_report)


if __name__ == "__main__":
    sys.exit(main())
