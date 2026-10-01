"""`e301` finds the corpus's second executions of experiments it already holds, so the tests pin what makes a pair one
execution rather than a sample swap or a coincidence, the transitive closure that turns four files into one cluster,
the four bookkeeping keys the comparison ignores, both faces of the three claims, and the live clusters.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from clfly.bench import corpus
from experiments import e301_the_corpus_holds_repeats as e301

_MISSING = object()


def _art(path: Path, n_eval=144, arms=("naive",), rows=5, losses=(1.0, 0.5), shape=None, draws=("readout",)):
    payload = {"config": dict({"circuit_size": 800, "train": 96, "seed0": 0, "methods": "naive"}, **(shape or {})),
               "evaluation_noise": {"n_eval": n_eval}, "methods": {}}
    for k in draws:
        payload[k] = {"subset_sha1": "abc"}
    for a in arms:
        payload["methods"][a] = {"replicates": [
            {"final_accuracy": 0.9 + 0.01 * i, "mean_forgetting": 0.05 + 0.001 * i,
             "losses": list(losses), "theta_drift": 0.5, "bias_norms": [0.5], "retention_loss": [0.5],
             "interference": [0.5], "full_train_loss": [0.5], "method": a} for i in range(rows)]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_a_repeat_is_one_experiment_and_not_a_sample_swap(tmp_path):
    _art(tmp_path / "a.json")
    b = _art(tmp_path / "b.json")
    b["config"]["json_out"] = "b.json"                       # the one difference a repeat is allowed to have
    (tmp_path / "b.json").write_text(json.dumps(b), encoding="utf-8")
    assert [Path(x).name for g in corpus.groups(tmp_path) for x in g] == ["a.json", "b.json"]

    # the same models on a larger sample is `e286`'s subject and not a repeat: the eval size separates them
    _art(tmp_path / "c.json", n_eval=1440)
    assert Path("c.json").as_posix() not in {Path(x).name for g in corpus.groups(tmp_path) for x in g}

    # and a training that moved is not one experiment either
    _art(tmp_path / "d.json", losses=(1.0, 0.4))
    assert len(corpus.groups(tmp_path)) == 1, corpus.groups(tmp_path)


def test_a_cluster_is_the_transitive_closure(tmp_path):
    for name in ("one.json", "two.json", "three.json"):
        _art(tmp_path / name)
    g = corpus.groups(tmp_path)
    assert len(g) == 1 and [Path(x).name for x in g[0]] == ["one.json", "three.json", "two.json"], g
    assert corpus.repeat_paths(tmp_path) == {"three.json", "two.json"}, corpus.repeat_paths(tmp_path)
    # three copies give three pairs and one cluster: the pair count is not the cluster count
    assert len(corpus.pairs(tmp_path)) == 3, corpus.pairs(tmp_path)


def test_a_payload_with_no_training_at_all_is_not_a_repeat(tmp_path):
    for name in ("a.json", "b.json"):
        d = _art(tmp_path / name)
        for rep in d["methods"]["naive"]["replicates"]:
            for f in corpus.TRAIN_FIELDS:
                rep.pop(f, None)
        (tmp_path / name).write_text(json.dumps(d), encoding="utf-8")
    assert corpus.groups(tmp_path) == [], corpus.groups(tmp_path)
    # and the evidence says so rather than the flags: nothing was present to compare
    assert corpus.shared_training(corpus.load(tmp_path / "a.json"),
                                  corpus.load(tmp_path / "b.json"))["naive"]["present"] == 0


def test_the_four_bookkeeping_keys_are_the_only_ones_ignored(tmp_path):
    a = _art(tmp_path / "a.json")
    b = json.loads(json.dumps(a))
    b["config"]["json_out"] = "elsewhere.json"
    b["code_revision"] = {"commit": "x", "dirty": False}
    b["timing_s"] = 999.0
    b["cpu_time_s"] = 1.0
    b["environment"] = {"calibration_matmul_s": 0.9}
    assert corpus.differing_paths(a, b) == [], corpus.differing_paths(a, b)
    b["methods"]["naive"]["replicates"][0]["losses"] = [2.0, 9.0]
    assert corpus.differing_paths(a, b) == ["methods.naive.replicates[0].losses[0]",
                                            "methods.naive.replicates[0].losses[1]"], corpus.differing_paths(a, b)
    b["config"]["lr"] = 0.01
    assert "config.lr" in corpus.differing_paths(a, b), corpus.differing_paths(a, b)


def _reading(clusters=11, differ=(), kept=None, dropped=None):
    censuses = {"kept": {"e286": {"n_candidates": 34, "n_swaps": 7,
                                  "claims": {"X1": "MET -- a", "X2": "FALSIFIER FIRED -- 2 of 54 did not fall"}},
                         "e295": {"n_comparisons": 28, "claims": {"B1": "MET -- c"}},
                         "e296": {"n_comparisons": 42, "claims": {"C1": "FALSIFIER FIRED -- 25 of 42"}}},
                "dropped": {"e286": {"n_candidates": 23, "n_swaps": 5,
                                     "claims": {"X1": "MET -- d", "X2": "FALSIFIER FIRED -- 1 of 34 did not fall"}},
                            "e295": {"n_comparisons": 24, "claims": {"B1": "MET -- f"}},
                            "e296": {"n_comparisons": 38, "claims": {"C1": "FALSIFIER FIRED -- 23 of 38"}}}}
    if kept:
        censuses["kept"] = kept
    if dropped:
        censuses["dropped"] = dropped
    return {"clusters": [{"members": [f"e{i}.json", f"e{i}b.json"], "differing_paths": list(differ)}
                         for i in range(clusters)],
            "n_files": 556, "n_second_copies": clusters, "censuses": censuses}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e301.judge(_reading())}
    for cid in ("R1", "R2", "R3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a corpus with one repeat is not the corpus this unit reports on
    assert e301.judge(_reading(clusters=2))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a pair that differs outside the four bookkeeping keys is R2's falsifier
    assert e301.judge(_reading(differ=("config.lr",)))[1]["verdict"].startswith("FALSIFIER FIRED")
    # a verdict that changes CLASS when the copies are dropped is R3's; a verdict that only requotes its counts is not
    dropped = json.loads(json.dumps(_reading()["censuses"]["dropped"]))
    j = {r["id"]: r for r in e301.judge(_reading(dropped=dropped))}
    assert j["R3"]["verdict"].startswith("MET"), j["R3"]
    dropped["e286"]["claims"]["X2"] = "MET -- the fall goes against the sample size"
    j = {r["id"]: r for r in e301.judge(_reading(dropped=dropped))}
    assert j["R3"]["verdict"].startswith("FALSIFIER FIRED"), j["R3"]
    assert e301.judge({"clusters": []})[0]["verdict"].startswith("REFUSED")
    assert e301.outcome("FALSIFIER FIRED -- 25 of 42") == "FALSIFIER FIRED"


def test_the_live_clusters_are_the_ones_the_finding_names():
    g = corpus.groups()
    assert len(g) >= 11, len(g)
    assert sum(len(x) - 1 for x in g) >= 17, g
    named = {Path(m).name for x in g for m in x}
    for n in ("e287_frozenbias_suite1440_40reps.json", "e288_frozenbias_suite1440_40reps.json",
              "e153_r32_overlap1_methods_40reps.json", "e159_r32_overlap1_methods_rerun.json"):
        assert n in named, n
    # the canonical member is the alphabetically first, so `e287` is kept and `e288` is the second copy
    assert "e288_frozenbias_suite1440_40reps.json" in corpus.repeat_paths()
    assert "e287_frozenbias_suite1440_40reps.json" not in corpus.repeat_paths()
    #: **RE-READ 2026-10-02.** This was `all(not c["differing_paths"])` and it is a point assertion on a record
    #: that gains keys as the runner does: `e336` added `theta_direction` and the two clusters it shares with
    #: `e334` -- same circuit, same seeds, same leak, a **bit-identical** training -- differ in exactly that key and
    #: in nothing else. The structural statement is that **every** differing path is one some member of its cluster
    #: does not record, computed from the payloads, so a cluster that really disagrees inside a shared key still
    #: fires.
    def _records(payload, path):
        """Whether a payload records a dotted path, with lists indexed in brackets."""
        cur = payload
        for token in re.findall(r"[^.\[\]]+", path):
            if isinstance(cur, list):
                if not token.isdigit() or int(token) >= len(cur):
                    return False
                cur = cur[int(token)]
            elif isinstance(cur, dict):
                if token not in cur:
                    return False
                cur = cur[token]
            else:
                return False
        return True

    def _absent_in_one(members):
        payloads = []
        for name in members:
            try:
                payloads.append(json.loads((Path("runs") / name).read_text(encoding="utf-8")))
            except (OSError, ValueError):
                return None
        return {p for p in set().union(*[set(c["differing_paths"]) for c in e301.clusters()
                                         if c["members"] == members])
                if not all(_records(pay, p) for pay in payloads)}

    dirty = [c for c in e301.clusters()
             if _absent_in_one(c["members"]) is None
             or set(c["differing_paths"]) - _absent_in_one(c["members"])]
    assert e301.clusters() and not dirty, dirty


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e301_the_corpus_holds_repeats.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["clusters"]) >= 11, len(d["clusters"])
    assert d["n_second_copies"] == len(d["second_copies"]) >= 17, d["second_copies"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("R1", "R3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    #: **R2's falsifier fired on 2026-10-02**: two clusters differ outside the bookkeeping keys, and both are
    #: `e334`'s runs against `e336`'s -- same circuit, same seeds, same leak, a bit-identical training, differing in
    #: exactly the `theta_direction` key that did not exist when `e334` was written. The verdict is reported as it
    #: stands rather than re-based.
    assert claims["R2"]["verdict"].startswith("FALSIFIER FIRED"), claims["R2"]
    kept, dropped = d["censuses"]["kept"], d["censuses"]["dropped"]
    for k in ("e286", "e295", "e296"):
        for n, v in kept[k].items():
            if n.startswith("n_"):
                assert dropped[k][n] < v, (k, n, v, dropped[k][n])
