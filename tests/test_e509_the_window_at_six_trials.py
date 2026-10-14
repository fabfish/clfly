"""Tests for `e509_the_window_at_six_trials`: the window table, the four claims' falsifiers, and the artifact's shape.

Every falsifier is driven on synthetic rolls, so a claim that cannot fail is caught here rather than by reading the
stored artifact; the live test only checks the shape the module promises and the bounds that have to grow with the
corpus. No test asserts a claim's own verdict on the real data.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments import e509_the_window_at_six_trials as e509

ARTIFACT = Path("runs/e509_the_window_at_six_trials.json")
#: the top-level keys the artifact may never carry, because a census would read them as a run's own configuration
FORBIDDEN = ("config", "env", "tasks")


def roll(value: float, label_at: int = 1, reps: int = 20, config=None, draw=None) -> dict:
    """One synthetic run's roll: a flat accuracy diagonal at ``value`` for every arm."""
    cfg = {"loop_label_at": label_at, "loop_episode": 6, "json_out": f"runs/x{label_at}.json",
           "save_theta": None, "lr": 0.003}
    cfg.update(config or {})
    env = {"episode_len": 6, "label_at": label_at, "tau": 12}
    env.update(draw or {})
    return {"artifact": f"x{label_at}.json",
            "arms": {a: {"replicates": reps, "accuracy_diagonal": [value] * reps, "accuracy_last": [0.5] * reps}
                     for a in e509.ARMS},
            "config": cfg, "env_draw": env}


def shares(values: dict | None = None, default: float = 0.05) -> dict:
    """A share instrument's own reading: every placement's share, keyed as the module keys them."""
    got = {key: {"share": default, "window": e509.WINDOW[key]} for key, _, _, _ in e509.PLACEMENTS}
    for key, value in (values or {}).items():
        got[key]["share"] = value
    return got


def reading(rolls: dict, share_values: dict | None = None, default_share: float = 0.05) -> dict:
    return e509._assemble(rolls, shares(share_values, default_share))


def flat(value: float = 0.30, label_at: int = 1) -> dict:
    """Every placement reading the same, which is the background the falsifiers are driven against."""
    return {key: roll(value, label_at) for key, _, _, _ in e509.PLACEMENTS}


def verdicts(r: dict) -> dict:
    return {row["id"]: row["verdict"] for row in e509.judge(r)}


#: the window each six-trial placement is claimed to carry, read from the pass's own arithmetic
SIX_WINDOWS = {"six_at1": 9, "six_at2": 7, "six_at3": 5}


