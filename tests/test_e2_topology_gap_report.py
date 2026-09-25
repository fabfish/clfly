from __future__ import annotations

from experiments import e2_topology_gap as e2


def geom(align: float = 0.05, chance: float = 0.0555) -> dict:
    return {"geometry": {"consecutive_alignment": align, "all_pairs_alignment": align,
                         "chance_alignment": chance, "flattening": 0.1, "effective_rank": 10.0,
                         "top_eig_share": 0.3, "mean_rank": 50.0, "mean_rank_fraction": chance}}


def armed(excess: float, realized: bool = False) -> dict:
    arm = {"analytic": {"excess_mean": excess, "excess_sem": 0.001, "excess_per_seed": [excess, excess + 0.001]}}
    if realized:
        arm["realized"] = {"excess_mean": excess, "excess_sem": 0.002}
    return arm


def test_a_screening_run_reports_its_own_topologies_and_no_verdict_it_did_not_measure(capsys):
    """The defect this test pins: a `--geometry-only` run's levels are `swap8`/`swap16`/..., none of which is in
    `TOPOLOGY_ORDER`, so the report's table came out EMPTY -- and the monotonicity lines printed `monotone=YES`
    because `all()` over an empty list is True. A verdict produced by an empty sequence is not a measurement."""
    results = {"topologies": {"swap8": geom(0.091), "swap16": geom(0.041), "swap32": geom(0.0416),
                              "swap64": geom(0.036)}}
    e2.report(results)
    out = capsys.readouterr().out
    assert "swap8" in out and "swap64" in out, "the report must print the artifact's own topologies"
    assert "geometry-only" in out
    assert "monotone=" not in out, "no monotonicity verdict when no arm was computed"
    assert "NOT available" in out


def test_a_single_topology_run_does_not_announce_an_ordering(capsys):
    """One point has no ordering, and `all()` over a one-element sequence is True for the same reason it is over an
    empty one. The report must say so rather than print a rising claim."""
    results = {"topologies": {"real": {**geom(0.0056), "diagonal(EWC)": armed(0.0183),
                                       "bio:cell_class": armed(0.02), "rand:cell_class": armed(0.019)}}}
    e2.report(results)
    out = capsys.readouterr().out
    assert "monotone=" not in out
    assert "NOT COMPUTED" in out
    assert "0.01830" in out, "and the single topology's own numbers are still printed"


def test_an_armed_run_prints_a_row_per_topology_and_the_monotonicity_readings(capsys):
    """The positive control: with arms present the table carries the penalty columns and the monotonicity section
    is computed -- so the guards above cannot be satisfied by a report that prints nothing."""
    def cell(align: float, excess: float) -> dict:
        return {**geom(align), "diagonal(EWC)": armed(excess), "bio:cell_class": armed(excess + 0.001),
                "rand:cell_class": armed(excess - 0.001)}
    results = {"topologies": {"real": cell(0.0056, 0.0183), "swap0.5": cell(0.0218, 0.0232),
                              "swap2": cell(0.0603, 0.0124), "erdos_renyi": cell(0.2904, 0.1419)}}
    e2.report(results)
    out = capsys.readouterr().out
    assert "monotone=YES" in out or "monotone=no" in out
    for name in ("real", "swap0.5", "swap2", "erdos_renyi"):
        assert name in out
    assert "adjacent-contrast significance" in out
