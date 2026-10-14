"""Tests for `e510_the_shape_of_the_window_curve`: the window arithmetic, each falsifier's firing, and the artifact's
shape.

Every falsifier is driven on synthetic rolls, so a claim that cannot fail is caught here rather than by reading the
stored artifact; the live test only checks the shape the module promises and the counts that have to grow with the
corpus. No test asserts a claim's own verdict on the real data.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from experiments import e510_the_shape_of_the_window_curve as e510

ARTIFACT = Path("runs/e510_the_shape_of_the_window_curve.json")
#: the top-level keys the artifact may never carry, because a census would read them as a run's own configuration
FORBIDDEN = ("config", "env", "tasks")


def roll(value: float, reps: int = 20, phase: float = 0.0, jitter: float = 0.002) -> dict:
    """One synthetic run's roll: a per-replicate diagonal around ``value``, so a paired sigma is defined.

    The jitter is a phase-shifted sinusoid, so two placements at the same family value carry a small, non-zero spread
    of their own -- which is what lets a resolved fall and a kept-shut falsifier both be driven.
    """
    diag = [value + jitter * math.sin(2.0 * math.pi * (i + phase) / reps) for i in range(reps)]
    return {"artifact": f"synth_{value:.4f}.json",
            "arms": {a: {"replicates": reps, "accuracy_diagonal": list(diag), "accuracy_last": [value] * reps}
                     for a in e510.ARMS},
            "config": {}, "env_draw": {}}


def ladder(by_window: dict, override: dict | None = None) -> dict:
    """One synthetic roll per placement: each placement takes its window's family value, then the override.

    ``override`` sets an individual placement, which is how a family wider than the registered bound is built without
    moving the family's own pooled value.
    """
    out = {}
    for i, (key, _, _, _) in enumerate(e510.PLACEMENTS):
        out[key] = roll(by_window[e510.WINDOW[key]], phase=i)
    for key, value in (override or {}).items():
        out[key] = roll(value, phase=list(k for k, _, _, _ in e510.PLACEMENTS).index(key))
    return out


def verdicts(r: dict) -> dict:
    return {row["id"]: row["verdict"] for row in e510.judge(r)}


#: the ladder the "stay shut" driver wants: a graded fall whose every adjacent share is under a half, and whose floor
#: windows (7, 5 and 3) sit inside the chance band
GRADED = {11: 0.80, 9: 0.55, 8: 0.40, 7: 0.33, 5: 0.29, 3: 0.24}


def test_windows_and_cues_are_the_pass_arithmetic():
    for key, trials, at, _ in e510.PLACEMENTS:
        assert e510.WINDOW[key] == e510.window(trials, at) == (e510.TAU - 1) - at * (e510.TAU // trials)
        assert e510.CUES[key] == e510.cues_after(trials, at) == trials - 1 - at
    #: the ladder is the corpus's six windows, ordered from the largest to the smallest
    assert e510.LADDER == (11, 9, 8, 7, 5, 3)
    assert set(e510.GROUPS) == set(e510.LADDER)
    for w in e510.LADDER:
        assert e510.GROUPS[w] == [k for k, _, _, _ in e510.PLACEMENTS if e510.WINDOW[k] == w]


def test_placements_cover_the_corpus_as_bounds_and_are_partitioned():
    keys = [k for k, _, _, _ in e510.PLACEMENTS]
    assert len(keys) == len(set(keys))
    #: the corpus grows, so the coverage is a bound and not an equality
    assert len(keys) >= 11
    assert len(set(e510.WINDOW.values())) >= 6
    #: windows 11, 7 and 5 are each carried by more than one pass length, so they are the families ZA4 reads
    assert set(e510.MULTI) == {k for k, _, _, _ in e510.PLACEMENTS if len(e510.GROUPS[e510.WINDOW[k]]) >= 2}
    assert {e510.WINDOW[k] for k in e510.MULTI} >= {11, 7, 5}
    #: an at-least-one-cue-after-the-label window varies by two, which is ZA4's second condition
    ranges = {w: max(e510.CUES[k] for k in e510.GROUPS[w]) - min(e510.CUES[k] for k in e510.GROUPS[w])
              for w in e510.LADDER}
    assert max(ranges.values()) >= 2


def test_claims_are_registered():
    assert [c[0] for c in e510.CLAIMS] == ["ZA1", "ZA2", "ZA3", "ZA4"]
    for claim in e510.CLAIMS:
        assert len(claim) == 4 and claim[3].startswith("falsifier")


def test_a_reading_carries_no_forbidden_top_level_key():
    r = e510._assemble(ladder(GRADED))
    for key in FORBIDDEN:
        assert key not in r
    assert set(r) >= {"ok", "reason", "placements", "spans"}


def test_each_claim_refuses_when_its_own_input_is_absent():
    #: nothing on disk: every claim refuses on its own input
    empty = e510._assemble({k: None for k, _, _, _ in e510.PLACEMENTS})
    assert empty["ok"]
    assert all("REFUSED" in text for text in verdicts(empty).values())
    #: four_at1 carries window 8, which ZA3 (the floor and window 11) and ZA4 (the multi-pass-length windows) do not
    #: need, but ZA1 and ZA2 pool the whole ladder and do
    gone = ladder(GRADED)
    gone["four_at1"] = None
    v = verdicts(e510._assemble(gone))
    assert "REFUSED" in v["ZA1"] and "REFUSED" in v["ZA2"]
    assert "REFUSED" not in v["ZA3"] and "REFUSED" not in v["ZA4"]


def test_each_falsifier_can_fire_on_synthetic_data():
    #: ZA1 -- a smaller window reading above the larger window above it by more than the window's own spread
    v = verdicts(e510._assemble(ladder({**GRADED, 3: 0.50})))
    assert "FALSIFIER FIRED" in v["ZA1"]
    #: ZA2 -- one adjacent fall carrying almost the whole fall from window 11 to window 3
    v = verdicts(e510._assemble(ladder({11: 0.95, 9: 0.25, 8: 0.24, 7: 0.23, 5: 0.22, 3: 0.21})))
    assert "FALSIFIER FIRED" in v["ZA2"]
    #: ZA3 -- a window at or below 7 reading more than the band above chance
    v = verdicts(e510._assemble(ladder({11: 0.80, 9: 0.58, 8: 0.45, 7: 0.40, 5: 0.30, 3: 0.24})))
    assert "FALSIFIER FIRED" in v["ZA3"]
    #: ZA3 -- window 11 reading within the band of chance
    v = verdicts(e510._assemble(ladder({11: 0.30, 9: 0.29, 8: 0.28, 7: 0.27, 5: 0.26, 3: 0.24})))
    assert "FALSIFIER FIRED" in v["ZA3"]
    #: ZA4 -- a multi-pass-length family wider than the registered bound, the family's own mean held
    wide = {"two_at1": 0.325, "four_at2": 0.255, "six_at3": 0.29}
    v = verdicts(e510._assemble(ladder(GRADED, override=wide)))
    assert "FALSIFIER FIRED" in v["ZA4"]


def test_each_falsifier_can_stay_shut_on_synthetic_data():
    """The same driver on a ladder the claim wants, so a falsifier that always fires is caught too."""
    v = verdicts(e510._assemble(ladder(GRADED)))
    assert "FALSIFIER FIRED" not in v["ZA1"]
    assert "FALSIFIER FIRED" not in v["ZA2"]
    assert "FALSIFIER FIRED" not in v["ZA3"]
    assert "FALSIFIER FIRED" not in v["ZA4"]


def test_live_artifact_shape_and_bounds():
    """The stored artifact, if it is there: shape and the counts that have to grow with the corpus."""
    if not ARTIFACT.is_file():
        pytest.skip(f"{ARTIFACT} is absent")
    doc = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for key in FORBIDDEN:
        assert key not in doc
    assert set(doc) >= {"ok", "placements", "spans", "claims"}
    assert [row["id"] for row in doc["claims"]] == ["ZA1", "ZA2", "ZA3", "ZA4"]
    for row in doc["claims"]:
        assert "verdict" in row and "measured" in row
    spans = doc["spans"]
    #: eleven placements over six windows, so the table's size is a bound and not a constant
    assert len(spans["accuracy_diagonal"]) >= len(e510.PLACEMENTS)
    assert len(spans["windows"]) >= len(e510.PLACEMENTS)
    assert set(spans["windows"]) >= {k for k, _, _, _ in e510.PLACEMENTS}
    assert len(spans["family"]) >= len(e510.LADDER)
    assert len(spans["fall"]) >= len(e510.LADDER) - 1
    assert spans["bound"] == pytest.approx(0.03125)
