"""`e163`'s two products, on synthetic inputs: the re-execution command and the run-to-run floor.

The floor is a *classification*, and its three cases are the whole content: same recorded environment (the floor
itself), two recorded environments (a named cause), and no recorded environment (movement nothing explains). A
version that pooled them would report the corpus's worst movement as `0.0396` without saying that it sits in runs
that cannot say why -- which is the sentence this unit exists to prevent.

`command_from_config` is tested for the `e153` defect specifically: it must emit a field even when that field
equals the runner's default, because omitting `--lam` *is* λ = 1.0. The helper is the reason `e164`'s command could
be derived rather than paraphrased.
"""

from __future__ import annotations

import pytest

from experiments import e163_repeat_floor as e163


def group(runs, names, environments, arms, differing=(), subgroups=()):
    """One `group_repeats` record, with only the fields `floor` reads."""
    return {"runs": runs, "names": list(names), "environments": environments,
            "subgroups": list(subgroups),
            "arms": {m: {"present": True, "movement_forgetting": v[0], "movement_accuracy": v[1],
                         "exact": m not in differing} for m, v in arms.items()},
            "arms_identical": sorted(m for m in arms if m not in differing),
            "arms_differing": sorted(differing)}


def subgroup(runs, environments, arms):
    """One `group_repeats` subgroup record -- a slice of a multi-environment group."""
    return {"environment": environments, "runs": runs, "names": [f"s{i}.json" for i in range(runs)],
            "arms": {m: {"present": True, "movement_forgetting": v[0], "movement_accuracy": v[1]}
                     for m, v in arms.items()}}


RECORDED = '{"omp_num_threads": "unset", "torch_num_threads": 20}'
OTHER = '{"omp_num_threads": "1", "torch_num_threads": 20}'


def test_a_field_is_emitted_even_when_it_equals_the_runners_default():
    """The `e153` defect: the runner's default λ is 1.0, so an omitted `--lam` is not "the default", it is 1.0."""
    cfg = {"lam": 1.0, "repeats": 40, "methods": "naive,ewc"}
    parts = e163.command_from_config(cfg)
    assert "--lam" in parts and parts[parts.index("--lam") + 1] == "1.0"
    assert parts[parts.index("--repeats") + 1] == "40"
    # every non-boolean, non-json_out key appears
    for key, flag in (("lam", "--lam"), ("repeats", "--repeats"), ("methods", "--methods")):
        assert flag in parts


def test_an_unmapped_config_key_is_refused_rather_than_left_to_the_default():
    """Two refusals, and the test names which: a key the *mapping* lacks, and a config no runner can claim.

    The first is the `e153` defect's guard; the second is what the runner inference adds when the caller does not
    say which runner wrote the artifact -- and they are different sentences because they are different problems.
    """
    with pytest.raises(ValueError, match="maps to no e8_rate_network.py runner flag"):
        e163.command_from_config({"lam": 0.003, "mystery_knob": 7}, runner="e8_rate_network.py")
    with pytest.raises(ValueError, match="cannot tell which runner"):
        e163.command_from_config({"lam": 0.003, "mystery_knob": 7})


def test_store_true_flags_are_read_in_the_direction_of_their_own_default():
    # default False: omitting it is faithful, so False emits nothing
    assert "--frozen-body" not in e163.command_from_config({"frozen_body": False}, runner="e8_rate_network.py")
    assert "--frozen-body" in e163.command_from_config({"frozen_body": True}, runner="e8_rate_network.py")
    # default True with no negative form: a recorded False cannot be reproduced at all
    with pytest.raises(ValueError, match="no command-line form"):
        e163.command_from_config({"normalise_fisher": False}, runner="e8_rate_network.py")
    assert "--normalise-fisher" in e163.command_from_config({"normalise_fisher": True}, runner="e8_rate_network.py")


def test_the_output_path_is_replaced_rather_than_reproduced():
    parts = e163.command_from_config({"lam": 0.003, "json_out": "runs/old.json"}, json_out="runs/new.json", runner="e8_rate_network.py")
    assert "runs/old.json" not in parts
    assert parts[parts.index("--json-out") + 1] == "runs/new.json"


def test_the_floor_separates_a_named_cause_from_an_unattributable_move():
    groups = [
        group(7, ["a.json"] * 7, {RECORDED: 7}, {"naive": (0.0, 0.0)}),
        group(2, ["b.json", "c.json"], {RECORDED: 1, OTHER: 1},
              {"replay": (0.0208, 0.0139)}, differing=("replay",),
              subgroups=(subgroup(1, RECORDED, {"replay": (0.0, 0.0)}),
                         subgroup(1, OTHER, {"replay": (0.0, 0.0)}))),
        group(2, ["d.json", "e.json"], {"unrecorded": 2},
              {"ewc-block": (0.0208, 0.0194)}, differing=("ewc-block",)),
    ]
    out = e163.floor(groups)
    # the floor is the one-environment groups plus the *within-subgroup* movement of the two-environment one
    assert out["floor_within_one_recorded_environment"]["worst_forgetting"] == 0.0
    assert out["movement_across_recorded_environments"]["worst_forgetting"] == pytest.approx(0.0208)
    assert out["movement_without_a_recorded_environment"]["worst_forgetting"] == pytest.approx(0.0208)
    # "runs in a group that moved" counts the two-environment group as well: one of its two runs moved
    assert out["runs_in_a_group_that_moved"] == 4
    assert out["runs_in_one_recorded_environment"] == 7
    assert out["moved_arms"] == {"ewc-block": pytest.approx(0.0208), "replay": pytest.approx(0.0208)}


