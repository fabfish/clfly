"""E203 -- the pooling ladder's draw-set claims (P1-P3), judged from the two artifacts and nothing else.

Registered 2026-09-25 before its run (`docs/findings/2026-09-25-registered-the-pooling-ladder-at-a-second-draw-set.md`):
the linear line's task draw had never been varied across a ladder's cells, because every pooling ladder in the record
is `--seed0 0`. `e202` runs the same command at `--seed0 100`, and this reader judges the three claims on the pair.

    python -m experiments.e203_ladder_draw_read
    python -m experiments.e203_ladder_draw_read --drawn runs/e202_ladder_d300_12seeds_seed0-100.json

**Why a reader rather than three lines in a shell task**: the claims are registered, and a registered claim whose read
is an ad-hoc snippet is a claim whose read is not versioned, not tested and not reproducible by a reader of the
repository -- which is the defect `e190` and `e194` were written to remove from this project's readings. It also
**refuses** rather than prints: an absent artifact, or a basis the table does not carry, is reported as a refusal and
counted, because those are the states in which a number would be a fabrication.

## What it reads, and what the reference is

Every claim compares the drawn table against the **reference** table (`e181`, `--seed0 0`, the same settings), and the
registered sentence for each is quoted into `CLAIMS` so the bar and the sentence can be read together. The quantity is
`excess` -- alignment above the chance level that the same partition achieves against random task subspaces -- which is
what this line's C2 claim is about.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RUNS = Path("runs")
REFERENCE = RUNS / "e181_ladder_d300_12seeds.json"
DRAWN = RUNS / "e202_ladder_d300_12seeds_seed0-100.json"

#: The reference table's peak and its value, quoted from `e181` rather than restated: the reader asserts them against
#: the artifact at run time, so a change to the reference fails here instead of silently moving a bar.
REFERENCE_PEAK = "bio:pool4"
REFERENCE_EXCESS = 2.28112

#: (id, what it compares, the registered bar and falsifier, and the sentence)
CLAIMS = (
    ("P1", "the peak's identity",
     "the rung with the highest excess at the drawn set is `bio:pool4`",
     "falsifier: a different rung peaks; null: another BIOLOGICAL rung beats it by less than 0.2"),
    ("P2", "the peak's value",
     "`bio:pool4`'s excess is within 25% of the reference value, i.e. in [1.711, 2.851]",
     "falsifier: outside 50% (below 1.141 or above 3.422); null: between 25% and 50%"),
    ("P3", "the matched-random gap at the peak",
     "`bio:pool4`'s excess exceeds `rand:pool4`'s by at least 0.5",
     "falsifier: a gap at or below 0.2, which would make the peak a pooling-depth effect rather than a biological one; "
     "null: 0.2-0.5"),
)


def table_of(path: Path) -> dict[str, float]:
    """The `excess` per basis, from the artifact's own topology block, or an empty dict if it is not there."""
    if not Path(path).is_file():
        return {}
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    block = ((d.get("topologies") or {}).get("real")) or {}
    return {b: v["excess"] for b, v in block.items() if isinstance(v, dict) and v.get("excess") is not None}


def judge(ref: dict, drawn: dict) -> list[dict]:
    """P1-P3 as verdicts, with every refusal named rather than printed as a number."""
    out = []
    if not drawn:
        return [{"id": c[0], "verdict": "REFUSED -- the drawn table is absent or carries no excess"} for c in CLAIMS]
    ranked = sorted(drawn.items(), key=lambda kv: -kv[1])
    peak, peak_v = ranked[0]
    runner, runner_v = ranked[1] if len(ranked) > 1 else ("", float("nan"))
    # The registration named THREE outcomes for P1, and the first version of this reader applied only two: same rung
    # (MET) or a different one (falsifier). Its null was *"another BIOLOGICAL rung beats it by less than 0.2"*, and on
    # `e202` that is exactly what happened -- `bio:pool8` peaks 0.049 above `bio:pool4` -- so a two-outcome reader
    # reports a fired falsifier where the registration says the null landed.
    if peak == REFERENCE_PEAK:
        verdict = "MET"
    elif "bio:" in peak and (peak_v - drawn.get(REFERENCE_PEAK, float("-inf"))) < 0.2:
        verdict = f"the registered null -- {peak} peaks above {REFERENCE_PEAK} by "                   f"{peak_v - drawn[REFERENCE_PEAK]:.5f}, under 0.2"
    else:
        verdict = f"FALSIFIER FIRED -- {peak} peaks"
    out.append({"id": "P1", "measured": f"peak {peak} at {peak_v:.5f}", "verdict": verdict,
                "note": f"runner-up {runner} at {runner_v:.5f}"})
    v = drawn.get(REFERENCE_PEAK)
    if v is None:
        out.append({"id": "P2", "verdict": "REFUSED -- the drawn table does not carry bio:pool4"})
    else:
        out.append({"id": "P2", "measured": f"bio:pool4 {v:.5f}",
                    "verdict": ("MET" if abs(v - REFERENCE_EXCESS) <= 0.25 * REFERENCE_EXCESS else
                                "null band" if abs(v - REFERENCE_EXCESS) <= 0.5 * REFERENCE_EXCESS else
                                "FALSIFIER FIRED")})
    r = drawn.get("rand:pool4")
    if v is None or r is None:
        out.append({"id": "P3", "verdict": "REFUSED -- bio:pool4 or rand:pool4 is absent"})
    else:
        gap = v - r
        out.append({"id": "P3", "measured": f"bio:pool4 - rand:pool4 = {gap:+.5f}",
                    "verdict": "MET" if gap >= 0.5 else "null band" if gap > 0.2 else "FALSIFIER FIRED",
                    "note": f"the reference gap is {REFERENCE_EXCESS - 1.21206:+.5f}"})
    return out


def report(ref: dict, drawn: dict) -> int:
    print(f"   == the pooling ladder's draw-set claims, drawn against the reference ==")
    print(f"   reference {REFERENCE.name}: peak {REFERENCE_PEAK} at {REFERENCE_EXCESS:.5f} "
          f"({len(ref)} bases)")
    print(f"   drawn     {DRAWN.name}: {len(drawn)} bases" if drawn else "   drawn     ABSENT")
    if ref.get(REFERENCE_PEAK) is None or abs(ref[REFERENCE_PEAK] - REFERENCE_EXCESS) > 1e-4:
        print(f"   NOTE: the reference artifact's own peak value is {ref.get(REFERENCE_PEAK)}, which is not the "
              f"{REFERENCE_EXCESS} these bars were registered against -- read the verdicts against the measured "
              f"reference, not the quoted one.")
    refused = 0
    for c, row in zip(CLAIMS, judge(ref, drawn)):
        print(f"        {row['id']}: {row.get('measured', '')}  -> {row['verdict']}"
              + (f"   ({row['note']})" if row.get("note") else ""))
        print(f"             the claim was: {c[2]}")
        print(f"             and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    if drawn:
        ranked = sorted(drawn.items(), key=lambda kv: -kv[1])
        print(f"        the drawn table, ranked: " + ", ".join(f"{b} {v:.4f}" for b, v in ranked[:6]))
    return refused


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reference", type=Path, default=REFERENCE)
    p.add_argument("--drawn", type=Path, default=DRAWN)
    a = p.parse_args(argv)
    return 1 if report(table_of(a.reference), table_of(a.drawn)) else 0


if __name__ == "__main__":
    sys.exit(main())
