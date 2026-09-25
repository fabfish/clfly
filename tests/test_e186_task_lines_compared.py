"""`e186` compares the two task lines and asks what a name actually selects.

The check's own arms, each of which caught something live: a value that matches **no** annotation value (the
analytic `heading` named `PB` and `NO`, both empty everywhere), a value the two lines disagree about inside one
assembly name (`ALIN`), an assembly the network suite does not have at all, and the read-out mode a run used --
because with a shared head the suite's read-out populations are inert and the tasks differ only in where the
stimulus enters.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from experiments import e186_task_lines_compared as e186


class Asm:
    def __init__(self, name, column, values):
        self.name, self.column, self.values = name, column, values


FRAME = pd.DataFrame({"cell_type": ["KC", "KC", "EPG", "PFN", "Nod1", "LAL1"],
                      "cell_class": ["Kenyon_Cell", "Kenyon_Cell", "CX", "CX", "nan", "nan"]})


def test_a_value_that_selects_nothing_anywhere_is_flagged_with_its_likely_intent():
    """`heading` asked `cell_type` for `PB` and `NO`: 0 in every column, and `Nod1` is what `NO` meant."""
    census = e186.value_census((Asm("heading", "cell_type", ("EPG", "PB", "NO")),), FRAME)
    by_value = {c["value"]: c for c in census}
    assert by_value["EPG"]["matches_nowhere"] is False and by_value["EPG"]["counts"]["cell_type"] == 1
    assert by_value["PB"]["matches_nowhere"] is True and by_value["PB"]["near_miss"] == []
    assert by_value["NO"]["matches_nowhere"] is True
    assert "Nod1" in by_value["NO"]["near_miss"], "the near-miss is what turns the flag into an edit"


def test_a_value_inside_the_other_column_is_not_a_defect():
    """`LAL1` exists as a cell_type and not as a cell_class: asking `cell_class` for it is a 0 that means something
    different from a name that exists nowhere -- and the census reports both counts so the two can be told apart."""
    census = e186.value_census((Asm("cx", "cell_class", ("LAL",)),), FRAME)
    assert census[0]["counts"] == {"cell_type": 1, "cell_class": 0}
    assert census[0]["matches_nowhere"] is False


def test_the_two_lines_are_compared_by_assembly_and_by_value():
    specs = (("odour_identity", ("cell_type", ("KC",)), ("cell_class", ("MBON",))),
             ("heading", ("cell_type", ("EPG",)), ("cell_class", ("CX",))))
    assemblies = (Asm("odour_identity", "cell_type", ("KC",)),
                  Asm("odour_valence", "cell_class", ("MBON", "DAN")),
                  Asm("heading", "cell_type", ("EPG",)),
                  Asm("odour_input", "cell_class", ("ALPN", "ALLN", "ALIN")))
    lines = e186.line_differences(specs, assemblies)
    assert lines["assemblies_missing_from_the_network_suite"] == ["odour_valence", "odour_input"]
    assert lines["value_differences"] == []


def test_a_column_difference_is_its_own_reading_of_the_same_name():
    specs = (("heading", ("cell_class", ("EPG",)), ("cell_class", ("CX",))),)
    lines = e186.line_differences(specs, (Asm("heading", "cell_type", ("EPG",)),))
    assert lines["value_differences"][0]["why"] == "column differs"


def test_the_readout_census_says_which_mode_each_run_used(tmp_path):
    """The distinction that decides whether the specs' read-out populations matter at all: a shared draw and a
    whole-state head make every task differ only in where the stimulus enters."""
    runs = tmp_path / "runs"
    runs.mkdir()
    for i, cfg in enumerate(({"shared_head": True, "readout_size": 32},
                             {"shared_head": True, "readout_size": 0},
                             {"shared_head": False, "readout_size": 0},
                             {"shared_head": True, "readout_size": 32})):
        (runs / f"e{i}_x.json").write_text(json.dumps({"config": cfg}), encoding="utf-8")
    (runs / "audit.json").write_text(json.dumps({"summary": 1}), encoding="utf-8")
    modes = e186.readout_modes(runs)
    assert modes == {"one shared draw of --readout-size neurons": 2, "the whole state, one shared head": 1,
                     "per-task heads (the spec populations ARE the read-outs)": 1}


def test_the_live_code_has_no_value_that_selects_nothing_and_the_lines_still_differ():
    """The gate. The two dropped values (`PB`, `NO`) are the fix this check bought; the remaining differences are
    the registered extension and the one value the network spec omits, and both are printed rather than flagged."""
    res = e186.audit(Path("runs"))
    assert res["values_matching_nowhere"] == [], res["values_matching_nowhere"]
    assert res["lines"]["assemblies_missing_from_the_network_suite"] == ["odour_valence", "innate_odour"]
    dropped = {d["assembly"]: d for d in res["lines"]["value_differences"]}
    assert dropped["odour_input"]["values"] == ["ALIN"]
    assert res["n_analytic_assemblies"] == 5 and res["n_network_specs"] == 3
    modes = res["readout_modes"]
    assert modes["one shared draw of --readout-size neurons"] >= 50, modes
