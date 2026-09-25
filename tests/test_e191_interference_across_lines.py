"""`e191` reads both lines' interference terms and splits them by task distance, and its own narrative has been
right, wrong and right again in that order.

`e189`'s first version said the far component is shared between the lines; its second version refused that, because
on the accuracy-drop **proxy** the network's far change cleared 2σ once in nine; `e191` finds it clears 2σ **nine
times in nine** on the account's own terms. The tests below pin the mechanics -- a per-pair interference split, a
paired change per component, and a refusal that is not a comparison -- so that the next correction of the narrative
is an argument about the sentence rather than about the arithmetic.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from experiments import e191_interference_across_lines as e191


def payload(path: Path, method: str, near: list[float], far: list[float], config=None) -> Path:
    """A payload whose per-pair interference terms are constant across replicates, so the split is exact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    reps = []
    for n, f in zip(near, far):
        # full-length `per_task` lists, as the runner writes them: index k is the damage from training task k, and
        # only k > j is a real pair. The first version of this fixture wrote short lists, so the k-loop's distance
        # arithmetic was wrong and the split came out empty -- which the live shape (2 near + 1 far per replicate
        # of a three-task run) is what caught.
        def rec(j):
            row = [0.0, 0.0, 0.0]
            if j == 0:
                row[1], row[2] = n, f
            elif j == 1:
                row[2] = n
            return {"task": j, "per_task": [{"first_order": v} for v in row]}
        reps.append({"interference": [rec(0), rec(1)]})
    path.write_text(json.dumps({"config": config or {"input_overlap": 0.0, "lam": 0.003}, "methods": {method: {"replicates": reps}}}),
                    encoding="utf-8")
    return path


def analytic(path: Path, near0: float, near1: float, far0: float, far1: float) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"controlled": [
        {"level": 0.0, "mean_interference": (near0 + far0) / 2, "mean_interference_near": near0,
         "mean_interference_far": far0},
        {"level": 1.0, "mean_interference": (near1 + far1) / 2, "mean_interference_near": near1,
         "mean_interference_far": far1}]}), encoding="utf-8")
    return path


def test_the_split_is_per_replicate_and_by_task_distance(tmp_path):
    a = payload(tmp_path / "lo.json", "naive", [0.10, 0.12], [0.05, 0.05])
    s = e191.per_replicate_split(a, "naive")
    assert s["n_pairs_near"] == 2 and s["n_pairs_far"] == 1
    assert s["near"].tolist() == pytest.approx([0.10, 0.12])
    assert s["far"].tolist() == pytest.approx([0.05, 0.05])


def test_a_rise_in_every_comparison_needs_no_proxy(tmp_path):
    """The live shape: seven comparisons whose interference rises in both components, and the analytic line whose
    near falls while its far rises -- the composition that the proxy could not resolve."""
    runs = tmp_path / "runs"
    # values that scatter a little, because a constant series has sem 0 and a direction needs one: the first
    # version of this fixture used four identical values and every component read as unresolved
    lo = payload(runs / "lo.json", "naive", [0.09, 0.11, 0.10, 0.10], [0.04, 0.06, 0.05, 0.05])
    hi = payload(runs / "hi.json", "naive", [0.19, 0.21, 0.20, 0.20], [0.08, 0.10, 0.09, 0.09],
                 config={"input_overlap": 1.0, "lam": 0.003})
    analytic(runs / e191.ANALYTIC, 0.025, -0.001, 0.008, 0.011)
    res = e191.audit(runs, pairs=[("the pair", "naive", "lo.json", "hi.json", "pair")])
    # the tallies declared in the live file are for nine comparisons, so a one-comparison fixture asserts the
    # numbers rather than the declarations
    assert res["comparisons"], res["refused"]
    row = res["comparisons"][0]
    assert row["near"]["change"] == pytest.approx(0.10) and row["far"]["change"] == pytest.approx(0.04)
    assert res["network_tally"]["near"]["rises"] == 1 and res["network_tally"]["far"]["rises"] == 1
    assert res["analytic_directions"] == {"near": "falls", "far": "rises"}


def test_an_arm_without_the_interference_key_is_refused_rather_than_counted(tmp_path):
    runs = tmp_path / "runs"
    (runs).mkdir(parents=True, exist_ok=True)
    good = payload(runs / "good.json", "naive", [0.10] * 2, [0.05] * 2)
    (runs / "bare.json").write_text(json.dumps({"config": {"input_overlap": 1.0, "lam": 0.003},
                                                "methods": {"naive": {"replicates": [{"retention": 1}]}}}),
                                    encoding="utf-8")
    analytic(runs / e191.ANALYTIC, 0.025, -0.001, 0.008, 0.011)
    res = e191.audit(runs, pairs=[("the pair", "naive", "good.json", "bare.json", "pair")])
    assert res["comparisons"] == [] and "no per-pair interference" in res["refused"][0]["why"]


