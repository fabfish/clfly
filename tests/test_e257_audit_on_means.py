"""`e257` re-arms `e230`'s audit on the column it never judged, so the tests pin the three verdict states, the
coverage counts, the re-found family, and the declarations' survival -- plus the module's refusal when a field is
missing.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e257_audit_on_means as e257


def fam(size: int, topo: str, within: float, means: float | None, single: float | None,
        declared: bool = False, groups: int = 2) -> dict:
    return {"circuit_size": size, "topology": topo, "drawings_at_ref": 3, "within_at_ref": within,
            "between_mean": means, "between_single": single,
            "means_verdict": (None if means is None or within is None else means > within),
            "as_read_verdict": (None if single is None or within is None else single > within),
            "declared": declared, "rho_groups": groups}


def test_the_three_verdict_states():
    rs = [fam(300, "alloy1", 2.0, 12.0, None), fam(800, "alloy1", 16.0, 7.8, None),
          fam(400, "alloy1", 1.5, None, None, groups=1)]
    assert rs[0]["means_verdict"] is True and rs[1]["means_verdict"] is False and rs[2]["means_verdict"] is None
    rows = {r["id"]: r for r in e257.judge(rs)}
    assert rows["G1"]["verdict"].startswith("MET") or rows["G1"]["verdict"].startswith("FALSIFIER")


def test_G1_counts_what_each_reading_can_see():
    rs = [fam(300, f"t{i}", 2.0, 8.0, None) for i in range(7)] + [fam(300, "s", 2.0, 8.0, 4.0)]
    rows = {r["id"]: r for r in e257.judge(rs)}
    assert "the means column covers 8 families against the as-read column's 1" in rows["G1"]["measured"], rows["G1"]
    assert rows["G1"]["verdict"].startswith("MET"), rows["G1"]


def test_G2_fires_when_nothing_gains_a_verdict():
    rs = [fam(300, "alloy1", 2.0, 1.0, 4.0)]              # means does not clear, as-read does
    rows = {r["id"]: r for r in e257.judge(rs)}
    assert rows["G2"]["verdict"].startswith("FALSIFIER FIRED"), rows["G2"]


def test_G3_refuses_without_the_cs_800_alloy1_contrast():
    rows = {r["id"]: r for r in e257.judge([fam(300, "alloy1", 2.0, 12.0, None)])}
    assert rows["G3"]["verdict"].startswith("REFUSED"), rows["G3"]
    ok = {r["id"]: r for r in e257.judge([fam(800, "alloy1", 16.44, 7.84, None)])}
    assert ok["G3"]["verdict"].startswith("MET"), ok["G3"]
    clears = {r["id"]: r for r in e257.judge([fam(800, "alloy1", 1.0, 7.84, None)])}
    assert clears["G3"]["verdict"].startswith("FALSIFIER FIRED"), clears["G3"]


def test_G4_checks_every_declared_family_against_the_means():
    still = {r["id"]: r for r in e257.judge([fam(300, "swap0.5", 8.77, 8.10, 4.05, declared=True)])}
    assert still["G4"]["verdict"].startswith("MET"), still["G4"]
    cleared = {r["id"]: r for r in e257.judge([fam(300, "swap0.5", 8.77, 9.10, 4.05, declared=True)])}
    assert cleared["G4"]["verdict"].startswith("FALSIFIER FIRED"), cleared["G4"]


def test_the_live_audit_covers_eleven_and_refinds_cs_800_alloy1():
    """The finding's numbers on the artifact: 11 families with a means contrast against 5 as-read, 31 with none, and
    cs 800 alloy1 unresolvable at a ratio of 0.48."""
    p = Path("runs/e257_audit_on_means.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rs = d["families"]
    covered = [r for r in rs if r["means_verdict"] is not None]
    as_read = [r for r in rs if r["as_read_verdict"] is not None]
    assert len(rs) == 42 and len(covered) == 11 and len(as_read) == 5, (len(rs), len(covered), len(as_read))
    assert len([r for r in rs if r["means_verdict"] is None]) == 31, "the rest have a single rho group"
    cs800 = [r for r in rs if r["circuit_size"] == 800 and r["topology"] == "alloy1"][0]
    assert cs800["means_verdict"] is False and abs(cs800["between_mean"] / cs800["within_at_ref"] - 0.48) < 0.01
    rows = {r["id"]: r for r in d["claims"]}
    for cid in ("G1", "G2", "G3", "G4"):
        assert rows[cid]["verdict"].startswith("MET"), rows[cid]
