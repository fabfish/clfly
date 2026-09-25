from __future__ import annotations

import json
from pathlib import Path

from experiments import e222_support_read as e222


def art(path: Path, support: int, rs: int, alloy: float, inalloy: float, er: float) -> Path:
    """One drawing at one support, as `--no-realized` writes it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tops = {name: {"diagonal(EWC)": {"analytic": {"excess_mean": val, "excess_sem": 0.001}}}
            for name, val in (("alloy1", alloy), ("inalloy1", inalloy), ("erdos_renyi", er))}
    path.write_text(json.dumps({"config": {"circuit_size": 800, "support": support, "rewire_seed": rs},
                                "topologies": tops}), encoding="utf-8")
    return path


def support(tmp_path, sup: int, rows: list[tuple[float, float, float]]) -> None:
    for rs, (a, i, e) in enumerate(rows):
        art(tmp_path / f"e221_support{sup}_rs{rs}.json", sup, rs, a, i, e)


def judged(tmp_path) -> dict:
    return {r["id"]: r for r in e222.judge(e222.sweep(tmp_path))}


def test_a_support_short_of_its_drawings_or_absent_is_refused(tmp_path):
    """Both supports with two drawings each is the design; the reader names which support is missing or short."""
    assert e222.judge({})[0]["verdict"].startswith("REFUSED")
    support(tmp_path, 20, [(0.09, 0.08, 0.16), (0.09, 0.08, 0.16)])
    assert "160" in judged(tmp_path)["U1"]["verdict"]
    support(tmp_path, 160, [(0.05, 0.05, 0.15)])
    assert "1" in judged(tmp_path)["U1"]["verdict"] or "has" in judged(tmp_path)["U1"]["verdict"]


def test_u1_reads_the_one_side_levels_ratio_in_its_three_bands(tmp_path):
    """The one-side level is the MEAN of the two one-side nulls, and the claim is about the ratio between supports."""
    support(tmp_path, 20, [(0.10, 0.10, 0.20), (0.10, 0.10, 0.20)])      # mean 0.10
    support(tmp_path, 160, [(0.05, 0.05, 0.20), (0.05, 0.05, 0.20)])     # mean 0.05 -> 2.0x -> MET
    assert judged(tmp_path)["U1"]["verdict"].startswith("MET"), judged(tmp_path)["U1"]
    support(tmp_path, 160, [(0.095, 0.095, 0.20), (0.095, 0.095, 0.20)])  # 1.05x boundary -> null
    assert judged(tmp_path)["U1"]["verdict"].startswith("null band"), judged(tmp_path)["U1"]
    support(tmp_path, 160, [(0.10, 0.10, 0.20), (0.10, 0.10, 0.20)])      # 1.00x -> falsifier
    assert "FALSIFIER" in judged(tmp_path)["U1"]["verdict"]


def test_u2_asks_for_the_top_step_to_follow_the_same_variable(tmp_path):
    """U2's falsifier is the REVERSE ordering, so a reader that only checked `both below 1.5x` would pass a design
    that refutes the share reading."""
    support(tmp_path, 20, [(0.10, 0.10, 0.14), (0.10, 0.10, 0.14)])       # top step 1.40x
    support(tmp_path, 160, [(0.06, 0.06, 0.10), (0.06, 0.06, 0.10)])      # top step 1.67x -> MET
    assert judged(tmp_path)["U2"]["verdict"] == "MET", judged(tmp_path)["U2"]
    support(tmp_path, 20, [(0.06, 0.06, 0.20), (0.06, 0.06, 0.20)])       # top step 3.33x, above 160's -> falsifier
    assert "FALSIFIER" in judged(tmp_path)["U2"]["verdict"]
    # both below 1.5x is the registered NULL -- and support 20's must still not exceed support 160's, or the
    # falsifier (the reverse ordering) is what fires
    support(tmp_path, 20, [(0.10, 0.10, 0.13), (0.10, 0.10, 0.13)])       # top step 1.30x
    support(tmp_path, 160, [(0.10, 0.10, 0.12), (0.10, 0.10, 0.12)])      # top step 1.20x -> null
    assert judged(tmp_path)["U2"]["verdict"].startswith("null band"), judged(tmp_path)["U2"]


def test_the_reference_support_is_quoted_and_not_recomputed(tmp_path):
    """Support 80 is this line's convention and its cells come from other designs, so the reader quotes them rather
    than pretending to have measured them here."""
    assert e222.REFERENCE_80["alloy1"] == 0.05136 and "five drawings" in e222.REFERENCE_80["note"]
    support(tmp_path, 20, [(0.09, 0.08, 0.16), (0.09, 0.08, 0.16)])
    support(tmp_path, 160, [(0.05, 0.05, 0.15), (0.05, 0.05, 0.15)])
    got = e222.sweep(tmp_path)
    assert set(got) == {20, 160}

def test_the_share_is_read_from_the_circuit_block_or_declared_unreadable(tmp_path):
    """The neuron count is the quantity the support-share question turns on, and this family began recording it
    only on 2026-09-26 -- so the reader must read it where it exists and SAY it cannot where it does not, rather
    than taking the analytic block's `n` (the replicate count, 3) or `config.circuit_size` (the requested 800)."""
    support(tmp_path, 20, [(0.09, 0.08, 0.16), (0.09, 0.08, 0.16)])
    support(tmp_path, 160, [(0.05, 0.05, 0.15), (0.05, 0.05, 0.15)])
    rows = e222.sweep(tmp_path)
    assert all(r["n_neurons"] is None for r in rows[20]), "the fixture writes no circuit block"
    # and with one present it is used
    p = tmp_path / "e221_support20_rs0.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for block in d["topologies"].values():
        block["circuit"] = {"n_neurons": 1307, "n_edges": 26568, "targets_changed": 0.98}
    p.write_text(json.dumps(d), encoding="utf-8")
    rows = e222.sweep(tmp_path)
    assert [r["n_neurons"] for r in rows[20]] == [1307, None], rows[20]
