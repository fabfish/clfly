"""`e144`'s reader has to combine a *three-draw* control, and the combination is the registered claim.

Rule 10 says the matched-random control is the **population** of size-matched partitions and one draw is one
sample from it, so the contrast is `ewc-block` minus the mean of K control draws and its variance has **two**
components: the between-draw one (K − 1 degrees of freedom) and the ordinary paired one. The failure modes worth
a test are the two that would flatter the result:

  * **a single draw must reproduce the old arithmetic exactly** — with K = 1 the draw component is zero and the
    sem is the paired sem, so a one-draw control cannot silently gain precision from this code;
  * **the draw term must *inflate* the error rather than be averaged away** — a code path that reported the
    paired component alone would quote a smaller sigma for the same data, which is the defect the flag exists to
    remove;
  * and a missing artifact must read as missing, with no verdict printed from it.
"""

from __future__ import annotations

import json
import math

import numpy as np

from experiments import e144_basis_harder_family as e144


def _arm(values, acc=0.9):
    v = np.array(values, dtype=float)
    return {"forgetting": v, "accuracy": np.full(len(v), acc), "sem": 0.01,
            "final_accuracy": acc, "n": len(v)}


def _draw(change, sem):
    return {"change": change, "sem": sem, "sigma": abs(change) / sem if sem else float("nan"),
            "n": 40, "negative": 20}


def test_one_draw_reproduces_the_paired_arithmetic_exactly():
    got = e144.combine_draws([_draw(-0.0125, 0.0060)])
    assert got["k_draws"] == 1 and got["draw_sd"] == 0.0
    assert got["sem_draw_component"] == 0.0
    assert math.isclose(got["sem_total"], 0.0060, rel_tol=1e-12)


def test_the_draw_term_inflates_the_error_rather_than_being_averaged_away():
    """Three draws whose means disagree add a term the paired component does not contain."""
    draws = [_draw(-0.0125, 0.0060), _draw(+0.0020, 0.0060), _draw(-0.0040, 0.0060)]
    got = e144.combine_draws(draws)
    paired_only = math.sqrt(np.mean([d["sem"] ** 2 for d in draws]) / 3)
    assert got["sem_paired_component"] == paired_only
    assert got["sem_total"] > paired_only                     # the draw term is present and positive
    assert got["draw_df"] == 2
    # and with the draw sd reported, the reader can see which component dominates
    assert got["draw_sd"] > 0 and got["sem_draw_component"] > 0


def test_the_verdicts_read_the_combined_sigma_and_a_missing_arm_prints_none():
    arms = {"naive": _arm([0.10] * 4), "ewc": _arm([0.09] * 4), "ewc-block": _arm([0.05] * 4),
            "ewc-block-rand": None}
    # no draws at all -> not decidable
    assert "verdict" in e144.verdicts(arms, None)
    # a strong, consistent contrast holds; a null fires the falsifier
    strong = [_draw(-0.0300, 0.0060), _draw(-0.0270, 0.0060), _draw(-0.0330, 0.0060)]
    v = e144.verdicts(arms, strong)
    assert v["P1_holds"] and not v["falsifier_fires"]
    nul = [_draw(+0.0010, 0.0060), _draw(-0.0020, 0.0060), _draw(+0.0005, 0.0060)]
    v = e144.verdicts(arms, nul)
    assert not v["P1_holds"] and v["falsifier_fires"]


def test_a_missing_artifact_reads_as_missing(tmp_path):
    assert e144.load(tmp_path / "absent.json", "ewc-block") is None
    (tmp_path / "partial.json").write_text(json.dumps({"methods": {"naive": {"replicates": [
        {"mean_forgetting": 0.1, "final_accuracy": 0.9, "forgetting_sem": 0.01,
         "final_accuracy": 0.9}]}}}), encoding="utf-8")
    assert e144.load(tmp_path / "partial.json", "ewc-block") is None
    assert e144.load(tmp_path / "partial.json", "naive")["n"] == 1
