"""`e506` separates the label's window from its position by adding the four-trial pass, so the tests pin the three
claims' both faces, the constants they are registered with, and the refusal when an input is absent.

The falsifier test drives `judge` on synthetic readings rather than on the artifact, so a claim's outcome is never
asserted as the artifact's shape: what is pinned is that each registered falsifier does fire, and that the three
claims read both faces. A second test drives `reading` on synthetic artifacts on disk with the share instrument
stubbed, so the pipeline that builds the window table is exercised as well.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e506_the_window_or_the_position as e506

ARMS = e506.ARMS
KEYS = [k for k, _, _, _ in e506.PLACEMENTS]
PAIRS = (("four_at0", "four_at1"), ("four_at1", "four_at2"), ("four_at0", "four_at2"))


def _diag(big0=0.8299, big1=0.8538, big2=0.8600, w8=0.55, w7=0.50, w5a=0.3104, w5b=0.3100, w3=0.26):
    return {"two_at0": {a: big0 for a in ARMS}, "three_at0": {a: big1 for a in ARMS},
            "four_at0": {a: big2 for a in ARMS}, "four_at1": {a: w8 for a in ARMS},
            "three_at1": {a: w7 for a in ARMS}, "two_at1": {a: w5a for a in ARMS},
            "four_at2": {a: w5b for a in ARMS}, "three_at2": {a: w3 for a in ARMS}}


def _shares(w11=1.05, w8=0.055, w7=0.050, w5a=0.0386, w5b=0.040, w3=0.031):
    return {"two_at0": {"window": 11, "share": w11},
            "three_at0": {"window": 11, "share": w11 + 0.002},
            "four_at0": {"window": 11, "share": w11 - 0.001},
            "four_at1": {"window": 8, "share": w8},
            "three_at1": {"window": 7, "share": w7},
            "two_at1": {"window": 5, "share": w5a},
            "four_at2": {"window": 5, "share": w5b},
            "three_at2": {"window": 3, "share": w3}}


def _paired(mean, sigma):
    return {"n": 20, "mean": mean, "sd": 0.01, "se": 0.001, "sigma": sigma}


def _cmp(differ=None, draw_differ=None, added=None, missing=None, moved=None):
    dd = list(draw_differ if draw_differ is not None else ["label_at"])
    return {"same": 60, "inert": ["json_out", "loop_label_at", "loop_label_first"],
            "differ": {k: [None, 1] for k in (differ or [])},
            "moved": (moved if moved is not None else {"loop_label_first": False, "loop_label_at": 1}),
            "draw": {"added": list(added or []), "missing": list(missing or []), "differ": dd,
                     "differ_outside": [k for k in dd if k not in e506.DRAW_MOVED]}}


def _spreads(diag):
    out = {}
    for w, ks in e506.GROUPS.items():
        here = [k for k in ks if diag.get(k) is not None]
        if len(here) < 2:
            continue
        out[w] = {a: max(diag[k][a] for k in here) - min(diag[k][a] for k in here) for a in ARMS}
    return out


def _doc(diag=None, shares=None, cmp_kw=None, end_to_end=None, absent=None, replicates=20):
    diag = _diag() if diag is None else diag
    shares = _shares() if shares is None else shares
    absent = list(absent or [])
    spread = _spreads(diag)
    bound = max(spread[e506.BIG_WINDOW].values()) if e506.BIG_WINDOW in spread else None
    pairs = {f"{a}|{b}": _cmp(**(cmp_kw or {})) for a, b in PAIRS}
    end = end_to_end or {a: _paired(+0.59, +12.00) for a in ARMS}
    return {
        "ok": True, "reason": None,
        "placements": {k: {"artifact": f"{k}.json", "config": {}, "env_draw": {},
                           "arms": {a: {"replicates": replicates} for a in ARMS}}
                       for k in KEYS if k not in absent},
        "share": {k: dict(v) for k, v in shares.items() if k not in absent},
        "recovery": {"pairs": {k: (None if k.split("|")[0] in absent else v) for k, v in pairs.items()},
                     "four_pairs": {}, "end_to_end": end, "alt_end_to_end": end},
        "spans": {
            "arms": list(ARMS), "chance": e506.CHANCE, "sigma": e506.SIGMA, "arms_needed": e506.ARMS_NEEDED,
            "factor": e506.FACTOR, "big_window": e506.BIG_WINDOW, "small_window": e506.SMALL_WINDOW,
            "replicates": [replicates], "absent": absent, "windows": dict(e506.WINDOW),
            "groups": {w: list(k) for w, k in e506.GROUPS.items()}, "spread": spread, "bound": bound,
            "accuracy_diagonal": {k: (None if k in absent else diag[k]) for k in KEYS},
            "accuracy_last": {k: ({a: 0.50 for a in ARMS} if k not in absent else None) for k in KEYS},
            "share": {k: round(v["share"], 4) for k, v in shares.items() if k not in absent},
            "share_window": {k: v["window"] for k, v in shares.items() if k not in absent},
        },
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e506.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("WA1", "WA2", "WA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # WA1: another config field differing, a draw field outside the placement added, missing or differing, a thin run
    assert _judge(cmp_kw={"differ": ["iters"]})["WA1"].startswith("FALSIFIER")
    assert _judge(cmp_kw={"added": ["reward_map_sha1"]})["WA1"].startswith("FALSIFIER")
    assert _judge(cmp_kw={"missing": ["boundary_sha1"]})["WA1"].startswith("FALSIFIER")
    assert _judge(cmp_kw={"draw_differ": ["cue_sha1"]})["WA1"].startswith("FALSIFIER")
    assert _judge(replicates=19)["WA1"].startswith("FALSIFIER")

    # WA2: two placements at the same window differing by more than the window-eleven bound -- four_at2 (window 5)
    # reads 0.55 where two_at1 (also window 5) reads 0.31
    over = _diag(w5b=0.55)
    assert _judge(diag=over)["WA2"].startswith("FALSIFIER")
    # WA2: the end-to-end move not resolving
    assert _judge(end_to_end={a: _paired(+0.01, +0.50) for a in ARMS})["WA2"].startswith("FALSIFIER")

    # WA3: two same-window shares outside the factor -- four_at2 at 0.30 against two_at1 at 0.0386
    assert _judge(shares=_shares(w5b=0.30))["WA3"].startswith("FALSIFIER")
    # WA3: a share that does not fall -- window 8 above window 11
    assert _judge(shares=_shares(w8=1.50))["WA3"].startswith("FALSIFIER")

    #: each claim refuses on its own absent input
    assert _judge(absent=["four_at1"])["WA1"].startswith("REFUSED")
    assert _judge(absent=["two_at1"])["WA2"].startswith("REFUSED")
    #: with no reading at all every claim refuses
    assert all(row["verdict"].startswith("REFUSED") for row in e506.judge({"ok": False, "reason": "no connectome"}))


def test_the_runs_the_windows_and_the_axis_are_registered():
    assert e506.NEW == ("four_at0", "four_at1", "four_at2"), e506.NEW
    assert (e506.END_FROM, e506.END_TO) == ("four_at0", "three_at2")
    assert set(e506.MOVED) == {"loop_label_first", "loop_label_at"}
    assert set(e506.DRAW_MOVED) == {"label_first", "label_at"}
    assert set(e506.BOOKKEEPING) == {"json_out", "save_theta"}
    #: the three pass lengths and the three placements this unit adds: trials of three steps, windows 11, 8 and 5
    assert e506.WINDOW == {"two_at0": 11, "two_at1": 5, "three_at0": 11, "three_at1": 7, "three_at2": 3,
                           "four_at0": 11, "four_at1": 8, "four_at2": 5}, e506.WINDOW
    #: window 11 is carried by three pass lengths and window 5 by two, which is what makes the window a variable
    assert e506.GROUPS[11] == ["four_at0", "three_at0", "two_at0"], e506.GROUPS[11]
    assert e506.GROUPS[5] == ["four_at2", "two_at1"], e506.GROUPS[5]
    assert e506.BIG_WINDOW == 11 and e506.SMALL_WINDOW == 3
    assert e506.CHANCE == 0.25
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e506.MIN_REPS, e506.SIGMA, e506.ARMS_NEEDED, e506.FACTOR) == (20, 2.0, 2, 2.0)
    assert e506._inert("loop_label_at", None, 2) and e506._inert("json_out", "a", "b")
    assert not e506._inert("iters", 500, 100)
    #: the three claims are registered with their falsifiers beside them, before the reading was opened
    assert [c[0] for c in e506.CLAIMS] == ["WA1", "WA2", "WA3"]
    assert all("falsifier:" in c[3] for c in e506.CLAIMS)


def _replicate(acc):
    return {"learned": [acc] * 4, "final_per_task": [acc] * 3}


def _write(path: Path, cfg: dict, draw: dict, acc: float) -> None:
    doc = {"config": cfg, "env_draw": draw,
           "methods": {a: {"replicates": [_replicate(acc) for _ in range(20)]} for a in ARMS}}
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_the_reading_builds_the_window_table_from_artifacts(tmp_path, monkeypatch):
    base4 = {"loop_episode": 4, "loop_label_first": False, "save_theta": None}
    places = {"two_at0": 0.8299, "two_at1": 0.3104, "three_at0": 0.8538, "three_at1": 0.3257,
              "three_at2": 0.2566, "four_at0": 0.8600, "four_at1": 0.5500, "four_at2": 0.3100}
    paths = {}
    for key, trials, at, _ in e506.PLACEMENTS:
        if key.startswith("four"):
            cfg = {**base4, "loop_label_at": at, "json_out": f"{key}.json"}
            draw = {"cue_sha1": "a", "episode_len": 4, "label_at": at}
        else:
            cfg = {"loop_episode": trials, "json_out": f"{key}.json"}
            draw = {"cue_sha1": "a", "episode_len": trials}
        p = tmp_path / f"{key}.json"
        _write(p, cfg, draw, places[key])
        paths[key] = p
    monkeypatch.setattr(e506, "share_of_placements", lambda: {k: {"window": e506.WINDOW[k], "share": 0.5}
                                                              for k in KEYS})
    r = e506.reading(paths=paths)
    assert set(r["placements"]) == set(KEYS), sorted(r["placements"])
    #: the three four-trial runs are compared pairwise: the placement is inert by the claim's own rule and no other
    #: config field moves
    for pair in PAIRS:
        c = r["recovery"]["pairs"][f"{pair[0]}|{pair[1]}"]
        assert c["differ"] == {}, c
        assert sorted(c["inert"]) == ["json_out", "loop_label_at"], c
        assert c["draw"]["added"] == [] and c["draw"]["missing"] == []
        assert c["draw"]["differ"] == ["label_at"], c
    assert r["spans"]["absent"] == []
    assert r["spans"]["windows"]["four_at1"] == 8 and r["spans"]["windows"]["four_at2"] == 5
    #: the window table carries each placement's pass length, trial, window and accuracy
    assert r["spans"]["accuracy_diagonal"]["four_at0"]["naive"] == 0.86
    #: the config and the draw are compared inside the runs, so the artifact carries no top-level `config`
    assert "config" not in r and "env" not in r and "tasks" not in r, sorted(r)
    #: an absent run reads as absent and refuses the claims that need it, rather than raising
    gone = e506.reading(paths={**paths, "four_at1": tmp_path / "nope.json"})
    assert gone["spans"]["absent"] == ["four_at1"]
    v = {row["id"]: row["verdict"] for row in e506.judge(gone)}
    assert v["WA1"].startswith("REFUSED") and v["WA2"].startswith("REFUSED")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e506_the_window_or_the_position.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e506.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    assert d["spans"]["replicates"] == [e506.MIN_REPS] or d["spans"]["replicates"] == [], d["spans"]["replicates"]
    assert e506.WINDOW["four_at1"] == 8 and e506.WINDOW["four_at2"] == 5
    #: the counts that grow with the corpus are read as bounds, so a longer artifact does not break the test
    for key in d["placements"]:
        diag = d["spans"]["accuracy_diagonal"][key]
        assert diag is not None
        for a in ARMS:
            assert 0.0 <= diag[a] <= 1.0, (key, a)
        for v in d["placements"][key]["arms"].values():
            assert v["replicates"] >= 1
    assert d["spans"]["bound"] is not None and d["spans"]["bound"] >= 0.0
    for a in ARMS:
        assert d["recovery"]["end_to_end"][a]["n"] >= e506.MIN_REPS, a
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
