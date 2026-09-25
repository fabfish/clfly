from __future__ import annotations

import json
from pathlib import Path

from experiments import e203_ladder_draw_read as e203


def art(path: Path, excess: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"topologies": {"real": {b: {"excess": v} for b, v in excess.items()}}}),
                    encoding="utf-8")
    return path


REF = {"bio:pool4": 2.28112, "bio:pool64": 1.71290, "rand:pool4": 1.21206}


def test_the_reader_refuses_rather_than_printing_a_number_without_its_artifact():
    """A registered claim whose read is a snippet is a claim whose read is not versioned; a reader that printed a
    verdict without the artifact would be worse -- the refusal is the point, and it is counted in the exit code."""
    assert e203.table_of(Path("runs/definitely-absent-artifact.json")) == {}
    assert e203.main(["--drawn", "runs/definitely-absent-artifact.json"]) == 1


def test_the_reader_calibrates_on_the_reference_against_itself(tmp_path):
    """Every bar was registered against `e181`'s table, so judging that table against itself must return all three
    MET -- a replication table its own subject fails would fire its falsifiers for the wrong reason."""
    ref = art(tmp_path / "ref.json", REF)
    drawn = art(tmp_path / "drawn.json", REF)
    row = e203.judge(e203.table_of(ref), e203.table_of(drawn))
    assert [r["verdict"] for r in row] == ["MET", "MET", "MET"], row


def test_each_claim_can_fire_and_the_null_bands_are_where_they_were_registered(tmp_path):
    """The bands are the registration's: P2's null is 25-50% away from 2.28112, i.e. outside [1.711, 2.851] and inside
    [1.141, 3.422], and P3's null is a gap of 0.2-0.5. The first version of this test asserted 1.9 was in the null --
    it is 17% below the reference, i.e. inside the bar, which is what the reader said."""
    ref = e203.table_of(art(tmp_path / "r.json", REF))
    inside = art(tmp_path / "i.json", {"bio:pool4": 1.9, "rand:pool4": 1.21206})
    v = e203.judge(ref, e203.table_of(inside))
    assert [r["verdict"] for r in v] == ["MET", "MET", "MET"], v
    null = art(tmp_path / "n.json", {"bio:pool4": 1.6, "rand:pool4": 1.0})
    w = e203.judge(ref, e203.table_of(null))
    assert w[0]["verdict"] == "MET", w[0]            # 1.6 is still the peak of this table
    assert w[1]["verdict"] == "null band", w[1]      # 0.68 away, between 25% and 50% of 2.28112
    assert w[2]["verdict"] == "MET", w[2]            # the gap is 0.6
    # another rung peaking fires P1, a value below 50% fires P2, and a small gap fires P3
    far = art(tmp_path / "f.json", {"bio:pool4": 1.0, "bio:pool64": 1.5, "rand:pool4": 0.95})
    x = e203.judge(ref, e203.table_of(far))
    assert x[0]["verdict"] == "FALSIFIER FIRED -- bio:pool64 peaks", x[0]
    assert x[1]["verdict"] == "FALSIFIER FIRED", x[1]   # 1.0 is below 1.141
    assert x[2]["verdict"] == "FALSIFIER FIRED", x[2]   # the gap is 0.05