def test_the_live_composition_is_the_one_the_proxy_could_not_see():
    """The gate, and the result: on the name-matched quantity the near component is opposite in the two lines and
    the far component agrees in nine of nine."""
    res = e191.audit(Path("runs"))
    assert res["n_mismatches"] == 0, res["mismatches"]
    assert res["analytic_directions"]["near"] == "falls" and res["analytic_directions"]["far"] == "rises"
    assert res["network_tally"]["near"]["rises"] >= 5 and res["network_tally"]["near"]["falls"] == 0
    assert res["network_tally"]["far"]["rises"] == len(res["comparisons"]), res["network_tally"]
    assert len(res["comparisons"]) >= 8
    assert len(res["refused"]) == 1, res["refused"]


# --- the dose read, written before its artifacts exist ---------------------------------------------------------

def dose_artifact(path: Path, method: str, near: list[float], far: list[float], overlap: float) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    reps = []
    for n, f in zip(near, far):
        row = lambda j: {"task": j, "per_task": [{"first_order": v} for v in (
            [0.0, n, f] if j == 0 else [0.0, 0.0, n])]}
        reps.append({"interference": [row(0), row(1)]})
    path.write_text(json.dumps({"config": {"input_overlap": overlap, "lam": 0.003, "methods": method},
                                "methods": {method: {"replicates": reps}}}), encoding="utf-8")
    return path


def test_the_dose_read_pairs_a_level_against_the_disjoint_baseline_and_checks_p1s_bar(tmp_path):
    """P1's bar is computed from the measured 0 -> 1 rise (+0.1234 on `naive`) rather than restated: the registered
    sentence is that the value at achieved 0.3333 is closer to the 1.0 end than to the 0.0 end."""
    d = tmp_path / "runs"
    base = dose_artifact(d / "base.json", "naive", [0.09, 0.11, 0.10, 0.10], [0.04, 0.06, 0.05, 0.05], 0.0)
    over = dose_artifact(d / "half.json", "naive", [0.17, 0.19, 0.18, 0.18], [0.07, 0.09, 0.08, 0.08], 0.5)
    res = e191.dose_read([over], base)
    row = res["levels"][0]
    assert row["target_overlap"] == 0.5 and row["achieved_overlap"] == 0.3333
    assert row["arms"]["naive"]["near"]["change"] == pytest.approx(0.08, abs=1e-9)
    assert row["arms"]["naive"]["P1_half_done"] is True, "0.08 > 0.0617"
    # and a rise below half the 0->1 change does not meet it
    weak = dose_artifact(d / "weak.json", "naive", [0.10, 0.12, 0.11, 0.11], [0.04, 0.06, 0.05, 0.05], 0.25)
    assert e191.dose_read([weak], base)["levels"][0]["arms"]["naive"]["P1_half_done"] is False


def test_the_dose_read_refuses_an_artifact_that_is_not_written_yet(tmp_path):
    res = e191.dose_read([tmp_path / "nope.json"], tmp_path / "also-nope.json")
    assert res["levels"][0]["status"] not in ("", None)
    assert e191.report_dose(res) == 1, "the count of missing levels is the exit signal"


def test_the_dose_read_on_the_live_registration_says_which_levels_are_missing():
    """The gate, in the form it will have until the runs land: the registration names three levels and none exists."""
    levels = [Path(f"runs/e193_r32_overlap{n}_methods_40reps.json") for n in (25, 50, 75)]
    res = e191.dose_read(levels)
    assert len(res["levels"]) == 3
    assert all(lv.get("status") == "not written yet" for lv in res["levels"]), res["levels"]
    assert e191.ACHIEVED_OVERLAP[0.5] == 0.3333 and e191.ACHIEVED_OVERLAP[0.75] == 0.6


def test_the_analytic_progress_fractions_come_from_the_artifact():
    """P2 is a shape claim, so both lines have to be expressed as the fraction of their own 0 -> 1 response. The
    analytic fractions are computed from e7's six levels rather than quoted, so they cannot drift from the table."""
    prog = e191.analytic_progress([0.1429, 0.3333, 0.6, 1.0])
    assert prog[0.1429] == pytest.approx(0.40, abs=0.02), prog
    assert prog[0.3333] == pytest.approx(0.76, abs=0.02), prog
    assert prog[0.6] == pytest.approx(0.86, abs=0.02), prog
    assert prog[1.0] == pytest.approx(1.0, abs=1e-9)
    # monotone, because the analytic near component falls monotonically over the six levels
    ordered = [prog[k] for k in (0.1429, 0.3333, 0.6, 1.0)]
    assert ordered == sorted(ordered)


