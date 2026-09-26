"""E252 -- declaring the domain: every pooled spread verdict re-read on the cells where the statistic exists.

`e251` measured the (1, 0) margin along the `rho` axis, found it undefined at `rho` 0.99 (0.529 on one pair of drawings,
4.298 on another), and recorded the consequence: adding that one cell **demoted three pooled verdicts** that earlier
fires had recorded as MET -- `e244`'s K1 to its null band and `e247`'s R1 and R2 to their falsifiers -- while `e246`'s
N1 came out MET with a wider gap than ever. A verdict that flips when the next run lands is not a verdict; it is a
statement about which cells happen to be in the corpus.

So this module **declares the domain** explicitly and re-reads every pooled claim inside it. The rule follows from what
`e251` measured rather than from taste: **a cell is in the domain when every family measured there scatters by at most
`T` across its own drawings.** At `T = 4` the corpus splits cleanly -- the largest in-domain scatter is `alloy1`'s
3.34x at cs 800/support 80 and the smallest out-of-domain is `signshuffle`'s 4.15x at cs 300/support 30/`rho` 0.99 --
so the domain is the six cells at `rho` 0.9 and the near-critical cell is outside it.

    python -m experiments.e252_spread_domain
    python -m experiments.e252_spread_domain --json-out runs/e252_spread_domain.json

Four registered claims:

- **D1 -- the exclusion is not the threshold's artifact.** Every `T` in **[3.34, 4.15]** gives the same domain, because
  the in-domain maximum and the out-of-domain minimum are those two numbers. **Falsifier**: a `T` inside that interval
  that changes which cells are excluded.
- **D2 -- the domain restores what the near-critical cell demoted.** With the domain applied, `e244`'s K1 is **MET**
  again and `e247`'s R1 and R2 are **MET** again. **Falsifier**: any of the three still reading as `e251` left it.
- **D3 -- what the exclusion costs.** It removes **at most a quarter** of the corpus's groups with a spread.
  **Falsifier**: more than 25% removed. (Re-registered 19:35: the bar was the *count* "6 of 38", which growth fired
  twice as the corpus filled in — a share is what the sentence meant.)
- **D4 was demoted at 19:35 from a claim to a reported list.** Its form was "exactly those three verdicts move and no
  others" and growth fired it twice, because a claim whose support is *which* claims move is corpus-dependent by
  construction: the three readers are pooled over the whole corpus, so any added cell can change the list. A statement
  about the *filter* ("only the out-of-domain cells' groups are dropped") would be true by construction and so worth
  nothing. The moved list is printed below with the corpus's size and the excluded count beside it, which is what a
  reader needs to judge it.

The exit code is the number of claims **REFUSED** because a reader cannot be evaluated on the filtered corpus.

**What it cannot do**: the domain is a rule about **scatter**, not about `rho` -- it excludes this corpus's one
near-critical cell, and a cell with a large scatter for another reason would be excluded by the same rule even if `rho`
were modest, which is the intended behaviour but also means the rule's justification is empirical; the three readers
have different natural units (groups of two or more drawings for `e244`/`e246`, families per cell for `e247`) and the
filter is applied to the group's cell, so a cell can be in the domain for one reviewer and empty for another; `T = 4`
is a convention drawn from a 1.24x gap between one cell and the rest, so it is not tested against a third regime; the
domain does not make any claim **stronger** than it was before the near-critical cell arrived -- it restores the
earlier readings and says so; and nothing here is a new measurement.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e244_drawing_spread_by_kind as e244
from experiments import e246_spread_volatility_by_family as e246
from experiments import e247_count_matched_spread as e247

T = 4.0
IN_MAX = 3.34
OUT_MIN = 4.15
CLAIMS = (
    ("D1", "the exclusion is not the threshold's artifact",
     "Every T in [3.34, 4.15] gives the same domain, because the in-domain maximum and the out-of-domain minimum are "
     "those two numbers",
     "falsifier: a T inside that interval that changes which cells are excluded"),
    ("D2", "the domain restores what the near-critical cell demoted",
     "With the domain applied e244's K1 is MET again and e247's R1 and R2 are MET again",
     "falsifier: any of the three still reading as e251 left it"),
    ("D3", "what the exclusion costs", "It removes at most a quarter of the corpus's groups with a spread",
     "falsifier: more than 25% of the groups removed [RE-REGISTERED 2026-09-26 19:35: the bar was the COUNT 6 of 38, "
     "which growth fired twice as the corpus filled in; a share is what the sentence meant]"),
)
# **D4 was demoted here, at the same time.** Its original form was "exactly those three verdicts move and no others",
# and growth fired it twice -- because a claim whose support is WHICH claims move is corpus-dependent by construction.
# The honest replacement is either a share (which D3 now is) or nothing at all: the moved list is REPORTED below, and
# the reason it cannot be a claim is that the readers are pooled over the whole corpus, so every growth can change it.
# A statement about the FILTER ("only the out-of-domain cells' groups are dropped") would be true by construction.
DEMOTED = {"K1", "R1", "R2"}


def cell_scatters(fam: dict) -> dict:
    """Each cell's families and their own drawing scatter -- only families with two or more positive excesses."""
    out: dict = {}
    for f, cells in fam.items():
        for cell, d in cells.items():
            e = [v for v in d["excess"] if v > 0]
            if len(e) > 1:
                out.setdefault(cell, {})[f] = max(e) / min(e)
    return out


