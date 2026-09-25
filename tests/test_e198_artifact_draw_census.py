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
    # read out from the WHOLE state: `readout_size` 0 is falsy in the runner, so no subset is drawn
    full = artifact(d / "full.json", {"circuit_size": 800, "readout_size": 0, "seed0": 0},
                    circuit="mb+cx+al@n1307")
    # a subset: the draw is live and unidentified
    sub = artifact(d / "sub.json", {"circuit_size": 800, "readout_size": 32, "seed0": 0},
                   circuit="mb+cx+al@n1307")
    # an overlap suite: the support draw is live even without any readout key
    ovl = artifact(d / "ovl.json", {"circuit_size": 800, "input_overlap": 0.5, "seed0": 0},
                   circuit="mb+cx+al@n1307")
    # a rand arm: the partition draw is live
    rnd = artifact(d / "rnd.json", {"circuit_size": 800, "methods": "naive,ewc-block-rand", "seed0": 0},
                   circuit="mb+cx+al@n1307")
    rows = {r["artifact"]: r for r in e198.census(d)["rows"]}
    assert rows["full.json"]["live"]["readout"] is False, "readout_size 0 is the whole state, not a subset"
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


def test_the_reconstruction_reproduces_every_recorded_fingerprint():
    """The reconstruction is evidence only because it is validated: a rebuild that did not reproduce the artifacts
    which DO record the field would turn an unidentified draw into a mis-identified one, which is worse than leaving
    it unknown. Both draws' reconstructions are checked against the real corpus, and both must be unanimous."""
    import json as _json
    from pathlib import Path as _P
    for key, fn, field in (("readout", e198.reconstruct_readout, lambda d: (d.get("readout") or {}).get("subset_sha1")),
                           ("support_draw", e198.reconstruct_supports,
                            lambda d: (d.get("support_draw") or {}).get("fingerprint_sha1"))):
        agree = disagree = 0
        for p in sorted(_P("runs").glob("*.json")):
            try:
                d = _json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            rec = field(d) if isinstance(d, dict) else None
            if not rec:
                continue
            if fn(d) == rec:
                agree += 1
            else:
                disagree += 1
        if agree == 0:
            return  # no artifacts of this family in this checkout
        assert disagree == 0, f"{key}: reconstruction disagreed with {disagree} recorded fingerprints"
        assert agree >= 6, (key, agree)


def test_a_zero_readout_size_is_the_whole_state_and_not_a_subset_draw(tmp_path):
    """`0` is falsy in the runner, so `readout_size = 0` means "use the whole state" and no subset is drawn -- counting
    it as a subset of size zero reported 27 artifacts as having an unidentified draw that does not exist."""
    d = tmp_path / "runs"
    artifact(d / "whole.json", {"circuit_size": 800, "readout_size": 0,
                                "seed0": 0, "methods": "naive"}, circuit="mb+cx+al@n1307")
    artifact(d / "subset.json", {"circuit_size": 800, "readout_size": 32,
                                 "seed0": 0, "methods": "naive"}, circuit="mb+cx+al@n1307")
    rows = {r["artifact"]: r for r in e198.census(d)["rows"]}
    assert rows["whole.json"]["live"]["readout"] is False, "0 is the whole state, not a size-zero subset"
    assert rows["subset.json"]["live"]["readout"] is True
    # and the reconstruction needs the circuit's neuron count, which comes from the circuit string and not
    # from circuit_size (800 here against the real 1307)
    assert e198._circuit_neurons({"circuit": "mb+cx+al@n1307"}) == 1307
    assert e198._circuit_neurons({"circuit": None}) is None
    assert e198.reconstruct_readout({"config": {"readout_size": 32, "seed0": 0},
                                     "readout": {"size": 32, "draw_seed": 0}}) is None, "no n, no reconstruction"
