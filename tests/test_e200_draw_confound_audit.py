from __future__ import annotations

import json
from pathlib import Path

from experiments import e200_draw_confound_audit as e200


def art(path: Path, **config) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"config": config, "circuit": "mb+cx+al@n1307"}), encoding="utf-8")
    return path


def test_two_overlaps_at_the_SAME_seed_are_not_a_confound_even_though_their_fingerprints_differ(tmp_path):
    """The correction this audit needed. A support fingerprint bundles the draw with the MANIPULATION -- two artifacts
    at different target overlaps necessarily have different supports, because the overlap IS their construction --
    while using the same support draw. The first version compared fingerprints and flagged 19 of 19 pairs, including
    every level-against-its-baseline comparison whose whole point is that the overlaps differ."""
    d = tmp_path / "runs"
    base = art(d / "base.json", circuit_size=800, support=80, input_overlap=0.0, seed0=0, methods="naive")
    lvl = art(d / "lvl.json", circuit_size=800, support=80, input_overlap=0.5, seed0=0, methods="naive")
    row = e200.compare(base, lvl)
    assert row["per_draw"]["support_draw"] == "same draw", row
    assert row["verdict"] == "SAME DRAW", row
    # and the fingerprints DO differ, which is why they cannot be the test
    from experiments.e200_draw_confound_audit import draws_of, load
    fa, fb = draws_of(load(base)), draws_of(load(lvl))
    assert fa["support_draw"]["fingerprint"] != fb["support_draw"]["fingerprint"]


def test_a_different_support_SEED_is_a_confound(tmp_path):
    """`--support-seed` is not an inert field, so two artifacts differing in it are measured on different draws --
    which is a deliberate design in the replication's families and a confound in any comparison that claims to
    isolate the manipulation."""
    d = tmp_path / "runs"
    a = art(d / "ss0.json", circuit_size=800, support=80, input_overlap=0.5, seed0=0, methods="naive")
    b = art(d / "ss1.json", circuit_size=800, support=80, input_overlap=0.5, seed0=0, support_seed=1, methods="naive")
    row = e200.compare(a, b)
    assert row["per_draw"]["support_draw"] == "DIFFERENT DRAW", row
    assert row["verdict"] == "CONFOUNDED", row


def test_a_readout_draw_that_is_live_on_one_side_only_is_NOT_called_a_confound(tmp_path):
    """A draw that one side has and the other does not is not a difference between two draws; calling it one would be
    the same false alarm in the other direction. The read-out draw is live only for a SUBSET, and `0` is the runner's
    "whole state"."""
    d = tmp_path / "runs"
    whole = art(d / "whole.json", circuit_size=800, readout_size=0, seed0=0, methods="naive")
    sub = art(d / "sub.json", circuit_size=800, readout_size=32, seed0=0, methods="naive")
    row = e200.compare(whole, sub)
    assert row["per_draw"]["readout"] == "live on one side only", row
    assert row["verdict"] == "partly unidentified", row


def test_the_live_audit_finds_no_confounded_pair_in_the_corpus():
    """The corpus's own answer, on the real pairs: the declared two-point contrasts and the four dose families'
    level-against-baseline comparisons are all measured on the same draws. If a future run introduces a pair that
    differs in a draw *and* claims to isolate the manipulation, this is where it shows up."""
    res = e200.audit(Path("runs"))
    if not res["pairs"]:
        return
    assert len(res["pairs"]) >= 19, len(res["pairs"])
    conf = [r for r in res["pairs"] if r.get("verdict") == "CONFOUNDED"]
    assert conf == [], conf
