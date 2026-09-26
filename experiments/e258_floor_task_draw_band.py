"""E258 -- the floor's task-draw band: the long-queued "support draw" question, answered from the corpus.

This line has carried an open item for many fires: *"the cs-300 task drift's remaining candidate is the support draw --
a run recording the support fingerprint at cs 300/support 30/seeds 3, against `e217`'s absence of one."* Read against the
corpus, the item resolves in two parts, and the second is a better question than the first:

1. **The run is not needed.** The `support_draw.fingerprint_sha1` convention belongs to the runners that take
   `--support-seed` (the overlap suite: `e198`'s census finds 137 artifacts with a live support draw and 8 identifying
   it). The ladder runs do not have that flag: their supports are drawn from the connectome **from the task seeds**, so
   `(seeds, seed0, q)` *is* the draw's identity, and the artifacts that vary it are already on disk.
2. **And what they show is worth having.** cs 300/support 30 carries **six `real` draws at `rho` 0.9** and
   cs 800/support 80 **eight**, so the floor -- the ladder's lowest level, and the one whose rise with the shrinking
   circuit this record quotes -- can be given a band instead of a point:

       cs 300/support 30   e13 0.02723, e181 0.02516, e202 0.02645, e204 0.02745, e206 0.02577, e217 0.02978
       cs 800/support 80   0.01739, 0.01749, 0.01749, 0.01762, 0.01762, 0.01830, 0.01830, 0.01902

    python -m experiments.e258_floor_task_draw_band
    python -m experiments.e258_floor_task_draw_band --json-out runs/e258_floor_task_draw_band.json

Four registered claims, the first three computed in the exploration that wrote this module and disclosed as
confirmatory:

- **W1 -- the floor is a draw at both cells.** Each cell's own task-draw span is at least **1.05x**. **Falsifier**: a
  cell whose floor spans less, i.e. a floor that is draw-stable.
- **W2 -- and the size effect is bigger than the draw.** The rise from cs 800's floor to cs 300's **exceeds each cell's
  own task-draw span**. **Falsifier**: the rise is smaller than either span, in which case "the floor rises as the
  circuit shrinks" is the draw rather than the size.
- **W3 -- but the quoted pair is at the top of its band.** `e217`'s cs-300 value (0.02978) is the **largest** of that
  cell's six draws, so the quoted size effect (measured against a cs-800 draw) sits at the top of the band rather than
  in it. **Falsifier**: it lies inside the middle half of its cell's draws.
- **W4 -- reported.** Both cells' draw tables, the band the size effect takes over draw pairs, and the resolution of
  the queued item (no run is needed, and why).

The exit code is the number of claims **REFUSED** because a cell carries fewer than three draws.

**What it cannot do**: the draws are the corpus's own and are unevenly distributed (six at cs 300, eight at cs 800, and
one at cs 400/support 40), so the two bands are estimated from different numbers of draws; the draws vary `seeds` and
`seed0` together, so "task draw" here mixes the seed count with the seed offset; cs 400/support 40 has a **single**
`real` draw, so the middle rung of the ladder cannot be given a band at all; the `rho`-sweep artifacts at both cells
are excluded because a different `rho` is a different task geometry and not another draw of the same one; and the
excesses are `e2_topology_gap`'s own, so a code epoch between them is invisible here (`e227`).
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

REF_RHO = 0.9
CELLS = ((800, 80), (300, 30))
# the artifact whose cs-300 floor this record quotes -- named, so W3 is a question about THAT draw and not about
# whichever draw happens to be largest (taking the maximum made the claim vacuous)
QUOTED_ARTIFACT = "e217_ladder_cs300.json"
CLAIMS = (
    ("W1", "the floor is a draw at both cells",
     "Each cell's own task-draw span is at least 1.05x",
     "falsifier: a cell whose floor spans less [confirmatory, computed in the exploration that wrote this module]"),
    ("W2", "and the size effect is bigger than the draw",
     "The rise from cs 800's floor to cs 300's exceeds each cell's own task-draw span",
     "falsifier: the rise is smaller than either span, so the rise is the draw and not the size [confirmatory]"),
    ("W3", "but the quoted pair is at the top of its band",
     "e217's cs-300 value is the largest of that cell's draws, so the quoted size effect sits at the top of the band",
     "falsifier: it lies inside the middle half of its cell's draws [confirmatory]"),
)


def draws(root: Path = Path("runs")) -> dict:
    """Every `real` draw at the chosen cells at the reference `rho`, keyed by cell."""
    out: dict = {c: [] for c in CELLS}
    for p in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        cfg = d.get("config") or {}
        cell = (cfg.get("circuit_size"), cfg.get("support"))
        if cell not in out:
            continue
        rho = cfg.get("rho", REF_RHO)
        rho = REF_RHO if rho is None else float(rho)
        if round(rho, 4) != REF_RHO:
            continue
        a = (((d.get("topologies") or {}).get("real") or {}).get("diagonal(EWC)") or {}).get("analytic") or {}
        v = a.get("excess_mean")
        if isinstance(v, (int, float)):
            out[cell].append({"artifact": Path(p).name, "seeds": cfg.get("seeds"), "seed0": cfg.get("seed0"),
                              "q": cfg.get("q"), "excess": float(v)})
    return out


def span(vals: list[float]) -> float:
    return max(vals) / min(vals) if len(vals) > 1 and min(vals) > 0 else float("nan")


def judge(d: dict) -> list[dict]:
    out: list[dict] = []
    if any(len(d[c]) < 3 for c in CELLS):
        return [{"id": cid, "verdict": f"REFUSED -- a cell carries fewer than three draws ({ {str(c): len(d[c]) for c in CELLS} })"}
                for cid, *_ in CLAIMS]

    hi, lo = [r["excess"] for r in d[CELLS[0]]], [r["excess"] for r in d[CELLS[1]]]
    span_hi, span_lo = span(hi), span(lo)
    measured = (f"cs 800/support 80 spans {span_hi:.3f}x over {len(hi)} draws ({min(hi):.5f} to {max(hi):.5f}); "
                f"cs 300/support 30 spans {span_lo:.3f}x over {len(lo)} draws ({min(lo):.5f} to {max(lo):.5f})")
    out.append({"id": "W1", "measured": measured,
                "verdict": "MET -- the floor is a draw at both cells" if min(span_hi, span_lo) >= 1.05 else
                           "FALSIFIER FIRED -- a floor is draw-stable"})

    rise_min = min(lo) / max(hi)          # the smallest honest rise: the smallest cs-300 draw over the largest cs-800
    rise_max = max(lo) / min(hi)
    biggest_span = max(span_hi, span_lo)
    out.append({"id": "W2",
                "measured": f"the rise runs {rise_min:.3f}x to {rise_max:.3f}x over draw pairs against the largest "
                            f"task-draw span {biggest_span:.3f}x",
                "verdict": "MET -- the size effect is bigger than either cell's own draw" if rise_min > biggest_span else
                           "FALSIFIER FIRED -- the rise is inside the draw"})

    quoted = next((r for r in d[CELLS[1]] if r["artifact"] == QUOTED_ARTIFACT), None)
    if quoted is None:
        out.append({"id": "W3", "verdict": f"REFUSED -- {QUOTED_ARTIFACT} is not among the cell's draws"})
        return out
    ordered = sorted(r["excess"] for r in d[CELLS[1]])
    n = len(ordered)
    rank = ordered.index(quoted["excess"]) + 1
    out.append({"id": "W3",
                "measured": f"the quoted cs-300 floor is {quoted['excess']:.5f} from {quoted['artifact']} "
                            f"(seeds {quoted['seeds']}, seed0 {quoted['seed0']}), rank {rank} of {n} "
                            f"and {quoted['excess'] / min(ordered):.3f}x over the smallest",
                "verdict": "MET -- it is the largest of its cell's draws" if rank == n else
                           "FALSIFIER FIRED -- it lies inside the middle half" if rank <= (3 * n) // 4 else
                           "null band -- above the middle half but not the largest"})
    return out


def report(d: dict) -> int:
    print("== the floor's task-draw band at `rho` 0.9: every `real` draw the corpus carries ==")
    for c in CELLS:
        vals = [r["excess"] for r in d[c]]
        print(f"   cs {c[0]}/support {c[1]}: {len(vals)} draws, span {span(vals):.3f}x" if vals else
              f"   cs {c[0]}/support {c[1]}: no draws")
        for r in sorted(d[c], key=lambda r: -r["excess"]):
            print(f"      {r['artifact']:44} seeds={r['seeds']:>3} seed0={str(r['seed0']):>4} excess {r['excess']:.5f}")

    print("\n== the size effect over draw pairs, and the band that replaces the quoted point ==")
    hi, lo = [r["excess"] for r in d[CELLS[0]]], [r["excess"] for r in d[CELLS[1]]]
    if hi and lo:
        print(f"   smallest honest rise (smallest cs-300 draw over the largest cs-800): "
              f"{min(lo):.5f} / {max(hi):.5f} = {min(lo) / max(hi):.3f}x")
        print(f"   largest rise      (largest cs-300 draw over the smallest cs-800): "
              f"{max(lo):.5f} / {min(hi):.5f} = {max(lo) / min(hi):.3f}x")
        q = max(d[CELLS[1]], key=lambda r: r["excess"])
        print(f"   the record's quoted pair: cs 300 {q['excess']:.5f} against cs 800 0.01830 = "
              f"{q['excess'] / 0.0183:.3f}x")

    print("\n== the queued item, resolved ==")
    print("   the `support_draw.fingerprint_sha1` convention belongs to the runners that take `--support-seed` (the")
    print("   overlap suite: e198's census finds 137 artifacts with a live support draw and 8 identifying it). The")
    print("   ladder runs have no such flag -- their supports are drawn from the connectome from the task seeds -- so")
    print("   `(seeds, seed0, q)` IS the draw's identity and the draws that vary it are already on disk. No new run is")
    print("   needed, and the numbers above are what it would have bought.")

    print("\n== the registered claims, W1-W3 ==")
    j = judge(d)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the draws vary `seeds` and `seed0` together, cs 400/support 40 carries a single `real` draw so the")
    print("    middle rung gets no band, and the rho-sweep artifacts are excluded as different task geometries)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    d = draws(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": [list(c) for c in CELLS], "reference_rho": REF_RHO,
                                   "draws": {f"{c[0]}/{c[1]}": d[c] for c in CELLS},
                                   "claims": judge(d)})
        print(f"wrote {args.json_out}")
    return report(d)


if __name__ == "__main__":
    sys.exit(main())
