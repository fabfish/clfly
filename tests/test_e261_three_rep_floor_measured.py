"""`e261` measures the three-replicate floor `e259` extrapolated to, so the tests pin the arithmetic it reads floors
with, the configuration check that licenses pairing two runs, the corpus scan for the largest budget, both faces of
the three claims, and the live table's own numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e261_three_rep_floor_measured as e261


def test_the_matched_pair_statistics_and_their_edges():
    st = e261.stats([0.1, 0.2, 0.3])
    assert st["n"] == 3 and abs(st["delta"] - 0.2) < 1e-12
    assert abs(st["sd"] - 0.1) < 1e-12 and abs(st["sem"] - 0.1 / 3 ** 0.5) < 1e-12
    assert abs(st["floor"] - 2 * 0.1 / 3 ** 0.5) < 1e-12 and abs(st["sigma"] - 0.2 / (0.1 / 3 ** 0.5)) < 1e-9
    assert e261.stats([1.0, -1.0])["floor"] > 0, "a floor is a sd over the replicates and never a bare sem"
    assert math.isnan(e261.stats([0.5])["floor"]), "one replicate has no spread and so no floor"


def test_diffs_reads_the_matched_pair_and_not_the_naive_arm():
    d = {"methods": {"ewc-block": {"replicates": [{"final_accuracy": 0.8, "mean_forgetting": 0.3},
                                                  {"final_accuracy": 0.6, "mean_forgetting": 0.2}]},
                     "ewc-block-rand": {"replicates": [{"final_accuracy": 0.7, "mean_forgetting": 0.1},
                                                       {"final_accuracy": 0.5, "mean_forgetting": 0.2}]},
                     "naive": {"replicates": [{"final_accuracy": 0.9, "mean_forgetting": 0.0},
                                              {"final_accuracy": 0.9, "mean_forgetting": 0.0}]}}}
    for got, want in zip(e261.diffs(d), (0.1, 0.1)):
        assert abs(got - want) < 1e-12, "the control is the size-matched random basis, not the naive arm"
    for got, want in zip(e261.diffs(d, "mean_forgetting"), (0.2, 0.0)):
        assert abs(got - want) < 1e-12


def _cfgs(**over):
    base = {"circuit_size": 800, "support": 80, "lam": 0.1, "basis": "side", "repeats": 16, "json_out": "b.json"}
    other = dict(base, json_out="a.json", repeats=3)
    other.update(over)
    return base, other


def test_config_diff_licenses_the_budget_and_flags_anything_else():
    base, other = _cfgs()
    differ, ok = e261.config_diff(base, other)
    assert ok and sorted(k for k, _, _ in differ) == ["json_out", "repeats"], differ
    differ, ok = e261.config_diff(base, _cfgs(lam=1.0)[1])
    assert not ok and "lam" in [k for k, _, _ in differ], differ
    differ, ok = e261.config_diff(base, _cfgs(methods="ewc-block,ewc-block-rand")[1])
    assert ok, "the arm list is reported and not treated as a configuration change"


def _artifact(root: Path, name: str, n: int, basis: str = "side", methods=None, cfg_extra=None):
    rep = {"final_accuracy": 0.5, "mean_forgetting": 0.1}
    payload = {"config": dict({"circuit_size": 300, "support": 80, "lam": 1.0, "basis": basis,
                               "repeats": n, "json_out": name}, **(cfg_extra or {})),
               "timing_s": 100.0 * n,
               "methods": methods if methods is not None else {
                   "ewc-block": {"replicates": [dict(rep, final_accuracy=0.5 + 0.01 * i) for i in range(n)]},
                   "ewc-block-rand": {"replicates": [dict(rep) for _ in range(n)]}}}
    (root / name).write_text(json.dumps(payload), encoding="utf-8")


def test_the_largest_budget_scan_ranks_by_replicates_and_survives_the_shapes_in_the_corpus(tmp_path):
    _artifact(tmp_path, "a.json", 3)
    _artifact(tmp_path, "b.json", 40)
    _artifact(tmp_path, "c.json", 9, basis="cell_class")
    _artifact(tmp_path, "no_basis.json", 200, cfg_extra={}, methods=None)
    (tmp_path / "no_basis.json").write_text(json.dumps(
        {"config": {"circuit_size": 800}, "methods": {"ewc-block": {"replicates": [{}] * 200}}}), encoding="utf-8")
    (tmp_path / "listy.json").write_text(json.dumps(
        {"config": {"basis": "side", "circuit_size": 800}, "methods": [1, 2, 3]}), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    rows = e261.largest_budget(tmp_path)
    assert [r["n"] for r in rows] == [40, 9, 3], rows
    assert rows[0]["artifact"] == "b.json" and rows[0]["basis"] == "side"


def _runs(side_ratio=1.131, cc_ratio=1.517):
    three = lambda floor: {"n": 3, "floor": floor, "sem": floor / 2, "sd": 1.0, "delta": 0.0, "sigma": 0.0}
    six = lambda floor: {"n": 16, "floor": floor, "per_replicate_s": 500.0}
    return {"side": (three(0.02891), six(0.02891 / side_ratio)),
            "cell_class": (three(0.04900), six(0.04900 / cc_ratio))}


def _rows(pub_side=0.0069, pub_cc=0.0648, pub_cross=0.0718, floor_side=0.02891, floor_cc=0.04900,
          floor_cross=0.06725, e259=(0.05901, 0.07459, 0.09979)):
    out = [{"figure": "side", "published": pub_side, "sem": floor_side / 2, "floor": floor_side,
            "ratio": pub_side / floor_side, "e259_floor": e259[0]},
           {"figure": "cell_class", "published": pub_cc, "sem": floor_cc / 2, "floor": floor_cc,
            "ratio": pub_cc / floor_cc, "e259_floor": e259[1]}]
    if pub_cross is not None:
        out.append({"figure": "side - cell_class", "published": pub_cross, "sem": floor_cross / 2,
                    "floor": floor_cross, "ratio": pub_cross / floor_cross, "e259_floor": e259[2]})
    return out


def test_R1_fires_if_an_extrapolated_floor_is_where_the_measured_one_is():
    rows = _rows(e259=(0.0290, 0.07459, 0.09979))
    j = {r["id"]: r for r in e261.judge(_runs(), rows, None, [])}
    assert j["R1"]["verdict"].startswith("FALSIFIER FIRED"), j["R1"]
    j = {r["id"]: r for r in e261.judge(_runs(), _rows(), None, [])}
    assert j["R1"]["verdict"].startswith("MET"), j["R1"]
    assert "2.04x" in j["R1"]["measured"], j["R1"]


def test_R2_reads_one_below_and_two_above_its_own_floor_and_fires_the_other_way():
    j = {r["id"]: r for r in e261.judge(_runs(), _rows(), None, [])}
    assert j["R2"]["verdict"].startswith("MET"), j["R2"]
    assert "2 of 3" in j["R2"]["verdict"], j["R2"]
    # the shape e259 described: two of the three under their own floor
    j = {r["id"]: r for r in e261.judge(_runs(), _rows(pub_cc=0.040, pub_cross=0.040), None, [])}
    assert j["R2"]["verdict"].startswith("FALSIFIER FIRED"), j["R2"]


def test_R3_refuses_without_the_largest_budget_and_fires_below_forty(tmp_path):
    _artifact(tmp_path, "small.json", 16)
    largest = e261.largest_budget(tmp_path)
    j = {r["id"]: r for r in e261.judge(_runs(), _rows(), None, largest)}
    assert j["R3"]["verdict"].startswith("REFUSED"), j["R3"]
    big = {"n": 16, "delta": 0.0, "sigma": 0.1, "floor": 0.1}
    j = {r["id"]: r for r in e261.judge(_runs(), _rows(), big, largest)}
    assert j["R3"]["verdict"].startswith("FALSIFIER FIRED"), j["R3"]
    j = {r["id"]: r for r in e261.judge(_runs(), _rows(), big, [{"n": 144, "artifact": "e178.json"}])}
    assert j["R3"]["verdict"].startswith("MET"), j["R3"]


def test_the_live_table_measures_the_three_floors_and_reconstructs_the_cross_rung():
    """The finding's numbers on the artifact: the reconstruction of the published cross-rung figure from the two
    three-replicate runs, the three floors against `e259`'s scaled ones, and the 144-replicate budget."""
    p = Path("runs/e261_three_rep_floor_measured.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = {r["figure"]: r for r in d["measured_floors"]}
    assert abs(rows["side"]["floor"] - 0.02891) < 1e-5 and abs(rows["side"]["ratio"] - 0.239) < 1e-3, rows["side"]
    assert abs(rows["cell_class"]["floor"] - 0.04900) < 1e-5 and rows["cell_class"]["ratio"] > 1, rows["cell_class"]
    cross = rows["side - cell_class"]
    assert abs(cross["delta"] - 0.07176) < 1e-4 and abs(cross["sigma"] - 2.13) < 0.02, cross
    assert abs(cross["ratio"] - 1.068) < 1e-3, cross
    for name, factor in (("side", 2.04), ("cell_class", 1.52), ("side - cell_class", 1.48)):
        assert abs(rows[name]["e259_floor"] / rows[name]["floor"] - factor) < 0.01, (name, rows[name])
    assert d["config_check"]["side"]["only_the_budget_differs"] is True, d["config_check"]["side"]
    assert d["largest_budget"][0]["n"] == 144 and d["largest_budget"][0]["basis"] == "side", d["largest_budget"][0]
    assert abs(d["e178_side_144"]["sigma"] - 0.28) < 0.01, d["e178_side_144"]
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("R1", "R2", "R3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