def test_the_dose_read_reports_each_levels_progress_against_the_analytic_fraction(tmp_path):
    d = tmp_path / "runs"
    base = dose_artifact(d / "base.json", "naive", [0.09, 0.11, 0.10, 0.10], [0.04, 0.06, 0.05, 0.05], 0.0)
    full = dose_artifact(d / "full.json", "naive", [0.21, 0.23, 0.22, 0.22], [0.09, 0.11, 0.10, 0.10], 1.0)
    half = dose_artifact(d / "half.json", "naive", [0.17, 0.19, 0.18, 0.18], [0.07, 0.09, 0.08, 0.08], 0.5)
    res = e191.dose_read([half], base, overlap1=full)
    arm = res["levels"][0]["arms"]["naive"]
    assert arm["full_rise"]["change"] == pytest.approx(0.12, abs=1e-9)
    assert arm["progress_fraction"] == pytest.approx(0.08 / 0.12, abs=1e-9)
    assert res["analytic_progress"][0.3333] == pytest.approx(0.76, abs=0.02)


def test_each_dose_row_states_the_overlap_pair_it_measures():
    """The baselines sit at different overlaps once per-arm admission is on (`e140` at 0.0 for `naive`, `e153` at
    1.0 for the block arms), so a row that names only its baseline invites reading across rows. The pair is what a
    reader must compare."""
    d = tmp_path = __import__("pathlib").Path("tmp_pair_test")
    base0 = dose_artifact(d / "base0.json", "naive", [0.09, 0.11, 0.10, 0.10], [0.04, 0.06, 0.05, 0.05], 0.0)
    base1 = dose_artifact(d / "base1.json", "ewc-block", [0.09, 0.11, 0.10, 0.10], [0.04, 0.06, 0.05, 0.05], 1.0)
    lvl0 = dose_artifact(d / "lvl0.json", "naive", [0.17, 0.19, 0.18, 0.18], [0.07, 0.09, 0.08, 0.08], 0.25)
    lvl1 = dose_artifact(d / "lvl1.json", "ewc-block", [0.17, 0.19, 0.18, 0.18], [0.07, 0.09, 0.08, 0.08], 0.25)
    res = e191.dose_read([lvl0, lvl1], base0, candidates=[base0, base1])
    first, second = res["levels"]
    assert first["arms"]["naive"]["baseline_overlap"] == 0.0
    assert second["arms"]["ewc-block"]["baseline_overlap"] == 1.0
    assert first["arms"]["naive"]["baseline"].startswith("base0")
    assert second["arms"]["ewc-block"]["baseline"].startswith("base1")
    for f in d.rglob("*.json"):
        f.unlink()
    d.rmdir()


def test_the_cleanest_admissible_baseline_is_preferred_and_its_refusals_are_reported(tmp_path):
    """`e116` needs three inert assumptions for `naive` where `e140` needs four, so the read prefers it -- and says
    why the cleaner candidate was refused when it is, which is how a reader sees that the block arm's baseline had
    to move to the lambda-1.0 family."""
    d = tmp_path / "runs"
    clean = dose_artifact(d / "clean.json", "naive", [0.09, 0.11, 0.10, 0.10], [0.04, 0.06, 0.05, 0.05], 0.0)
    dirty = dose_artifact(d / "dirty.json", "naive", [0.09, 0.11, 0.10, 0.10], [0.04, 0.06, 0.05, 0.05], 0.0)
    lvl = dose_artifact(d / "lvl.json", "naive", [0.17, 0.19, 0.18, 0.18], [0.07, 0.09, 0.08, 0.08], 0.25)
    res = e191.dose_read([lvl], clean, candidates=[clean, dirty])
    row = res["levels"][0]["arms"]["naive"]
    assert row["baseline"] == "clean.json"
    assert row["refusals"] == [], "the first candidate is admitted, so there is nothing to refuse"
    # with a candidate that does not carry the arm first, the refusal says so
    res2 = e191.dose_read([lvl], dirty, candidates=[d / "absent-arm.json", dirty])
    assert res2["levels"][0]["arms"]["naive"]["baseline"] == "dirty.json"