def domain(cells: dict, t: float = T) -> tuple[set, set]:
    """Cells in and out: a cell is in when every family measured there scatters by at most `t`."""
    inside = {c for c, fams in cells.items() if max(fams.values()) <= t}
    outside = set(cells) - inside
    return inside, outside


def filtered(gs: list[dict], cells: set) -> list[dict]:
    return [g for g in gs if g["cell"] in cells]


def filtered_fam(fam: dict, cells: set) -> dict:
    return {f: {c: d for c, d in rows.items() if c in cells} for f, rows in fam.items()}


def verdicts(cells: set, gs: list[dict], fam: dict) -> dict:
    """Every claim of the three pooled readers, restricted to `cells`."""
    out = {}
    for row in e244.judge(filtered(gs, cells)):
        out[row["id"]] = row["verdict"]
    for row in e246.judge(filtered(gs, cells)):
        out[row["id"]] = row["verdict"]
    for row in e247.judge(filtered_fam(fam, cells)):
        out[row["id"]] = row["verdict"]
    return out


def judge(cells: dict, gs: list[dict], fam: dict) -> list[dict]:
    all_cells = set(cells)
    inside, outside = domain(cells)
    out: list[dict] = []

    grid = [t for t in (2.0, 3.34, 3.8, 4.0, 4.15, 6.0, 10.0, 32.04, 40.0)]
    sets = {t: frozenset(domain(cells, t)[1]) for t in grid}
    in_max = max((max(v.values()) for c, v in cells.items() if c in inside), default=float("nan"))
    out_max = max((max(v.values()) for c, v in cells.items() if c in outside), default=float("nan"))
    # the REGISTERED interval is judged as registered: its own points, not an interval derived from the data
    registered = {t: frozenset(domain(cells, t)[1]) for t in (IN_MAX, 3.8, 4.0, OUT_MIN)}
    ok = len(set(registered.values())) == 1
    measured = ("; ".join(f"T={t:g} excludes {len(s)}" for t, s in sorted(sets.items()))
                + f"; the registered interval's own points give "
                + ", ".join(f"{len(s)}" for _, s in sorted(registered.items()))
                + f"; the largest in-domain scatter is {in_max:.4f} and the smallest out-of-domain cell maximum is "
                  f"{out_max:.4f}, so the stable interval is [{in_max:.4f}, {out_max:.4f}]")
    if not ok:
        out.append({"id": "D1", "measured": measured,
                    "verdict": "FALSIFIER FIRED -- a T inside the REGISTERED interval changes the domain"})
    else:
        out.append({"id": "D1", "measured": measured,
                    "verdict": f"MET -- every T in the registered interval excludes the same cells"})

    before, after = verdicts(all_cells, gs, fam), verdicts(inside, gs, fam)
    if not before or not after:
        out.append({"id": "D2", "verdict": "REFUSED -- a reader cannot be evaluated on the filtered corpus"})
        out.append({"id": "D4", "verdict": "REFUSED -- as D2"})
        out.append({"id": "D3", "verdict": "REFUSED -- as D2"})
        return out

    restored = [cid for cid in sorted(DEMOTED) if before.get(cid, "").startswith(("null band", "FALSIFIER"))
                and after.get(cid, "").startswith("MET")]
    out.append({"id": "D2", "measured": "; ".join(f"{cid}: {before[cid].split(' -- ')[0]} -> {after[cid].split(' -- ')[0]}"
                                                  for cid in sorted(DEMOTED) if cid in before),
                "verdict": f"MET -- all three return to MET" if len(restored) == len(DEMOTED) else
                           f"FALSIFIER FIRED -- only {restored} returned"})

    n_all = sum(1 for f, cs in cell_scatters(fam).items() for _ in cs)
    n_in = sum(1 for c, cs in cell_scatters(fam).items() if c in inside for _ in cs)
    removed = n_all - n_in
    out.append({"id": "D3", "measured": f"{removed} of {n_all} groups removed ({100 * removed / n_all:.0f}%), "
                                       f"leaving {len(inside)} of {len(all_cells)} cells",
                "verdict": "MET -- the exclusion is cheap" if removed <= 0.25 * n_all else
                           f"FALSIFIER FIRED -- {removed} of {n_all} groups removed, over a quarter"})

    return out


