"""The declared domain of the pooled spread claims, in one place.

`e252` declared a domain for the spread story and `e255`/`e256` then drew the cells it flagged, which left the rule
living in a module of its own while the three readers it applies to (`e244`, `e246`, `e247`) knew nothing about it --
and the lesson of that session was that **an instrument whose subject is a property of the record's DESIGN loses that
subject as the record improves, so a verdict must not be able to leave the table quietly.** The domain belongs in the
readers, so it lives here and both they and `e252` take it from here.

    a cell is IN the domain when every family measured there scatters by at most `T` across its own drawings

At `T = 4` the corpus splits into six or seven in-domain cells and two or three out (the `rho` 0.98 and 0.99 cells at
cs 300 and the `rho` 0.95 to 0.99 cells at cs 800, whose families scatter by 9x to 32x), and the rule is stable for
every `T` from the largest in-domain scatter to the smallest out-of-domain one -- a 9.6x window, which is what `e252`
measured and what its D1 fired on when the registration drew its bar from a rounded print.

**What it cannot do**: the rule is about **scatter**, not about `rho`, so it excludes a cell that scatters for any
other reason -- intended, and empirical; it is applied per group's cell, so a cell can be in the domain for one reader
and contribute nothing to another; and a `T` is a convention inside that 9.6x window rather than a tested boundary.
"""

from __future__ import annotations

from pathlib import Path

#: The scatter bar a cell's families must stay under.
T = 4.0


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
    return inside, set(cells) - inside


def corpus(root: Path = Path("runs"), t: float = T) -> tuple[set, set]:
    """The in- and out-of-domain cells of the corpus on disk.

    `e247`'s reader is imported here rather than at module scope: it is the module that turns artifacts into the
    per-cell structure the rule is about, and importing it above would make every reader that takes this rule --
    `e244`, `e246` and `e247` itself -- a cycle.
    """
    from experiments.e247_count_matched_spread import per_cell

    return domain(cell_scatters(per_cell(root)), t)


def inside_cells(root: Path = Path("runs"), t: float = T) -> set:
    """The in-domain cells of the corpus on disk, for a reader that wants to filter itself."""
    return corpus(root, t)[0]


def filter_gs(gs: list[dict], inside: set) -> list[dict]:
    """`e244`/`e246`'s group list, restricted to the in-domain cells."""
    return [g for g in gs if g["cell"] in inside]


def filter_fam(fam: dict, inside: set) -> dict:
    """`e247`'s per-cell structure, restricted to the in-domain cells."""
    return {f: {c: d for c, d in rows.items() if c in inside} for f, rows in fam.items()}


def statement(claims_all: list[dict], claims_domain: list[dict]) -> str:
    """The two-column sentence a reader prints when asked: which of its claims the domain changes.

    `claims_all` are the rows the reader's own `judge` returns on the whole corpus and `claims_domain` the rows it
    returns on the in-domain cells only. A claim whose id is missing from the filtered rows counts as changed, so a
    claim that leaves the table rather than turning over is reported as a change rather than disappearing.
    """
    after = {r["id"]: r["verdict"] for r in claims_domain}
    moved = [r["id"] for r in claims_all if after.get(r["id"]) != r["verdict"]]
    inside = "; ".join(f"{r['id']} {after[r['id']].split(' -- ')[0]}" for r in claims_domain)
    lines = [f"   inside the declared domain ({len(after)} of {len(claims_all)} claims read here): "
             + (inside or "none of them -- the filter leaves this reader no group"),
             "   outside it the same claims read: "
             + "; ".join(f"{r['id']} {r['verdict'].split(' -- ')[0]}" for r in claims_all)]
    lines.append(f"   -> the domain changes {len(moved)} of {len(claims_all)}: {', '.join(moved)}" if moved
                 else f"   -> the domain changes none of the {len(claims_all)} claims")
    return "\n".join(lines)