def test_a_within_subgroup_move_counts_against_the_floor_and_not_against_the_cause():
    """A multi-environment group's *subgroups* are same-environment comparisons, so they belong in the floor."""
    groups = [group(3, ["a.json", "b.json", "c.json"], {RECORDED: 2, OTHER: 1},
                    {"replay": (0.0208, 0.0139)}, differing=("replay",),
                    subgroups=(subgroup(2, RECORDED, {"replay": (0.0170, 0.0100)}),
                               subgroup(1, OTHER, {"replay": (0.0, 0.0)})))]
    out = e163.floor(groups)
    assert out["floor_within_one_recorded_environment"]["worst_forgetting"] == pytest.approx(0.0170)
    assert out["floor_within_one_recorded_environment"]["groups"] == 0     # no one-environment group here


def test_the_floor_is_zero_only_over_groups_that_record_one_environment():
    """A pooled floor would be the worst movement anywhere; the reported one must ignore the unattributable."""
    groups = [
        group(2, ["a.json", "b.json"], {RECORDED: 2}, {"ewc": (0.0, 0.0)}),
        group(2, ["c.json", "d.json"], {"unrecorded": 2}, {"ewc": (0.0396, 0.0458)}, differing=("ewc",)),
    ]
    out = e163.floor(groups)
    assert out["floor_within_one_recorded_environment"]["worst_forgetting"] == 0.0
    assert out["movement_without_a_recorded_environment"]["worst_forgetting"] == pytest.approx(0.0396)
    assert out["arms_identical"] == 1 and out["arms_compared"] == 2
    assert out["groups_with_no_movement"] == 1


# --- the second runner: the analytic line's commands must be derivable too ------------------------------------


def test_the_helper_knows_the_analytic_runner_and_infers_it_from_the_config_keys():
    """`e3_basis_selection` produced the ladder comparisons, and its commands were written by hand until now.

    Inference is the same test `e172` makes for authorship -- a `config` is `vars(args)`, so a runner can have
    written it only if it can name every field -- and it is why the helper needs no `--runner` in the common case.
    """
    cfg = {"circuit_size": 300, "support": 30, "seeds": 12, "q": 0.02, "ladder": True, "topologies": ("real",)}
    assert e163.runner_for(cfg) == ["e3_basis_selection.py"]
    parts = e163.command_from_config(cfg, json_out="runs/x.json")
    assert parts[1].endswith("e3_basis_selection.py")
    # a `store_true` flag is emitted, a string-valued field is passed through, and `None` is omitted
    assert "--ladder" in parts and parts[parts.index("--support") + 1] == "30"
    # a training-runner config infers to the other runner, so the two maps do not collide
    assert e163.runner_for({"lam": 0.003, "methods": "ewc", "repeats": 40, "seed0": 0, "train": 96, "test": 48,
                            "batch": 32, "iters": 500, "lr": 0.003}) == ["e8_rate_network.py"]


def test_a_tuple_valued_field_is_joined_because_the_runner_itself_splits_on_commas():
    """`e3_basis_selection` transforms its namespace before dumping it, so the artifact holds a tuple.

    `args.topologies = tuple(t for t in args.topologies.split(",") if t)` is the runner's own line, so the join is
    that transform's inverse -- and a field the helper cannot invert is refused rather than emitted as a Python
    repr, which would be a command that cannot run.
    """
    parts = e163.command_from_config({"topologies": ("real", "swap0.5")}, runner="e3_basis_selection.py")
    assert parts[parts.index("--topologies") + 1] == "real,swap0.5"
    assert not any("(" in p for p in parts), "no Python repr may reach the command line"
    with pytest.raises(ValueError, match="maps to no e3_basis_selection.py runner flag"):
        e163.command_from_config({"not_a_flag": 1}, runner="e3_basis_selection.py")


def test_the_census_reports_coverage_and_the_refusals_by_reason(capsys):
    """Most of the corpus derives a command, and the refusals are two kinds with two different remedies.

    The maps come from `e172`'s registry now, which is what took coverage from two hand-mapped runners to every
    parser in the tree: **295 configs derive a command and 21 are refused**, and the four that no runner fits are
    **exactly the artifacts `e172` found carrying a key no parser defines** (`save_theta`, which two runners assign
    at runtime). The other seventeen are small configs several parsers could have written, which a caller lifts by
    naming the runner -- so the two refusals are different problems and the census keeps them apart.
    """
    assert e163.main(["--census"]) == 0
    out = capsys.readouterr().out
    handled = int(out.split("configs the path handles:")[1].split()[0])
    none_fit = int(out.split("NO runner fits:")[1].split()[0])
    several = int(out.split("SEVERAL fit:")[1].split()[0])
    assert handled >= 250 and none_fit == 4 and several >= 10
    assert len(e163.RUNNERS) > 50, "the maps are read from every parser, not from two hand-written ones"


def test_the_plain_run_does_not_crash(capsys):
    """`e163` crashed on every plain run until 2026-09-25 and its `--census` path worked, which is how it went
    unnoticed: a local `import load_artifacts` inside the census branch made the name local to the whole function,
    so the `group_repeats(load_artifacts())` call below it raised `UnboundLocalError` whenever `--census` was not
    passed. The regression guard is that the default entry point returns 0 at all.
    """
    assert e163.main([]) == 0
    out = capsys.readouterr().out
    assert "executed more than once" in out
