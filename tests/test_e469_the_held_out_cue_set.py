"""`e469` reads the held-out cue set on a frozen body, so the tests pin both faces of the four claims, the probe's
counts, and the refusal when a roll or a holdout block is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e469_the_held_out_cue_set as e469

TRAINED = ["loop_odour_identity", "loop_heading", "loop_odour_input"]
HELD = "loop_holdout"
REPS = 20


def _paired(mean, sigma, n=REPS):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma}


def _doc(same_differ=None, trained=None, held=HELD, thin=False, n_train=(96,), n_eval=(48,), blocks=True,
         baseline=(0.10, 2.50), over_baseline=(0.01, 0.40), ok=True, reason="a roll is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "probe": {}, "contrasts": {}, "spans": {}}
    rolls = {"bio": e469.ANCHOR_OF["bio"], "rand": e469.ANCHOR_OF["rand"]}
    probe = {}
    contrasts = {}
    for label, anchor in rolls.items():
        for arm in (e469.BASELINE, anchor, e469.BUFFER):
            probe[f"{label}/{arm}"] = {"task": [held] if blocks else [], "n_train": list(n_train),
                                       "n_eval": list(n_eval), "ridge": [1e-2],
                                       "before": 0.60, "after": 0.70}
        contrasts[f"{label}/baseline"] = _paired(*baseline)
        contrasts[f"{label}/{anchor}_over_baseline"] = _paired(*over_baseline)
        contrasts[f"{label}/{anchor}_before"] = _paired(0.0, 0.10)
        contrasts[f"{label}/{e469.BUFFER}_over_baseline"] = _paired(0.02, 0.60)
        contrasts[f"{label}/{e469.BUFFER}_before"] = _paired(0.0, 0.10)
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "readout_size")}
    same.update({"circuit": True, "tasks": True})
    if same_differ:
        same[same_differ] = False
    names = trained if trained is not None else TRAINED
    return {"ok": True, "reason": None,
            "runs": {label: {"anchor": anchor, "arms": {a: {"replicates": REPS} for a in
                                                        (e469.BASELINE, anchor, e469.BUFFER)}}
                     for label, anchor in rolls.items()},
            "same": same, "probe": probe, "contrasts": contrasts,
            "spans": {"rolls": 2, "same_fields": len(same), "thin": {"x/y": 19} if thin else {},
                      "trained": {label: list(names) for label in rolls},
                      "held_out": [held],
                      "n_train": list(n_train), "n_eval": list(n_eval), "replicates": [REPS],
                      "before": {label: 0.60 for label in rolls}, "after": {label: 0.70 for label in rolls},
                      "baseline": {label: (0.60, 0.70) for label in rolls}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e469.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: a held-out cue set the sequence never trained on, read better after training, unmoved by the anchoring
    j = _judge()
    for cid in ("VA1", "VA2", "VA3", "VA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # VA1: a field differing, a held-out set the sequence trained on, and thin replicates
    assert _judge(same_differ="config.iters")["VA1"].startswith("FALSIFIER")
    assert _judge(trained=TRAINED[:2] + [HELD])["VA1"].startswith("FALSIFIER")
    assert _judge(trained=TRAINED[:2])["VA1"].startswith("FALSIFIER")
    assert _judge(thin=True)["VA1"].startswith("FALSIFIER")

    # VA2: a block that records no task, and one whose count differs from the other roll's
    assert _judge(blocks=False)["VA2"].startswith("FALSIFIER")
    assert _judge(n_train=(96, 48))["VA2"].startswith("FALSIFIER")
    assert _judge(n_train=())["VA2"].startswith("FALSIFIER")

    # VA3: a contrast that does not resolve, and one of the wrong sign
    assert _judge(baseline=(0.02, 1.20))["VA3"].startswith("FALSIFIER")
    assert _judge(baseline=(-0.05, -3.00))["VA3"].startswith("FALSIFIER")

    # VA4: an anchor that moves the held-out reading against the baseline, in either direction
    assert _judge(over_baseline=(0.08, 2.40))["VA4"].startswith("FALSIFIER")
    assert _judge(over_baseline=(-0.08, -2.40))["VA4"].startswith("FALSIFIER")
    assert _judge(over_baseline=(0.05, 1.90))["VA4"].startswith("MET")

    #: a roll or a holdout block that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e469.judge(_doc(ok=False)))


def test_the_runs_and_the_bounds_are_registered():
    assert e469.RUNS["bio"].name == "e469_earned_label_neurons_holdout_20reps.json"
    assert e469.RUNS["rand"].name == "e469_earned_label_rand_neurons_holdout_20reps.json"
    assert e469.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e469.ANCHOR_OF
    assert (e469.BASELINE, e469.BUFFER) == ("naive", "replay")
    assert set(e469.IGNORED) == {"json_out", "save_theta", "methods"}, e469.IGNORED
    assert (e469.N_ARMS, e469.MIN_REPS, e469.N_TASKS, e469.SIGMA) == (3, 20, 3, 2.0)
    #: the holdout is a flag on the runner this unit drove, and the probe's ridge is the one the runner records
    assert set(e469.SHARED) == {"circuit", "tasks"}, e469.SHARED


def test_the_probe_reads_a_separable_task_and_the_flag_defaults_to_none():
    """The helper this unit put in the runner, and the default that keeps every earlier call unchanged."""
    import inspect

    import numpy as np

    from experiments import e8_rate_network as runner

    assert "holdout" in inspect.signature(runner.run_method).parameters
    assert inspect.signature(runner.run_method).parameters["holdout"].default is None

    class _Task:
        n_classes = 4
        readout_neurons = np.arange(4)

    class _Body:
        """A body whose last step *is* the one-hot label: the probe's best case."""

        def __call__(self, U, w=None):
            return U

    class _Flat(_Body):
        """A body with no class signal at all: the probe's floor."""

        def __call__(self, U, w=None):
            return U * 0.0 + 1.0

    n = 60
    rng = np.random.default_rng(0)
    y = rng.integers(0, 4, size=n)
    u = np.zeros((n, 3, 4), dtype=np.float32)
    u[:, -1, :] = np.eye(4)[y]
    task = _Task()
    task.u_train, task.y_train, task.u_test, task.y_test = u, y, u, y
    assert runner.probe_readout(_Body(), task) > 0.99
    assert runner.probe_readout(_Flat(), task) <= 0.5

    #: and the flag is in the runner's own parser, so the key a holdout run records is the one this unit reads
    src = Path("experiments/e8_rate_network.py").read_text(encoding="utf-8")
    assert "--loop-holdout" in src and "loop_holdout" in src


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e469_the_held_out_cue_set.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e469.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: two rolls of three arms is structural; the counts that grow with the corpus are read as floors
    assert sorted(d["runs"]) == ["bio", "rand"], sorted(d["runs"])
    for label, roll in d["runs"].items():
        assert len(roll["arms"]) >= e469.N_ARMS, label
        for arm, got in roll["arms"].items():
            assert got["replicates"] >= e469.MIN_REPS, (label, arm)
    assert len(d["probe"]) >= 2 * e469.N_ARMS, len(d["probe"])
    for key, got in d["probe"].items():
        assert len(got["task"]) == 1 and got["n_train"] and got["n_eval"], key
        assert 0.0 <= got["before"] <= 1.0 and 0.0 <= got["after"] <= 1.0, key
    assert d["spans"]["held_out"], d["spans"]
    assert set(d["spans"]["held_out"]) & {t for v in d["spans"]["trained"].values() for t in v} == set(), d["spans"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
