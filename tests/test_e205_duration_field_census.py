from __future__ import annotations

import json
from pathlib import Path

from clfly.bench.artifacts import duration_field, duration_seconds
from experiments import e205_duration_field_census as e205


def art(path: Path, **payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"config": payload.pop("config", {"circuit_size": 800}), **payload}),
                    encoding="utf-8")
    return path


def test_one_quantity_two_spellings_and_the_reader_takes_either():
    """The analytic line writes `timing = {"total_s": ...}` and the trained runners write `timing_s`. A reader
    that keys on one spelling is blind to the other line, which is the whole defect this module is about."""
    assert duration_seconds({"timing_s": 12.5}) == 12.5
    assert duration_seconds({"timing": {"total_s": 34.0}}) == 34.0
    assert duration_field({"timing": {"total_s": 34.0}}) == "timing.total_s"
    assert duration_seconds({"config": {}}) is None
    # a `timing` block that holds something other than a total is not a duration, and the reader must not
    # invent one: the first version of this branch did `payload["timing"]["total_s"]` unguarded
    assert duration_seconds({"timing": {"total_s": None}}) is None
    assert duration_seconds({"timing": "fast"}) is None


def test_a_run_like_artifact_with_no_duration_is_listed_and_an_undeclared_one_counts(tmp_path):
    art(tmp_path / "e900_run.json", methods={"naive": {}})
    art(tmp_path / "e900_summary.json", config={"circuit_size": 800, "note": "hand-built"})
    res = e205.census(tmp_path)
    assert [w["artifact"] for w in res["no_duration"]] == ["e900_run.json"], res["no_duration"]
    assert res["run_like"] == 1
    # a hand-built summary is not run-like, so its absent duration is not a gap -- and that is a scope
    # decision the module makes explicitly rather than a consequence of which key it happens to read
    assert "e900_summary.json" not in res["no_duration"]


def test_a_third_spelling_is_a_violation(tmp_path):
    """The `e201` failure, one level over: a hand-written vocabulary misses the field a new writer invents.
    Here the vocabulary is declared and anything outside it with a duration-shaped name is counted -- including
    a key like `time_used`, since the check matches the key's NAME rather than its meaning, and a key whose name
    says nothing about time is passed without argument."""
    art(tmp_path / "e901_run.json", timing_seconds=99.0, methods={"naive": {}})
    art(tmp_path / "e901_other.json", iters=3, methods={"naive": {}})
    res = e205.census(tmp_path)
    assert res["unknown_spellings"] == [{"artifact": "e901_run.json", "key": "timing_seconds"}]
    assert e205.strange_spellings({"time_used": 3.0}) == ["time_used"]
    assert e205.strange_spellings({"total_seconds": 3.0}) == []
    assert duration_seconds({"timing_seconds": 99.0}) is None


def test_a_reader_that_bypasses_the_helper_is_counted_and_one_that_uses_it_is_not(tmp_path):
    """The check that keeps this fixed. It is a text check and its false-positive class is declared: a module
    that re-reads its own dict is a READ too, and is excluded by having imported the helper rather than by the
    receiver -- so a module that reads the raw key while also importing the helper is NOT counted, which is the
    honest limit of a check that cannot follow the data."""
    (tmp_path / "e900_reader.py").write_text(
        'from clfly.bench.artifacts import write_json\n\n\ndef go(d):\n    return d.get("timing_s")\n',
        encoding="utf-8")
    (tmp_path / "e901_reader.py").write_text(
        'from clfly.bench.artifacts import duration_seconds\n\n\ndef go(d):\n'
        '    t = duration_seconds(d)\n    return {"timing_s": t}\n', encoding="utf-8")
    sites = {s["module"]: s for s in e205.read_sites(tmp_path)}
    assert sites["e900_reader.py"]["kind"] == "read" and not sites["e900_reader.py"]["uses_helper"]
    assert sites["e901_reader.py"]["kind"] == "write" or sites["e901_reader.py"]["uses_helper"]


def test_the_three_duration_readers_go_through_the_helper_and_the_declared_writers_exist():
    """Pinned so the counts in the findings are read from the corpus rather than from the finding's prose: the
    three modules that read a duration from an artifact must go through the helper, and every declared gap names
    a runner that exists."""
    assert all(Path("experiments", m).exists() for m in e205.NO_DURATION.values())
    for module in ("e169_start_time_dating.py", "e190_side_rung_read.py", "e38_variance_budget.py"):
        assert "duration_seconds" in Path("experiments", module).read_text(encoding="utf-8"), module


