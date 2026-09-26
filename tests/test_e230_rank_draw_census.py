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
    """The widest rho contrast left on the live corpus is cs 800 `inalloy1`'s 45x, against a 8x scatter -- and cs 300
    `alloy1`, whose 25x contrast this audit once called resolvable, is NOT any more: `e253`'s second drawing at rho
    0.95 and 0.98 collapsed it to 1.51x, inside its own 2.73x scatter."""
    fams = {(f["circuit_size"], f["topology"]): f for f in e230.families(e230.rows_of())}
    assert fams[(800, "inalloy1")]["resolvable"] is True
    assert fams[(800, "inalloy1")]["between_single"] > 5 * fams[(800, "inalloy1")]["within_at_ref"]
    assert fams[(300, "alloy1")]["resolvable"] is False
    assert fams[(300, "alloy1")]["between_single"] < fams[(300, "alloy1")]["within_at_ref"]


def test_the_live_corpus_has_only_declared_unresolvable_families():
    """The gate: the audit must be green because every family it cannot resolve is declared with its scatter -- five
    of them since `e253` added a second drawing at two cs-300 rho values."""
    fams = e230.families(e230.rows_of())
    unres = {(f["circuit_size"], f["topology"]) for f in fams if f["resolvable"] is False}
    assert unres == set(e230.DECLARED_UNRESOLVABLE), (unres, set(e230.DECLARED_UNRESOLVABLE))
    assert e230.main([]) == 0


def test_the_cs_800_inalloy_family_is_resolvable_which_is_what_the_directional_claim_needs():
    """The side of the cs-800 directional reading that has to hold: the collapsing family must beat its own scatter.
    `e243`'s three designed drawings widened this family's own scatter from 4.14x to 8.02x, so the margin is 5.6x
    where it was 10.8x -- still resolvable, and the narrowing is the point of pinning it here."""
    fams = {(f["circuit_size"], f["topology"]): f for f in e230.families(e230.rows_of())}
    f = fams[(800, "inalloy1")]
    assert f["resolvable"] is True, f
    assert f["within_at_ref"] > 4.14, "the designed drawings must have widened the scatter, or this pin is stale"
    assert f["between_single"] > 5 * f["within_at_ref"], f
