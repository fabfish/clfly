"""E293 -- how many draws a draw sd needs: the paper's own rung table, reproduced, and where its ordering is noise.

The paper's section 4.3 carries the one table whose subject is a **draw sd** rather than a seed spread: five named
partition rungs, each with the draw-to-draw sd of its matched-random control measured over 5 or 8 draws, and each with
the run that measured it credited in the row. It is the table that says which rungs are near-diagonal and which are
coarse, and the section's own argument about non-monotonicity is read off the *ordering* of those five numbers.

An sd estimated from `k` draws has `k - 1` degrees of freedom, so its own relative standard error is about
`1/sqrt(2(k - 1))`: **27% at 5 draws and 35% at 8** -- and the table's five entries are spread over a factor of 5.7,
which is close enough to that error that the ordering needs checking rather than assuming. That is what this unit
does, on the artifacts the table itself credits.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **V1 -- the column reproduces.** Each of the five draw sds comes out of the artifact the row credits, within 1%.
  **Falsifier**: one outside that.
- **V2 -- and the column's own precision is the binding limit.** At 5 and 8 draws, most of the ten pairwise orderings
  of the five rungs are not resolved at 95%. **Falsifier**: fewer than half of them are unresolved.
- **V3 -- and the ordering the paper's argument uses is safe.** The two rungs the non-monotonicity argument actually
  contrasts are separated by more than a factor of three, which 5 and 8 draws do resolve. **Falsifier**: that pair is
  not resolved either.

**What the three add up to.** The column is right and it is *thin*: a draw sd measured over 5 draws is a five-point
standard deviation, and the table's middle rows -- `ito_lee_hemilineage`, `supertype`, `cell_type` -- are what the
error bars cannot separate. So the table's *level* statement (coarse versus near-diagonal, which the section uses) is
supported and its *fine ordering* is not, and the fix is **more draws rather than more seeds**: the same runner has a
`--draws` flag, and the corpus already has runs at 8 draws against runs at 5.

**What it cannot do.** *The intervals assume the draws are independent normal samples of the control's excess*, which
is the arithmetic the runner's own `control_sd_across_draws` is built on and not something this unit checks. *The
degrees of freedom are `k - 1` and no more*: nothing here accounts for the seed component that is also inside each
draw's mean, so the intervals are a lower bound on the real uncertainty -- the true ordering is weaker than reported,
not stronger. *Six of ten unresolved is not six of ten wrong*: an unresolved ordering is one the data cannot
distinguish, and the true values may still be ordered as the table prints them. *The section's non-monotonicity
argument uses more rows than this table* -- it also reads a four-point concentration series from other artifacts --
so V3 clears the comparison this unit can check and not the whole argument. *And no number of the paper's is
re-measured*: what is new is the column's own error bar and what it does to the ordering.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

from scipy import stats

from clfly.bench.artifacts import write_json

#: The section's table, row by row: rung, the artifact the row credits, the draws it credits, the sd it prints.
RUNG_TABLE = (
    ("side", "runs/e67_drawsd_side_min1.json", 8, 2.16e-4),
    ("cell_class", "runs/e17_cell_class_drawsd.json", 5, 2.37e-4),
    ("ito_lee_hemilineage", "runs/e17b_ito_lee_hemilineage_drawsd.json", 5, 4.16e-5),
    ("supertype", "runs/e17b_supertype_drawsd.json", 5, 8.35e-5),
    ("cell_type", "runs/e67_drawsd_cell_type_min1.json", 8, 6.80e-5),
)
#: The two rungs the section's non-monotonicity argument contrasts.
ARGUMENT_PAIR = ("side", "cell_type")
#: The precision the printed sds are checked to.
TOLERANCE = 0.01
ALPHA = 0.05
CLAIMS = (
    ("V1", "the column reproduces",
     "Each of the five draw sds comes out of the artifact the row credits, within one per cent",
     f"falsifier: one outside {TOLERANCE}"),
    ("V2", "and the column's own precision is the binding limit",
     "Most of the ten pairwise orderings of the five rungs are not resolved at 95%",
     "falsifier: fewer than half of them are unresolved"),
    ("V3", "and the ordering the paper's argument uses is safe",
     "The pair the non-monotonicity argument contrasts is resolved",
     "falsifier: that pair is not resolved either"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def interval(sd: float, draws: int, alpha: float = ALPHA) -> tuple[float, float]:
    """The 95% interval for a standard deviation estimated from `draws` draws, which is `draws - 1` dof."""
    df = max(draws - 1, 1)
    return (sd * math.sqrt(df / stats.chi2.ppf(1 - alpha / 2, df)),
            sd * math.sqrt(df / stats.chi2.ppf(alpha / 2, df)))


def ordered(a: dict, b: dict) -> bool:
    """Whether two draw sds are separated at 95%, in either direction."""
    return a["lo"] > b["hi"] or b["lo"] > a["hi"]


def draws_for(ratio: float, alpha: float = ALPHA, cap: int = 2000) -> int | None:
    """The draws per rung a ratio between two draw sds needs for their intervals to separate, if it ever does.

    Two intervals `s1 [a, b]` and `s2 [a, b]` (the factors are the same when the draws are equal) separate when
    `s1 * a > s2 * b`, i.e. when the ratio exceeds `b / a` -- which falls towards one as the draws grow.
    """
    for df in range(2, cap):
        lo = math.sqrt(df / stats.chi2.ppf(1 - alpha / 2, df))
        hi = math.sqrt(df / stats.chi2.ppf(alpha / 2, df))
        if ratio * lo > hi:
            return df + 1
    return None


def reading() -> dict:
    rows = []
    for rung, path, draws, printed in RUNG_TABLE:
        d = load(path)
        if d is None:
            continue
        measured = d["control_sd_across_draws"]
        lo, hi = interval(measured, draws)
        rows.append({"rung": rung, "artifact": Path(path).name, "draws": draws, "credited": draws,
                     "draws_recorded": (d.get("config") or {}).get("draws"),
                     "printed": printed, "measured": measured,
                     "difference": (measured - printed) / printed,
                     "seed_sem": d.get("seed_sem"), "lo": lo, "hi": hi,
                     "replicates": (d.get("config") or {}).get("seeds")})
    pairs = []
    for a, b in itertools.combinations(rows, 2):
        pairs.append({"a": a["rung"], "b": b["rung"], "ratio": max(a["measured"], b["measured"])
                      / min(a["measured"], b["measured"]), "ordered": ordered(a, b)})
    return {"rows": rows, "pairs": pairs,
            "unresolved": [p for p in pairs if not p["ordered"]],
            "argument_pair": next((p for p in pairs if {p["a"], p["b"]} == set(ARGUMENT_PAIR)), None),
            "draws_for_1.5x": draws_for(1.5), "draws_for_2x": draws_for(2.0)}


def judge(r: dict) -> list[dict]:
    rows = (r or {}).get("rows") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the table could not be read"} for c in CLAIMS]

    worst = max(abs(x["difference"]) for x in rows)
    out = [{"id": "V1", "measured": f"{len(rows)} rows read; the largest relative difference between the artifact and "
                                     f"the printed sd is {100 * worst:.2f}%; "
                                     + "; ".join(f"{x['rung']} {x['measured']:.3g} against {x['printed']:.3g}"
                                                  for x in rows),
            "verdict": "MET -- the table's draw-sd column comes out of the runs it credits" if worst <= TOLERANCE else
                       f"FALSIFIER FIRED -- {100 * worst:.2f}%"}]

    unresolved, pairs = r["unresolved"], r["pairs"]
    out.append({"id": "V2", "measured": f"{len(unresolved)} of {len(pairs)} pairwise orderings are not resolved at "
                                        f"95% at 5 and 8 draws; the largest unresolved ratio is "
                                        f"{max((p['ratio'] for p in unresolved), default=float('nan')):.2f}; "
                                        f"a 1.5x ordering would need {r['draws_for_1.5x']} draws and a 2x ordering "
                                        f"{r['draws_for_2x']}",
                "verdict": "MET -- the column's own precision is the binding limit" if 2 * len(unresolved) > len(pairs)
                else f"FALSIFIER FIRED -- only {len(unresolved)} of {len(pairs)} are unresolved"})

    pair = r["argument_pair"]
    out.append({"id": "V3", "measured": f"the pair the non-monotonicity argument contrasts is {pair['a']} against "
                                        f"{pair['b']} at a ratio of {pair['ratio']:.2f}, ordered at 95%: "
                                        f"{pair['ordered']}",
                "verdict": "MET -- the ordering the paper's argument uses is resolved" if pair and pair["ordered"] else
                           "FALSIFIER FIRED -- the argument's own pair is not resolved"})
    return out


def report(r: dict) -> int:
    print("== the section's draw-sd table, re-derived ==")
    print(f"   {'rung':22} {'draws':>5} {'sd':>11} {'printed':>11} {'diff':>7} {'95% interval':>26} {'seeds':>6}")
    for x in r["rows"]:
        print(f"   {x['rung']:22} {x['draws']:5} {x['measured']:11.3g} {x['printed']:11.3g} "
              f"{100 * x['difference']:+6.2f}% [{x['lo']:.2e}, {x['hi']:.2e}] {str(x['replicates']):>6}")

    print("\n== the ten pairwise orderings ==")
    for p in sorted(r["pairs"], key=lambda p: p["ratio"]):
        print(f"   {p['a']:22} / {p['b']:22} ratio {p['ratio']:6.2f}  ordered at 95%: {p['ordered']}")
    print(f"\n   unresolved: {len(r['unresolved'])} of {len(r['pairs'])}; a 1.5x ordering needs "
          f"{r['draws_for_1.5x']} draws per rung and a 2x ordering {r['draws_for_2x']}")

    print("\n== the registered claims, V1-V3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the column is right and thin: a five-point sd cannot order the table's middle rows, and the fix is")
    print("    more draws rather than more seeds -- which the section's own argument turns on resolving)")
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