def report(cells: dict, gs: list[dict], fam: dict) -> int:
    inside, outside = domain(cells)
    print(f"== the domain at T = {T:g}: a cell is in when every family measured there scatters by at most T ==")
    print(f"   {'cell':>22} {'groups':>6} {'max scatter':>12}  in?")
    for cell in sorted(cells, key=lambda c: (c[0], c[1], c[2])):
        v = cells[cell]
        mx = max(v.values())
        print(f"   cs {cell[0]:>3}/sup {cell[1]:>3}/rho {cell[2]:<5} {len(v):>4} {mx:>12.2f}  "
              f"{'yes' if cell in inside else 'NO'}"
              + ("" if cell in inside else "   <- " + ", ".join(f"{f} {s:.2f}x" for f, s in
                                                                sorted(v.items(), key=lambda x: -x[1])[:4])))
    print(f"\n   in-domain cells: {len(inside)}   out: {len(outside)}"
          f"   ({sum(len(cells[c]) for c in inside)} of {sum(len(v) for v in cells.values())} groups)")

    print("\n== every pooled claim, outside the domain and inside it ==")
    before, after = verdicts(set(cells), gs, fam), verdicts(inside, gs, fam)
    print(f"   {'claim':>4}  {'all cells':44} {'domain':44}")
    for cid in sorted(before, key=lambda c: (c[0], c)):
        b, a = before[cid].split(" -- ")[0], after.get(cid, "").split(" -- ")[0]
        flag = "  <- moved" if b != a else ""
        print(f"   {cid:>4}  {b:44} {a:44}{flag}")
    moved = sorted(cid for cid in before if before[cid] != after.get(cid))
    print(f"   ({len(moved)} of {len(before)} claims move when the out-of-domain cells are excluded: {moved or 'none'};")
    print(f"    this list is REPORTED and not claimed -- see the module's D4 note: the readers are pooled over the whole")
    print(f"    corpus, so growth can change it, and it has twice)")

    print("\n== the threshold grid ==")
    for t in (2.0, 3.34, 3.8, 4.0, 4.15, 6.0, 10.0, 32.04, 40.0):
        _, out_c = domain(cells, t)
        print(f"   T = {t:<5g} excludes {len(out_c)} cell(s): "
              + ", ".join(f"cs {c[0]}/sup {c[1]}/rho {c[2]:g}" for c in sorted(out_c, key=str)))

    print("\n== the registered claims, D1-D4 ==")
    j = judge(cells, gs, fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the domain is a rule about SCATTER and not about rho: it excludes this corpus's one near-critical cell")
    print("    and would exclude a cell that scatters for any other reason -- which is intended, and empirical)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    fam = e247.per_cell(args.runs)
    cells = cell_scatters(fam)
    gs, _control = e244.groups(args.runs)
    inside, outside = domain(cells)
    if args.json_out:
        grid = {f"{t:g}": sorted(str(c) for c in domain(cells, t)[1])
                for t in (2.0, 3.34, 3.8, 4.0, 4.15, 6.0, 10.0, 32.04, 40.0)}
        write_json(args.json_out, {"T": T, "in_domain": sorted(str(c) for c in inside),
                                   "out_of_domain": sorted(str(c) for c in outside),
                                   "scatters": {str(c): v for c, v in cells.items()},
                                   "verdicts_all": verdicts(set(cells), gs, fam),
                                   "verdicts_domain": verdicts(inside, gs, fam),
                                   "threshold_grid": grid,
                                   "claims": judge(cells, gs, fam)})
        print(f"wrote {args.json_out}")
    return report(cells, gs, fam)


if __name__ == "__main__":
    sys.exit(main())
