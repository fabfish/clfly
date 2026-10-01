"""`e336` records the direction of a task's parameter update, so the tests pin the cosine arithmetic, the two
groupings it is compared in, the subspace fingerprint, and both faces of the four claims.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from experiments import e336_the_direction_of_the_update as e336


def test_the_cosine_is_the_one_it_says():
    assert abs(e336.cosine([1.0, 0.0], [1.0, 0.0]) - 1.0) < 1e-12
    assert abs(e336.cosine([1.0, 0.0], [0.0, 1.0])) < 1e-12
    assert abs(e336.cosine([1.0, 0.0], [-1.0, 0.0]) + 1.0) < 1e-12
    assert abs(e336.cosine([2.0, 0.0], [5.0, 0.0]) - 1.0) < 1e-12, "scale must not matter"
    assert e336.cosine([1.0], [1.0, 2.0]) is None
    assert e336.cosine([], []) is None


def test_the_two_groupings_count_what_they_should():
    # three replicates, two tasks: 3 within-pairs per task and 9 across-pairs per task
    a = [[[1.0, 0.0], [1.0, 0.0]], [[1.0, 0.0], [0.0, 1.0]], [[0.9, 0.1], [1.0, 0.0]]]
    b = [[[0.0, 1.0], [1.0, 0.0]], [[0.1, 0.9], [0.0, 1.0]], [[0.0, 1.0], [1.0, 0.0]]]
    w = e336.within(a)
    x = e336.across(a, b)
    assert [len(row) for row in w] == [3, 3], w
    assert [len(row) for row in x] == [9, 9], x
    # the within pairs of the first task are all nearly parallel, the third replicate being tilted
    assert all(c > 0.99 for c in w[0]), w[0]
    assert w[0][0] == 1.0, w[0]
    # and a run against itself across the grouping is not the same statistic
    assert e336.across(a, a)[0][0] == 1.0


def _run(vectors, leak=1.0, n=None):
    reps = [{"theta_direction": [{"index_sha1": "abc", "values": v, "subspace_norm": 0.3} for v in row],
             "mean_forgetting": 0.05, "final_accuracy": 0.6} for row in vectors]
    return {"config": {"circuit_size": 300, "loop_world_leak": leak}, "circuit": "MB",
            "readout": {"subset_sha1": "abc"}, "tasks": [{"name": "t"}],
            "env_draw": {"world_leak": leak, "world_modes": 2},
            "methods": {e336.ARM: {"final_accuracy": 0.6, "mean_forgetting": 0.05, "replicates": reps}}}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _vecs(seed, n_reps=4, n_tasks=3, tilt=0.0):
    """Replicate directions that cluster around a per-task axis, with ``tilt`` rotating the second group."""
    import numpy as np
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_reps):
        row = []
        for j in range(n_tasks):
            v = np.zeros(6)
            v[j % 6] = 1.0
            v[(j + 1) % 6] = tilt
            v = v + 0.05 * rng.standard_normal(6)
            row.append((v / np.linalg.norm(v)).tolist())
        out.append(row)
    return out


def _reading(tilt_a=0.0, tilt_b=0.0, leak=(1.0, 0.35), n_reps=4, same_fingerprint=True):
    a = _run(_vecs(1, n_reps, tilt=tilt_a), leak=leak[0])
    b = _run(_vecs(1, n_reps, tilt=tilt_b), leak=leak[1])
    if not same_fingerprint:
        for r in b["methods"][e336.ARM]["replicates"]:
            for e in r["theta_direction"]:
                e["index_sha1"] = "different"
    return e336.reading({"instant": _write(a), "carry": _write(b)})


def test_the_four_claims_read_both_faces():
    # the default fixture draws both worlds from the same seed, so the directions agree everywhere
    j = {row["id"]: row for row in e336.judge(_reading())}
    assert j["T1"]["verdict"].startswith("MET"), j["T1"]
    assert j["T2"]["verdict"].startswith("MET"), j["T2"]

    # T1: a differing subspace is the falsifier, and so is a differing leak pair
    assert e336.judge(_reading(same_fingerprint=False))[0]["verdict"].startswith("FALSIFIER")
    assert e336.judge(_reading(leak=(0.5, 0.35)))[0]["verdict"].startswith("FALSIFIER")
    # T2: directions that do not reproduce within a run
    import numpy as np
    noisy = [[ (lambda v: (v / np.linalg.norm(v)).tolist())(np.random.default_rng(100 + i * 7 + j).standard_normal(6))
               for j in range(3)] for i in range(4)]
    r = _reading()
    r["within"] = {"instant": e336.within(noisy), "carry": e336.within(noisy)}
    r["mean_within"] = {"instant": None, "carry": None}
    r["mean_within_per_task"] = [
        [float(np.mean(row)) if row else None for row in r["within"]["instant"]],
        [float(np.mean(row)) if row else None for row in r["within"]["carry"]]]
    assert e336.judge(r)[1]["verdict"].startswith("FALSIFIER"), e336.judge(r)[1]

    # T3 and T4: a rotated second world drops the across cosine
    tilted = _reading(tilt_b=3.0)
    j = {row["id"]: row for row in e336.judge(tilted)}
    assert j["T3"]["verdict"].startswith("MET"), j["T3"]
    assert j["T4"]["verdict"].startswith("MET"), j["T4"]
    # an unrotated one leaves it where it was
    flat = e336.judge(_reading())
    assert flat[2]["verdict"].startswith("FALSIFIER"), flat[2]

    # and a run with no recorded direction refuses every claim
    a = _run(_vecs(1), leak=1.0)
    b = _run(_vecs(1), leak=0.35)
    for r in b["methods"][e336.ARM]["replicates"]:
        r["theta_direction"] = []
    no_dir = e336.reading({"instant": _write(a), "carry": _write(b)})
    assert all(row["verdict"].startswith("REFUSED") for row in e336.judge(no_dir)), e336.judge(no_dir)


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e336_the_direction_of_the_update.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e336.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the two runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["fingerprints"][0] == d["fingerprints"][1], d["fingerprints"]
    assert d["dim"] == 256 and d["n_tasks"] == 3, (d["dim"], d["n_tasks"])
