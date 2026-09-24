"""`e169` validates rule 47 with a clock the timestamps cannot influence, so the test has to pin both clocks.

The smaller-keyset-first invariant is only a *test* of a clock if a violation is possible, so the first test
builds a synthetic pair that each clock orders differently and checks that the two orderings disagree. The rest
pin the corpus's own answer: **write time has three violations, start time has none**, and the three are the
corpus's longest runs — a test that let both clocks pass, or both fail, would destroy the unit's content.
"""

from __future__ import annotations

import pytest

from experiments import e169_start_time_dating as e169


def row(name, keys, mtime, duration):
    return {"name": name, "keys": set(keys), "mtime": mtime, "duration": duration,
            "payload": {"timing_s": duration}, "start": mtime - duration}


def test_start_time_is_the_write_time_less_the_duration():
    r = row("a", ["x"], 1000.0, 400.0)
    assert e169.start_time(r) == 600.0


def test_a_run_is_only_in_scope_when_its_config_is_a_parser_dump():
    ok = {"config": {f"k{i}": i for i in range(25)}, "payload": {"timing_s": 10.0, "methods": {}}}
    assert e169.in_scope(ok)
    # a hand-built summary: a small config, which this method must refuse rather than date
    small = {"config": {f"k{i}": i for i in range(12)}, "payload": {"timing_s": 10.0, "methods": {}}}
    assert not e169.in_scope(small)
    # an aggregate with no per-arm results and no duration is not a run at all
    assert not e169.in_scope({"config": {f"k{i}": i for i in range(30)}, "payload": {}})


def test_the_two_clocks_can_disagree_and_the_invariant_names_the_loser():
    """A four-hour run written after a one-hour run whose config gained a key in between."""
    long_run = row("long", ["a", "b", "c"], mtime=14 * 3600, duration=4 * 3600)     # started at 10:00
    later = row("later", ["a", "b", "c", "d"], mtime=11.5 * 3600, duration=1.5 * 3600)  # started at 10:00
    later["start"] = 10.5 * 3600                                                    # started 10:30
    assert e169.nested_violations([long_run, later], "mtime")["violations"]
    assert not e169.nested_violations([long_run, later], "start")["violations"]


def test_pairs_too_close_to_order_are_counted_as_neither():
    a = row("a", ["a"], mtime=100.0, duration=50.0)
    b = row("b", ["a", "b"], mtime=130.0, duration=20.0)   # started 30 s after a
    res = e169.nested_violations([a, b], "start")
    assert res["ties"] == 1 and not res["violations"] and res["ordered_correctly"] == 0


def test_the_corpus_answers_zero_for_start_time_and_three_for_write_time():
    from experiments.e103_reproducibility_audit import load_artifacts

    rows = [{"name": a["name"], "keys": set(a["config"]), "mtime": a["mtime"], "duration": a["payload"]["timing_s"],
             "payload": a["payload"]} for a in load_artifacts() if e169.in_scope(a)]
    for r in rows:
        r["start"] = e169.start_time(r)
    # 129 artifacts and 5,263 nested pairs when this unit was written; the corpus grows, so the count is a floor
    # and the *identity* below is the part that must hold at any size -- both clocks order the same pair set, so
    # every pair write time gets wrong is one start time gets right.
    assert len(rows) >= 129
    w = e169.nested_violations(rows, "mtime")
    s = e169.nested_violations(rows, "start")
    assert len(w["violations"]) == 3 and s["violations"] == []
    assert w["ordered_correctly"] + len(w["violations"]) == s["ordered_correctly"] >= 5263
    # the misplaced side is always the long run, and never the artifact whose config gained the key
    assert all(v["durations_h"][0] > v["durations_h"][1] for v in w["violations"])
    assert {v["earlier_keyset"] for v in w["violations"]} == {
        "e144_r32_overlap1_methods_40reps.json", "e140_r32_methods_plastic_40reps.json"}
    assert all(v["keys"][0] < v["keys"][1] for v in w["violations"])


def test_the_pair_rule_47_was_written_for_is_one_of_the_three():
    """`e144` bodies its own rand-draw siblings, which is how the reconstruction's epoch was fixed."""
    from experiments.e103_reproducibility_audit import load_artifacts

    rows = [{"name": a["name"], "keys": set(a["config"]), "mtime": a["mtime"], "duration": a["payload"]["timing_s"],
             "payload": a["payload"]} for a in load_artifacts() if e169.in_scope(a)]
    for r in rows:
        r["start"] = e169.start_time(r)
    pairs = {(v["earlier_keyset"], v["later_keyset"]) for v in e169.nested_violations(rows, "mtime")["violations"]}
    assert ("e144_r32_overlap1_methods_40reps.json", "e144_r32_overlap1_rand_draw1.json") in pairs
    assert ("e144_r32_overlap1_methods_40reps.json", "e144_r32_overlap1_rand_draw2.json") in pairs
    # and by start time both go the right way: the 29-key run began before either 30-key sibling
    by_name = {r["name"]: r for r in rows}
    assert (by_name["e144_r32_overlap1_methods_40reps.json"]["start"]
            < by_name["e144_r32_overlap1_rand_draw1.json"]["start"])
