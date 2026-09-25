"""`e187` classifies a payload's tasks by the builder that made them, from two independent signals.

The check exists because the answer changes what the rest of the project's claims are about: `make_suite` drives
tasks into identified circuits and `make_overlap_suite` gives them random supports, and the plan block, `e185` and
`e186` all describe the first while the corpus's replicates are overwhelmingly the second. A classifier that read
only the config key would misclassify every artifact older than the flag, and one that read only the task names
would have nothing to disagree with -- so both are read and their agreement is the check.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e187_suite_provenance as e187


def build(tmp_path: Path, artifacts: dict[str, dict]) -> Path:
    runs = tmp_path / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    for name, payload in artifacts.items():
        (runs / name).write_text(json.dumps(payload), encoding="utf-8")
    return runs


def test_the_config_key_and_the_task_name_agree_on_the_overlap_family(tmp_path):
    runs = build(tmp_path, {"a.json": {"config": {"input_overlap": 0.0, "repeats": 40},
                                       "tasks": [{"name": "ov0_t0"}, {"name": "ov0_t1"}]}})
    res = e187.audit(runs)
    assert res["by_family"] == {e187.OVERLAP: 1}
    assert res["replicates_by_family"] == {e187.OVERLAP: 40}


def test_an_artifact_older_than_the_flag_is_the_assembly_suite_and_not_a_disagreement(tmp_path):
    """The five `e8_*` payloads: no `input_overlap` key at all, assembly task names. The overlap builder is
    reachable only through the flag, so a payload without the key predates it -- the same reading `e172` takes of a
    config that carries a subset of today's flags."""
    runs = build(tmp_path, {"e8_basis.json": {"config": {"repeats": 3}, "tasks": [{"name": "odour_identity"}]}})
    res = e187.audit(runs)
    assert res["by_family"] == {e187.ASSEMBLY: 1}
    assert res["n_disagreements"] == 0


def test_a_real_disagreement_is_reported_rather_than_resolved(tmp_path):
    """An `ov0_` task name with `input_overlap: None` cannot both be true, and the classifier says so instead of
    picking the signal it trusts -- it is the one state this file cannot classify."""
    runs = build(tmp_path, {"bad.json": {"config": {"input_overlap": None, "repeats": 5},
                                         "tasks": [{"name": "ov0_t0"}]}})
    res = e187.audit(runs)
    assert res["n_disagreements"] == 1
    assert "while the task name" in res["disagreements"][0]["why"]
    assert e187.report(res) == 1


def test_a_payload_without_tasks_is_not_counted_at_all(tmp_path):
    runs = build(tmp_path, {"audit.json": {"config": {"input_overlap": 0.0}, "summary": 1}})
    res = e187.audit(runs)
    assert res["artifacts_with_tasks"] == 0


def test_the_live_corpus_is_the_overlap_family_and_the_two_signals_never_disagree():
    """The gate, and the measurement itself: the assembly suite is a small minority of the replicates."""
    res = e187.audit(Path("runs"))
    assert res["n_disagreements"] == 0, res["disagreements"]
    assert res["by_family"][e187.OVERLAP] >= 100
    assert res["replicates_by_family"][e187.OVERLAP] >= 10 * res["replicates_by_family"][e187.ASSEMBLY]
    assert res["artifacts_with_tasks"] == sum(res["by_family"].values())
