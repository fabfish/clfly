"""`e230` asks whether the task geometry's rank contrast is larger than the family's own drawing scatter -- an audit
of a claim made one fire earlier, with the artifacts that claim came from.

The pattern it established on the live corpus: **every** family is resolvable at cs 300 (rho contrasts of 7.68x-25.25x
against within-`rho` scatters of 1.06x-2.98x) while at cs 800 the `alloy1` family's twelve drawings span 16.44x, more
than the 3.01x contrast the record read off its single-drawing cells -- so a bigger circuit buys a *volatile* one-sided
task geometry, which is the same direction the *penalty* side already showed (3.34x over five drawings). The exit code
counts unresolvable-and-undeclared families, so a family whose volatility is known is a precondition rather than a
surprise.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e230_rank_draw_census as e230


def art(name: str, size: int, rho: float | None, topo: str, rank: float, excess: float = 0.02,
        rewire_seed: int = 0) -> tuple[str, dict]:
    cfg = {"circuit_size": size, "support": 30, "seeds": 3, "seed0": 0, "q": 0.02, "rewire_seed": rewire_seed}
    if rho is not None:
        cfg["rho"] = rho
    payload = {"config": cfg,
               "topologies": {topo: {"geometry": {"effective_rank": rank, "chance_alignment": 1.0,
                                                  "all_pairs_alignment": 0.5},
                                     "diagonal(EWC)": {"analytic": {"excess_mean": excess}}}}}
    return name, payload


def write(tmp_path: Path, files: list[tuple[str, dict]]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for name, payload in files:
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_the_within_scatter_is_measured_across_drawings_at_one_rho_and_size(tmp_path):
    root = write(tmp_path, [art("a.json", 800, 0.9, "alloy1", 2.0, rewire_seed=0),
                            art("b.json", 800, 0.9, "alloy1", 8.0, rewire_seed=1),
                            art("c.json", 800, 0.99, "alloy1", 12.0)])
    fam = e230.families(e230.rows_of(root))[0]
    assert fam["topology"] == "alloy1" and fam["drawings_at_ref"] == 2
    assert abs(fam["within_at_ref"] - 4.0) < 1e-12
    # one of the two rho groups has a single drawing, so there is no "as the record read it" contrast to compute --
    # and the reader must say so rather than divide by that one cell and call it a contrast
    assert fam["between_single"] is None
    assert abs(fam["between_mean"] - 12.0 / 5.0) < 1e-12, "the mean spelling is computable and is the other column"


def test_a_contrast_inside_the_familys_own_scatter_is_not_resolvable(tmp_path):
    """The live cs-800 `alloy1` shape: twelve drawings spanning 16x, and a single-drawing contrast of 3x."""
    files = [art(f"d{i}.json", 800, 0.9, "alloy1", 2.0 if i == 0 else 32.0, rewire_seed=i) for i in range(12)]
    files += [art("p5.json", 800, 0.5, "alloy1", 60.0), art("p99.json", 800, 0.99, "alloy1", 20.0)]
    fam = e230.families(e230.rows_of(write(tmp_path, files)))[0]
    assert fam["within_at_ref"] == 16.0 and abs(fam["between_single"] - 3.0) < 1e-12
    assert fam["resolvable"] is False
    assert e230.DECLARED_UNRESOLVABLE, "the live table declares this family"


def test_an_unresolvable_family_that_is_not_declared_is_the_exit_code(tmp_path, capsys):
    files = [art(f"d{i}.json", 999, 0.9, "alloy1", 2.0 if i == 0 else 32.0, rewire_seed=i) for i in range(3)]
    files += [art("p5.json", 999, 0.5, "alloy1", 4.0), art("p99.json", 999, 0.99, "alloy1", 5.0)]
    root = write(tmp_path, files)
    assert e230.main(["--runs", str(root)]) == 1
    assert "NOT RESOLVABLE AND NOT DECLARED" in capsys.readouterr().out


def test_a_resolvable_family_with_a_wide_between_contrast_passes():
    """The audit is down to five auditable families and the widest contrast left among them is cs 800 `real`'s 5.6x
    against a 1.01x scatter: the ladder families have all left its scope as their cells were drawn, which is what
    happens to a design that reads single-drawing cells."""
    fams = {(f["circuit_size"], f["topology"]): f for f in e230.families(e230.rows_of())}
    assert fams[(800, "real")]["resolvable"] is True
    assert fams[(800, "real")]["between_single"] > 5 * fams[(800, "real")]["within_at_ref"]
    # cs 300 alloy1 was declared unresolvable at 1.51x against a 2.73x scatter, and e255's low-rho drawings put it
    # back INSIDE the audit: every rho group there now has two drawings, so the as-read column is undefined for it and
    # the verdict is read off means instead
    # since the 21:00 fold the VERDICT is the means column: cs 300 alloy1 is RESOLVABLE on its means (12.11 against
    # 2.73) while its as-read column, which e255's drawings emptied, carries no verdict at all
    f = fams[(300, "alloy1")]
    assert f["between_single"] is None and f["as_read_resolvable"] is None, f
    assert f["resolvable"] is True, f
    assert all(g["n"] >= 2 for g in f["rho_groups"].values()), f["rho_groups"]
    assert all(x["resolvable"] is None or x["between_mean"] is not None for x in fams.values()),         "a verdict implies a contrast"


def test_the_live_corpus_has_only_declared_unresolvable_families():
    """The gate: the audit must be green because every family it cannot resolve is declared with its scatter -- three
    of them now, since `e255` drew the low-rho end and un-declared two."""
    fams = e230.families(e230.rows_of())
    unres = {(f["circuit_size"], f["topology"]) for f in fams if f["resolvable"] is False}
    assert unres == set(e230.DECLARED_UNRESOLVABLE), (unres, set(e230.DECLARED_UNRESOLVABLE))
    assert e230.main([]) == 0


def test_the_cs_800_ladder_families_are_judged_on_their_means():
    """`e243`'s three designed drawings once made this family the audit's margin-narrowing example, and `e256` then
    drew every remaining cs-800 rho cell so its as-read column went undefined. Since the 21:00 fold the verdict comes
    from the means instead, and this family is RESOLVABLE there -- 50.54x against its own 8.02x scatter -- which is the
    question the audit was built to ask and could not ask for one session."""
    fams = {(f["circuit_size"], f["topology"]): f for f in e230.families(e230.rows_of())}
    f = fams[(800, "inalloy1")]
    assert f["between_single"] is None and f["as_read_resolvable"] is None, f
    assert f["resolvable"] is True and f["between_mean"] > 4 * f["within_at_ref"], f
    assert f["within_at_ref"] > 4.0, "the family's own scatter is still what e243 widened"
