from __future__ import annotations

import json
from pathlib import Path

from experiments import e198_artifact_draw_census as e198


def artifact(path: Path, config: dict, **blocks) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"config": config, **blocks}), encoding="utf-8")
    return path


def test_a_draw_is_live_only_when_the_configuration_makes_it_so(tmp_path):
    """The false-alarm class `e126`'s preamble is about: a checker that reports everything gets ignored. An artifact
    read out from EVERY neuron has no subset to identify, an artifact without an overlap suite has no support draw,
    and an artifact without a `*-rand` arm has no partition draw."""
    d = tmp_path / "runs"
    # read out from the whole circuit: no subset draw exists
    full = artifact(d / "full.json", {"circuit_size": 800, "readout_size": 800})
    # a subset: the draw is live and unidentified
    sub = artifact(d / "sub.json", {"circuit_size": 800, "readout_size": 32})
    # an overlap suite: the support draw is live even without any readout key
    ovl = artifact(d / "ovl.json", {"circuit_size": 800, "input_overlap": 0.5})
    # a rand arm: the partition draw is live
    rnd = artifact(d / "rnd.json", {"circuit_size": 800, "methods": "naive,ewc-block-rand"})
    rows = {r["artifact"]: r for r in e198.census(d)["rows"]}
    assert rows["full.json"]["live"]["readout"] is False, "the whole circuit is not a subset draw"
    assert rows["sub.json"]["live"]["readout"] is True
    assert rows["sub.json"]["recorded"]["readout"] is None
    assert rows["ovl.json"]["live"]["support_draw"] is True
    assert rows["rnd.json"]["live"]["partition_draw"] is True
    assert rows["sub.json"]["live"]["support_draw"] is False
    assert rows["ovl.json"]["live"]["partition_draw"] is False


def test_a_fingerprint_counts_as_identified_and_a_null_one_does_not(tmp_path):
    """`e168`'s distinction is between an artifact that does not CARRY the field and one that carries a null: both are
    unidentified, and neither is the same as carrying a fingerprint. The field's presence is what the runner added."""
    d = tmp_path / "runs"
    cfg = {"circuit_size": 800, "input_overlap": 0.5}
    artifact(d / "absent.json", cfg)
    artifact(d / "nulled.json", cfg, support_draw=None)
    artifact(d / "present.json", cfg, support_draw={"draw_seed": 1, "fingerprint_sha1": "abc123"})
    rows = {r["artifact"]: r for r in e198.census(d)["rows"]}
    assert rows["absent.json"]["recorded"]["support_draw"] is None
    assert rows["nulled.json"]["recorded"]["support_draw"] is None, "a null block is unidentified, not identified"
    assert rows["present.json"]["recorded"]["support_draw"] == "abc123"
    assert e198.report({"rows": list(rows.values()), "unreadable": []}) == 0


def test_the_live_census_reproduces_e168s_count_on_the_real_corpus():
    """The census's second draw was measured by `e168` at **31** artifacts that ran a `*-rand` arm and cannot say
    which partition they drew. If this census disagrees with a number the corpus already published, one of the two is
    wrong -- and it is the cross-check that distinguishes a census from a script."""
    res = e198.census(Path("runs"))
    if not res["rows"]:
        return  # no artifacts in this checkout
    un = [r for r in res["rows"] if r["live"]["partition_draw"] and not r["recorded"]["partition_draw"]]
    assert len(un) == 31, f"e168 published 31; this census counts {len(un)}"
    assert any(r["live"]["support_draw"] for r in res["rows"]), "the overlap family should be present"