def test_the_writer_of_a_gap_is_derived_from_the_parser_registry_and_not_declared():
    """The correction this check made on its own first run: two of the four gaps were declared to
    `e136_geometry_persistence.py`, which READS those grids, and the registry says otherwise. The derivation is
    max overlap rather than containment, because a flag that has since been removed makes containment fail."""
    # a synthetic registry where the best parser misses one key the artifact HAS -- the `save_theta` shape, a flag
    # that has since been removed, which is exactly why containment fails and ranking works
    parsers = {"writer.py": {"a", "b", "c"}, "reader.py": {"a"}, "other.py": {"a", "b"}}
    got = e205.derive_writer({"a": 1, "b": 2, "c": 3, "gone": 4}, parsers)
    assert got["module"] == "writer.py" and got["overlap"] == 3 and got["runner_up"] == 2
    assert got["missing_from_best"] == ["gone"], got
    # and against the real registry: e122's own flag set belongs to `e122_path_geometry.py`
    real = e205.parser_registry()
    flags = sorted(real["e122_path_geometry.py"])
    assert e205.derive_writer({k: 0 for k in flags}, real)["module"] == "e122_path_geometry.py"


def test_a_declared_runner_that_does_not_derive_is_counted_as_a_violation(tmp_path, monkeypatch):
    """The declaration is data, the derivation is evidence, and the two are compared rather than assumed. This is
    the correction the real table needed: `e136_geometry_persistence.py` reads the two barrier grids and defines
    three flags, so declaring it their writer is a defect the check reports instead of believing."""
    (tmp_path / "e900_run.json").write_text(
        json.dumps({"config": {**{f"k{i}": 0 for i in range(24)}, "circuit_size": 100, "iters": 5},
                    "check": {}}), encoding="utf-8")
    monkeypatch.setattr(e205, "NO_DURATION", {"e900_run.json": "e136_geometry_persistence.py"})
    res = e205.census(tmp_path)
    w = res["no_duration"][0]
    assert w["declared"] == "e136_geometry_persistence.py" and not w["declared_agrees"]
    assert e205.report(res) == 1, "a gap declared to the wrong writer is one violation and nothing else"

def test_the_third_spelling_lives_one_level_down_and_the_scan_descends_into_blocks():
    """The defect this module committed on its own first run: it declared `summary.time_s` a near-miss to inspect
    and scanned only the top level, so its vocabulary check could not see a spelling one level down. The scan now
    descends into the declared blocks -- and no further, which is stated rather than implied."""
    assert duration_seconds({"summary": {"time_s": 3600.0}}) == 3600.0
    assert duration_field({"summary": {"time_s": 3600.0}}) == "summary.time_s"
    # a declared spelling is not flagged; a nested one that is not declared is
    assert e205.strange_spellings({"summary": {"time_s": 1.0}}) == []
    assert e205.strange_spellings({"summary": {"time_taken_s": 1.0}}) == ["summary.time_taken_s"]
    # and the class this scan MISSES, asserted so it is a declared limit and not a surprise: `cpu_time_s`
    # starts with `cpu`, so the name rule does not see it -- and it names a different quantity anyway
    assert e205.strange_spellings({"environment": {"cpu_time_s": 1.0}}) == []


def test_an_artifact_carrying_a_key_its_own_parser_does_not_define_is_reported_as_plumbing(tmp_path):
    """`save_theta` generalised: `config` is `vars(args)` plus whatever the runner assigns into its own
    namespace. The census counts the artifacts, not the pattern, and prints the key and the injector so the next
    one is visible rather than inferred."""
    flags = sorted(e205.parser_registry()["e122_path_geometry.py"])
    (tmp_path / "e900_run.json").write_text(
        json.dumps({"config": {k: 0 for k in flags + ["save_theta"]}, "check": {}}), encoding="utf-8")
    res = e205.census(tmp_path)
    assert res["plumbing"] == [{"artifact": "e900_run.json", "module": "e122_path_geometry.py",
                               "missing": ["save_theta"]}], res["plumbing"]
