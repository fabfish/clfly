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
    # the registered null: another BIOLOGICAL rung peaks by less than 0.2 -- which is what `e202` did
    near = art(tmp_path / "nn.json", {"bio:pool4": 2.05, "bio:pool8": 2.10, "rand:pool4": 1.33})
    y = e203.judge(ref, e203.table_of(near))
    assert y[0]["verdict"].startswith("the registered null"), y[0]
    far = art(tmp_path / "f.json", {"bio:pool4": 1.0, "bio:pool64": 1.5, "rand:pool4": 0.95})
    x = e203.judge(ref, e203.table_of(far))
    assert x[0]["verdict"] == "FALSIFIER FIRED -- bio:pool64 peaks", x[0]
    assert x[1]["verdict"] == "FALSIFIER FIRED", x[1]   # 1.0 is below 1.141
    assert x[2]["verdict"] == "FALSIFIER FIRED", x[2]   # the gap is 0.05


def test_the_across_view_reports_each_rungs_span_and_the_peaks(tmp_path, capsys):
    """A band claim is about how far each rung MOVES across draw sets, not about one pair, so the reader prints the
    across view whenever it is given more than one table -- and two draw sets give a difference while three give a
    span, which is the distinction today's support-draw work had to unlearn."""
    a = art(tmp_path / "a.json", {"bio:pool4": 2.28, "bio:pool8": 1.45, "rand:pool4": 1.21})
    b = art(tmp_path / "b.json", {"bio:pool4": 2.06, "bio:pool8": 2.11, "rand:pool4": 1.34})
    tables = {"draw0": e203.table_of(a), "draw1": e203.table_of(b)}
    e203.across(tables)
    out = capsys.readouterr().out
    assert "each rung across 2 draw sets" in out, out
    assert "bio:pool8" in out and "0.66000" in out.replace("0.6600", "0.66000") or "0.66" in out, out
    assert "the peaks: draw0 bio:pool4 2.28000, draw1 bio:pool8 2.11000" in out, out
    assert "the peak's span: 0.17000" in out, out
    # one table is not a span and the view stays silent rather than printing a zero-width band
    capsys.readouterr()
    e203.across({"draw0": e203.table_of(a)})
    assert capsys.readouterr().out == ""

def tab(bio4=2.0, bio8=1.9, rand4=1.0, rand8=0.9, extra=None):
    """A ladder table built to order, for the band claims: the four rungs Q1-Q3 are stated about."""
    t = {"bio:pool4": bio4, "bio:pool8": bio8, "rand:pool4": rand4, "rand:pool8": rand8}
    t.update(extra or {})
    return t


def test_the_band_claims_refuse_until_three_draw_sets_are_given():
    """Q1 and Q2 are stated AT the third draw set and Q2's band is the mean of the first two, so a run given two
    tables can print Q3's two-draw span but must refuse the other two rather than invent their subject."""
    two = {"a": tab(), "b": tab(bio4=2.1)}
    rows = e203.judge_band(two)
    assert all("REFUSED" in r["verdict"] for r in rows), rows
    three = {"a": tab(), "b": tab(bio4=2.1), "c": tab(bio4=2.05)}
    assert [r["id"] for r in e203.judge_band(three)] == ["Q1", "Q2", "Q3"]


def test_q1_is_about_every_random_rung_and_not_the_size_matched_one():
    """The distinction the third draw set turned on: P3 compares the peak with its OWN size-matched control, Q1 with
    the best `rand:` rung of any size. A table whose matched control is far below but whose pool16 sits at the peak
    is the draw-set-200 shape, and the first version of this reader had no quantity that could see it."""
    close = {"a": tab(rand4=1.0), "b": tab(rand4=1.05),
             "c": tab(bio4=2.0, rand4=1.0, extra={"rand:pool16": 1.99})}
    rows = {r["id"]: r for r in e203.judge_band(close)}
    assert rows["Q1"]["verdict"] == "FALSIFIER FIRED", rows["Q1"]
    assert rows["Q2"]["verdict"] == "MET", rows["Q2"]
    far = {"a": tab(rand4=1.0), "b": tab(rand4=1.05), "c": tab(bio4=2.0, rand4=1.0)}
    assert {r["id"]: r for r in e203.judge_band(far)}["Q1"]["verdict"] == "MET"
    # and the null band is the registration's 0.2-0.5
    mid = {"a": tab(), "b": tab(bio4=2.1), "c": tab(bio4=2.0, rand4=1.0, extra={"rand:pool16": 1.75})}
    assert {r["id"]: r for r in e203.judge_band(mid)}["Q1"]["verdict"] == "null band"


def test_q2_measures_against_the_mean_of_the_first_two_draw_sets():
    """The bar is 25% of the two-draw mean, computed from the tables given rather than read from the registration --
    and the registration's own 2.16987 is printed beside the measured mean so the two can be compared."""
    ok = {"a": tab(bio4=2.0), "b": tab(bio4=2.4), "c": tab(bio4=2.2)}   # mean 2.2, third off it by 0%
    assert {r["id"]: r for r in e203.judge_band(ok)}["Q2"]["verdict"] == "MET"
    off = {"a": tab(bio4=2.0), "b": tab(bio4=2.4), "c": tab(bio4=1.6)}  # mean 2.2, off by 27%
    assert {r["id"]: r for r in e203.judge_band(off)}["Q2"]["verdict"] == "null band"
    bad = {"a": tab(bio4=2.0), "b": tab(bio4=2.4), "c": tab(bio4=1.0)}  # off by 55%
    assert {r["id"]: r for r in e203.judge_band(bad)}["Q2"]["verdict"] == "FALSIFIER FIRED"


def test_q3_is_the_span_of_the_peak_and_not_of_a_named_rung():
    """`bio:pool4` can sit still while `bio:pool8` takes the head and moves a lot -- the span is over the PEAK, which
    is why the claim is about the head rather than about the rung Q2 names."""
    still = {"a": tab(bio4=2.0, bio8=1.9), "b": tab(bio4=2.0, bio8=1.9), "c": tab(bio4=2.0, bio8=1.9)}
    assert {r["id"]: r for r in e203.judge_band(still)}["Q3"]["verdict"] == "MET"
    # a span of 0.6 is the registration's null band and 1.2 fires its falsifier; they are asserted apart because
    # the first version of this test wrote 2.6 expecting a firing, and the reader said `null band`
    moved = {"a": tab(bio4=2.0, bio8=1.9), "b": tab(bio8=3.2), "c": tab(bio4=2.0)}
    assert {r["id"]: r for r in e203.judge_band(moved)}["Q3"]["verdict"] == "FALSIFIER FIRED"
