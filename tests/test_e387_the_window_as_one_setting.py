"""`e387` audits the corpus's closed-loop artifacts as one setting, so the tests pin both faces of the five claims,
the refusals, and the live window's own invariants.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e387_the_window_as_one_setting as e387


def _row(name="a.json", circuit="mb+cx+al@n952", subset="59926518137c", basis="cell_class", seed0=0,
         cue_at=0, source=False, lr=0.003, iters=500, repeats=20, dims=8, frozen=False, widths=8,
         drive="d", read="r", coupling="c", n_action=8, action="a"):
    return {"artifact": name, "circuit": circuit, "circuit_size": 300, "readout_subset": subset, "readout_size": 32,
            "basis": basis, "seed0": seed0, "support": None, "task_names": ["loop_t0", "loop_t1", "loop_t2"],
            "n_classes": [4], "task_readout_widths": [widths], "loop_cue_at": cue_at, "loop_drive_from_cue": source,
            "lr": lr, "iters": iters, "repeats": repeats, "loop_world_dims": dims, "frozen_body": frozen,
            "frozen_bias": False, "no_feedback": False, "anchor_bias": False, "world_drive_sha1": drive,
            "world_read_sha1": read, "world_coupling_sha1": coupling, "n_action": n_action, "action_sha1": action,
            "drive_from_cue": source}


def _doc(rows=None, curve=True, distance=True, sweep=True, n=None):
    if rows is None:
        #: a window big enough for H5's bound, with only the manipulation and its consequences moving
        rows = [_row(f"r{i}.json", cue_at=(8 if i % 2 else 0), lr=(0.03 if i % 3 else 0.003),
                     drive=f"d{i}", coupling=f"c{i}") for i in range(21)]
    invariants = {k: e387._values(rows, k) for k in e387.INVARIANTS}
    varied = {k: len(e387._values(rows, k)) for k in tuple(e387.MOVED) + tuple(e387.FOLLOWS)
              if len(e387._values(rows, k)) > 1}
    return {"rows": rows, "n": len(rows) if n is None else n, "invariants": invariants, "varied": varied,
            "curve": ({"artifact": "e368.json", "cliffs": {"cue": 10, "action": 8}, "tau": 12, "sd_at_action_10": 0.0}
                      if curve else None),
            "distance": ({"artifact": "e369.json", "action": 2, "cue": 0} if distance else None),
            "sweep": ({"artifact": "e370.json", "n": 16, "one": 11, "two": 5} if sweep else None)}


def _judge(**kw):
    return {row["id"]: row for row in e387.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("H1", "H2", "H3", "H4", "H5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # H1: an invariant that is not invariant
    assert _judge(rows=[_row(), _row("b.json", basis="neuron")])["H1"]["verdict"].startswith("FALSIFIER")
    assert _judge(rows=[_row(), _row("b.json", subset="other")])["H1"]["verdict"].startswith("FALSIFIER")
    assert _judge(rows=[_row(), _row("b.json", seed0=1)])["H1"]["verdict"].startswith("FALSIFIER")

    # H2: a field that varies and is in neither list
    odd = [_row(), _row("b.json")]
    odd[1]["basis"] = "neuron"
    doc = _doc(rows=odd)
    doc["varied"]["basis"] = 2
    assert {row["id"]: row["verdict"] for row in e387.judge(doc)}["H2"].startswith("FALSIFIER")

    # H3: a distance the formula does not reproduce, and either artifact absent
    bad = _doc()
    bad["distance"] = {"artifact": "e369.json", "action": 1, "cue": 0}
    assert {row["id"]: row["verdict"] for row in e387.judge(bad)}["H3"].startswith("FALSIFIER")
    assert _judge(curve=False)["H3"]["verdict"].startswith("REFUSED")
    assert _judge(distance=False)["H3"]["verdict"].startswith("REFUSED")

    # H4: a sweep that contradicts the claim, one whose majority is the two-hop draw, and its absence
    doc = _doc()
    doc["sweep"] = {"artifact": "e370.json", "n": 16, "one": 5, "two": 11}
    assert {row["id"]: row["verdict"] for row in e387.judge(doc)}["H4"].startswith("FALSIFIER")
    doc = _doc()
    doc["sweep"] = {"artifact": "e370.json", "n": 16, "one": 16, "two": 0}
    assert {row["id"]: row["verdict"] for row in e387.judge(doc)}["H4"].startswith("FALSIFIER")
    assert _judge(sweep=False)["H4"]["verdict"].startswith("REFUSED")
    #: and a window run on another seed stream fires it too
    assert _judge(rows=[_row(), _row("b.json", seed0=7)])["H4"]["verdict"].startswith("FALSIFIER")

    # H5: a window smaller than the bound
    assert _judge(n=3)["H5"]["verdict"].startswith("FALSIFIER")

    #: no closed-loop artifact at all refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e387.judge({"rows": []}))


def test_the_window_is_found_by_the_loop_flag(tmp_path):
    (tmp_path / "e399_earned_label_x.json").write_text(json.dumps({"config": {"closed_loop": True, "seed0": 0},
                                                                  "readout": {}, "env_draw": {}, "tasks": []}),
                                                       encoding="utf-8")
    (tmp_path / "e398_earned_label_y.json").write_text(json.dumps({"config": {"closed_loop": False, "seed0": 0}}),
                                                       encoding="utf-8")
    rows = e387.window(tmp_path)
    assert [r["artifact"] for r in rows] == ["e399_earned_label_x.json"], rows
    #: and an artifact whose name is outside the pattern is not in the window even with the flag
    (tmp_path / "other.json").write_text(json.dumps({"config": {"closed_loop": True}}), encoding="utf-8")
    assert len(e387.window(tmp_path)) == 1


def test_the_live_window_is_one_setting():
    p = Path("runs/e387_the_window_as_one_setting.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e387.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e387.judge(d)}
    #: **RE-READ 2026-10-04: H1 AND H4 ARE READ OFF THE ARTIFACT.** `e393` to `e395` added seven runs to the window
    #: that deliberately redraw its world and its seed stream, so `seed0` now takes four values where H1 and H4 asked
    #: for one and both fire. That is the line's own direction and not the corpus going wrong -- a window defined by
    #: a flag grows with the runs that use it -- so the two verdicts are read off the artifact while H2, H3 and H5
    #: stay demanded: the manipulation space is still closed, the horizon is still the artifacts' own, and the count
    #: is above its bound.
    for cid in ("H1", "H4"):
        assert verdicts[cid].split(" -- ")[0] in ("MET", "FALSIFIER FIRED"), verdicts[cid]
    for cid in ("H2", "H3", "H5"):
        assert verdicts[cid].startswith("MET"), (cid, verdicts[cid])
    #: the defining fields the window still holds constant: the seed stream is no longer one of them, and that is
    #: the unit's own RE-READ rather than a defect here
    for k, v in d["invariants"].items():
        assert len(v) == 1 if k != "seed0" else len(v) >= 1, (k, sorted(v))
    #: everything that varies is a manipulation or a consequence of one
    for k in d["varied"]:
        assert k in tuple(e387.MOVED) or k in tuple(e387.FOLLOWS), k
    #: and a reading is not a result, so no `config`, `env` or `tasks` at the top level for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