def test_windows_are_the_six_trial_windows():
    for key, want in SIX_WINDOWS.items():
        trials, at = [(t, a) for k, t, a, _ in e509.PLACEMENTS if k == key][0]
        assert trials == 6
        assert e509.WINDOW[key] == want
        assert e509.WINDOW[key] == e509.window(trials, at) == (e509.TAU - 1) - at * (e509.TAU // trials)


def test_placements_cover_the_corpus_and_are_partitioned():
    keys = [k for k, _, _, _ in e509.PLACEMENTS]
    assert len(keys) == len(set(keys))
    #: the corpus grows, so the coverage is a bound and not an equality
    assert len(keys) >= 11
    assert set(e509.NEW) <= set(keys)
    assert set(e509.DISK) | set(e509.NEW) == set(keys)
    assert not set(e509.DISK) & set(e509.NEW)
    assert len(e509.NEW) == 3
    #: three pass lengths carry window 11 and two carry window 5, so those are the families with a spread
    assert len(e509.GROUPS[11]) >= 3
    assert len(e509.GROUPS[5]) >= 3


def test_claims_and_tests_are_registered():
    assert [c[0] for c in e509.CLAIMS] == ["YA1", "YA2", "YA3", "YA4"]
    for claim in e509.CLAIMS:
        assert len(claim) == 4 and claim[3].startswith("falsifier")
    #: YA2 tests the six-trial placements whose windows the corpus already carries
    assert set(e509.TESTS) == {("six_at2", 7), ("six_at3", 5)}
    assert all(k in e509.WINDOW and e509.WINDOW[k] == w for k, w in e509.TESTS)
    #: YA4's window pair shares a window, and the same-position pair does not
    assert e509.WINDOW[e509.SIX] == e509.WINDOW[e509.WINDOW_PAIR]
    assert all(e509.WINDOW[k] != e509.WINDOW[e509.SIX] for k in e509.SAME_POSITION)


def test_a_reading_carries_no_forbidden_top_level_key():
    r = reading(flat())
    for key in FORBIDDEN:
        assert key not in r
    #: the config and the draw are kept inside the spans, where the census does not read them as the run's own
    assert set(r) >= {"ok", "reason", "placements", "share", "recovery", "spans"}


def test_a_reading_refuses_every_claim_when_the_runs_are_absent():
    r = e509._assemble({key: None for key, _, _, _ in e509.PLACEMENTS}, {})
    assert r["ok"]
    assert r["spans"]["absent"]
    v = verdicts(r)
    assert set(v) == {"YA1", "YA2", "YA3", "YA4"}
    assert all("REFUSED" in text for text in v.values())


def test_reading_is_refused_whole_when_the_share_instrument_raises():
    def boom():
        raise OSError("no connectome")

    r = e509.reading(paths={}, shares_fn=boom)
    assert not r["ok"]
    assert "connectome" in r["reason"]
    assert all("REFUSED" in row["verdict"] for row in e509.judge(r))


def test_each_falsifier_can_fire_on_synthetic_data():
    #: YA1 -- one config field outside the placement pair and the bookkeeping moved
    rolls = flat()
    rolls["six_at2"]["config"]["lr"] = 0.01
    assert "FALSIFIER FIRED" in verdicts(reading(rolls))["YA1"]
    #: YA1 -- a draw field added beyond the placement
    rolls = flat()
    rolls["six_at2"]["env_draw"]["world_leak"] = 0.5
    assert "FALSIFIER FIRED" in verdicts(reading(rolls))["YA1"]
    #: YA1 -- a replicate count other than twenty
    rolls = flat()
    rolls["six_at3"] = roll(0.30, reps=10)
    assert "FALSIFIER FIRED" in verdicts(reading(rolls))["YA1"]
    #: YA2 -- the six-trial window-5 placement read far from its window's family
    rolls = {k: roll(0.30) for k, _, _, _ in e509.PLACEMENTS}
    rolls["six_at3"] = roll(0.20)
    assert "FALSIFIER FIRED" in verdicts(reading(rolls))["YA2"]
    #: YA3 -- a six-trial ladder that does not fall
    assert "FALSIFIER FIRED" in verdicts(reading(flat(), {"six_at1": 0.02, "six_at2": 0.03,
                                                          "six_at3": 0.04}))["YA3"]
    #: YA3 -- a six-trial share outside the factor from its window's family
    v = verdicts(reading(flat(), {"six_at1": 0.9, "six_at2": 0.9, "six_at3": 0.9}))
    assert "FALSIFIER FIRED" in v["YA3"]
    #: YA4 -- the six-trial trial-2 placement read nearer a same-position placement than its window's
    rolls = {k: roll(0.30) for k, _, _, _ in e509.PLACEMENTS}
    rolls[e509.WINDOW_PAIR] = roll(0.20)
    rolls[e509.SIX] = roll(0.30)
    rolls[e509.SAME_POSITION[0]] = roll(0.29)
    assert "FALSIFIER FIRED" in verdicts(reading(rolls))["YA4"]
    #: YA4 -- the window-9 point outside the band its neighbouring windows bound
    rolls = {k: roll(0.30) for k, _, _, _ in e509.PLACEMENTS}
    rolls[e509.NINE] = roll(0.90)
    assert "FALSIFIER FIRED" in verdicts(reading(rolls))["YA4"]


def test_each_falsifier_can_stay_shut_on_synthetic_data():
    """The same driver with the readings the claim wants, so a falsifier that always fires is caught too."""
    #: window 11 spread 0.02 across its three pass lengths and window 5 spread 0.01 across its two, so the
    #: registered bound is 0.02; the six-trial window-7 and window-5 placements read inside their families and the
    #: window-9 point between the window-8 placement and the window-11 family
    rolls = {k: roll(0.30) for k, _, _, _ in e509.PLACEMENTS}
    rolls["two_at0"], rolls["three_at0"], rolls["four_at0"] = roll(0.31), roll(0.32), roll(0.33)
    rolls["two_at1"], rolls["four_at2"] = roll(0.30), roll(0.29)
    rolls["three_at2"] = roll(0.27)
    rolls["six_at1"], rolls["six_at2"], rolls["six_at3"] = roll(0.32), roll(0.31), roll(0.30)
    sh = {"six_at1": 0.09, "six_at2": 0.05, "six_at3": 0.04,
          "three_at1": 0.048, "two_at1": 0.038, "four_at2": 0.036}
    v = verdicts(reading(rolls, sh))
    assert "FALSIFIER FIRED" not in v["YA1"]
    assert "FALSIFIER FIRED" not in v["YA2"]
    assert "FALSIFIER FIRED" not in v["YA3"]
    assert "FALSIFIER FIRED" not in v["YA4"]


def test_live_artifact_shape_and_bounds():
    """The stored artifact, if it is there: shape and the counts that have to grow with the corpus."""
    if not ARTIFACT.is_file():
        pytest.skip(f"{ARTIFACT} is absent")
    doc = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for key in FORBIDDEN:
        assert key not in doc
    assert set(doc) >= {"ok", "placements", "share", "recovery", "spans", "claims"}
    assert [row["id"] for row in doc["claims"]] == ["YA1", "YA2", "YA3", "YA4"]
    for row in doc["claims"]:
        assert "verdict" in row and "measured" in row
    spans = doc["spans"]
    #: one row per placement on disk, so the table's size is a bound and not a constant
    assert len(spans["accuracy_diagonal"]) >= len(e509.PLACEMENTS)
    assert len(spans["windows"]) >= len(e509.PLACEMENTS)
    assert set(e509.NEW) <= set(spans["windows"])
    assert set(spans["windows"]) >= {k for k, _, _, _ in e509.PLACEMENTS}
    assert spans["bound"] is None or spans["bound"] >= 0.0
    #: the shares and the two comparisons are carried, since YA3 and YA4 read them
    assert isinstance(spans["share"], dict)
    assert isinstance(doc["recovery"].get("pairs"), dict)
