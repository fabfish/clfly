"""E203 -- the pooling ladder's draw-set claims (P1-P3 and the band's Q1-Q3), judged from the artifacts and nothing else.

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

## And the band's own claims, which needed a second quantity

The third draw set's registration asked three further questions (`Q1`-`Q3` in `BAND_CLAIMS`), and judging them
exposed that this reader had been printing only **one** of the two gaps a ladder comparison can mean. `P3` compares the
peak rung with its **own size-matched control**; `Q1` compares the peak with the **best `rand:` rung of any size**.
They are different statements, and on the corpus they point different ways -- at draw set 100 the matched gap at the
*peak* is the largest of the three while the matched gap at the *named* rung is the smallest of its own three -- so
both are now printed per draw set, beside the count of biological rungs in the top eight. **The reader whose whole
purpose was to print the registered quantity had been printing a neighbouring one**, and the third draw set's
falsifier fired on the quantity it had never printed.
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


#: The band claims, registered for the THIRD draw set
#: (`docs/findings/2026-09-25-registered-a-third-draw-set-for-the-band.md` section 3), quoted rather than restated.
#: P1-P3 ask "did the claim survive"; these ask "how far does each rung move", and the two turned out to need different
#: quantities: **Q1 is about the peak's lead over the best `rand:` rung at all**, which the pairwise reader never
#: computed -- it computed the lead over the *same-sized* control -- while P1's band and Q1's decay are two different
#: statements about the same table.
BAND_CLAIMS = (
    ("Q1", "the biological advantage is present again",
     "At draw set 200 the peak's `excess` exceeds **every** `rand:` rung's by **at least 0.5**",
     "falsifier: a `rand:` rung comes within 0.2 of the peak, which would make the band a pooling-depth effect; "
     "null: a gap of 0.2-0.5, i.e. the advantage survives and shrank again"),
    ("Q2", "`bio:pool4` is the stable member of the band",
     "Its excess at draw set 200 lies within **25%** of its mean over draw sets 0 and 100 (2.16987), i.e. in "
     "**[1.627, 2.712]**",
     "falsifier: outside **50%** (below 1.085 or above 3.255); null: between 25% and 50%"),
    ("Q3", "the head's value stays in a band of half a unit",
     "The **span of the peak's excess across the three draw sets** is **below 0.5**",
     "falsifier: a span at or above **1.0**; null: between 0.5 and 1.0"),
)

#: the mean of `bio:pool4` over draw sets 0 and 100, quoted from the registration, and asserted against the tables
Q2_PRIOR_MEAN = 2.16987
Q2_PRIOR_BAND = ("bio:pool4", 0.25)


def band_numbers(tables: dict[str, dict]) -> list[dict]:
    """Per draw set, the two quantities the band claims turn on, plus the membership count they are stated about.

    `unmatched` is the peak's lead over the best `rand:` rung of any size -- Q1's quantity, which no earlier reader
    printed -- and `matched` is the lead over the peak rung's own size-matched control, which is what P3 registers.
    They are not comparable to each other, and at draw set 100 the matched gap at the *peak* is the largest of the
    three while the matched gap at the *named* rung is the smallest of its own three: once the peak moves, the peak
    and the named rung are different objects.
    """
    out = []
    for name, t in tables.items():
        if not t:
            continue
        ranked = sorted(t.items(), key=lambda kv: -kv[1])
        peak, peak_v = ranked[0]
        rands = [(b, v) for b, v in ranked if b.startswith("rand:")]
        best_rand = rands[0] if rands else (None, float("nan"))
        matched = t.get("rand:" + peak.split(":", 1)[-1], float("nan"))
        out.append({"draw": name, "peak": peak, "peak_v": peak_v, "best_rand": best_rand[0],
                    "best_rand_v": best_rand[1], "unmatched": peak_v - best_rand[1],
                    "matched": peak_v - matched,
                    "bio_in_top8": sum(1 for b, _ in ranked[:8] if b.startswith("bio:"))})
    return out


def judge_band(tables: dict[str, dict]) -> list[dict]:
    """Q1-Q3 as verdicts, refused rather than guessed when the tables a claim is stated over are not present.

    Q1 and Q2 are stated **at draw set 200**, which is the LAST table given; Q3 is stated over **the three draw
    sets**; Q2's band is a statement about the mean of the first two. So a run given two tables can compute Q3's
    two-draw span but must refuse Q1's and Q2's bars, and a run given one must refuse all three -- printing a number
    for a claim whose table is absent is the fabrication `e190` and `e194` exist to refuse.
    """
    live = {n: t for n, t in tables.items() if t}
    nums = band_numbers(live)
    if len(nums) < 3:
        return [{"id": c[0], "verdict": f"REFUSED -- {c[0]} is stated over three draw sets, {len(nums)} given"}
                for c in BAND_CLAIMS]
    third = nums[-1]
    out: list[dict] = []
    # Q1 -- the peak against EVERY rand: rung of any size
    gap = third["unmatched"]
    out.append({"id": "Q1", "measured": f"the peak {third['peak']} {third['peak_v']:.5f} against the best rand: rung "
                                         f"{third['best_rand']} {third['best_rand_v']:.5f} = {gap:+.5f}",
                "verdict": "MET" if gap >= 0.5 else "null band" if gap > 0.2 else "FALSIFIER FIRED"})
    # Q2 -- bio:pool4 within 25% of its mean over the first two draw sets
    known = [t for n, t in live.items()][:2]
    means = [t.get("bio:pool4") for t in known]
    if any(m is None for m in means):
        out.append({"id": "Q2", "verdict": "REFUSED -- bio:pool4 is absent from one of the first two draw sets"})
    else:
        mean = sum(means) / len(means)
        cur = [t for t in live.values()][-1].get("bio:pool4")
        off = abs(cur - mean) / mean if cur is not None else None
        note = f"the two-draw mean of bio:pool4 is {mean:.5f}"
        if abs(mean - Q2_PRIOR_MEAN) > 1e-4:
            note += f", which is not the {Q2_PRIOR_MEAN} the bar was registered against -- read the verdict against "\
                    f"the measured mean"
        out.append({"id": "Q2", "measured": f"bio:pool4 {cur:.5f}" if cur is not None else "",
                    "verdict": ("REFUSED -- bio:pool4 is absent from the third draw set" if cur is None else
                                "MET" if off <= Q2_PRIOR_BAND[1] else "null band" if off <= 0.5 else
                                "FALSIFIER FIRED"),
                    "note": note + (f"; off the mean by {off:.1%}" if off is not None else "")})
    # Q3 -- the span of the peak across the three
    peaks = [n["peak_v"] for n in nums]
    span = max(peaks) - min(peaks)
    out.append({"id": "Q3", "measured": f"the peaks {', '.join(f'{p:.5f}' for p in peaks)} span {span:.5f}",
                "verdict": "MET" if span < 0.5 else "null band" if span < 1.0 else "FALSIFIER FIRED"})
    return out


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


def across(tables: dict[str, dict]) -> None:
    """The per-rung values ACROSS the draw sets given, which is the view a band claim needs.

    `report`'s pairwise verdicts answer "did this claim survive"; a band claim asks "how far does each rung move", and
    that is a span over the tables rather than a comparison with one reference. Printed always, because two draw sets
    give a difference and three give a span -- and reading a difference as a span is what today's support-draw work
    had to unlearn.
    """
    # A table that is absent or empty contributes nothing and must not be counted as a draw set -- the refusal path
    # passes one, and `max()` over it raised rather than skipping.
    tables = {n: t for n, t in tables.items() if t}
    rungs = sorted({b for t in tables.values() for b in t})
    if len(tables) < 2 or not rungs:
        return
    names = list(tables)
    print()
    print(f"   == each rung across {len(names)} draw sets ({', '.join(names)}) ==")
    print(f"   {'rung':16} " + " ".join(f"{n[:14]:>14}" for n in names) + f" {'span':>9}  {'leader':>6}")
    for b in rungs:
        vals = [tables[n].get(b) for n in names]
        if any(v is None for v in vals):
            continue
        leader = names[max(range(len(names)), key=lambda i: vals[i])]
        print(f"   {b:16} " + " ".join(f"{v:14.5f}" for v in vals) + f" {max(vals) - min(vals):9.5f}  {leader:>6}")
    peaks = [max(t.items(), key=lambda kv: kv[1]) for t in tables.values()]
    print(f"   the peaks: " + ", ".join(f"{n} {p[0]} {p[1]:.5f}" for n, p in zip(names, peaks)))
    print(f"   the peak's span: {max(p[1] for p in peaks) - min(p[1] for p in peaks):.5f}   "
          f"(Q3's bar: below 0.5; falsifier at or above 1.0)")

    print()
    print("   == per draw set, the two gaps the band claims are about ==")
    print(f"   {'draw set':<26}{'peak':<14}{'value':>9}{'best rand:':>14}{'value':>9}"
          f"{'unmatched':>11}{'matched':>9}{'bio/8':>7}")
    for n in band_numbers(tables):
        print(f"   {n['draw']:<26}{n['peak']:<14}{n['peak_v']:>9.5f}{str(n['best_rand']):>14}"
              f"{n['best_rand_v']:>9.5f}{n['unmatched']:>+11.5f}{n['matched']:>+9.5f}{n['bio_in_top8']:>4} of 8")
    print("   `unmatched` is the peak against the best `rand:` rung of ANY size (Q1's quantity); `matched` is the")
    print("   lead over the peak rung's own size-matched control (P3's quantity). They are different statements and")
    print("   at draw set 100 they point different ways, which is why both are printed.")

    print()
    print("   == the band's registered claims, Q1-Q3 ==")
    for c, row in zip(BAND_CLAIMS, judge_band(tables)):
        print(f"        {row['id']}: {row.get('measured', '')}  -> {row['verdict']}"
              + (f"   ({row['note']})" if row.get("note") else ""))
        print(f"             the claim was: {c[2]}")
        print(f"             and its {c[3]}")


def report(ref: dict, drawn: dict, tables: dict | None = None) -> int:
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
    across(tables or {"reference": ref, "drawn": drawn})
    return refused


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reference", type=Path, default=REFERENCE)
    p.add_argument("--drawn", type=Path, action="append", default=None,
                   help="a draw set's artifact; repeatable, since a band claim is about how far each rung moves "
                        "ACROSS draw sets and not about one pair.")
    a = p.parse_args(argv)
    drawns = [Path(x) for x in a.drawn] if a.drawn else [DRAWN]
    tables = {Path(a.reference).stem.replace("e181_ladder_", ""): table_of(a.reference)}
    for d in drawns:
        tables[d.stem.replace("e204_ladder_", "").replace("e202_ladder_", "")] = table_of(d)
    first = table_of(drawns[0])
    return 1 if report(table_of(a.reference), first, tables) else 0


if __name__ == "__main__":
    sys.exit(main())
