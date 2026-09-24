"""`--save-fisher` / `--fisher-from`, tested by the identity they exist for.

`e173`'s finding is that the Fisher is measured after each task's training, so every knob that moves the
forgetting level moves the penalty's inputs too -- which is why no single-field manipulation in this corpus can
separate "less room to forget" from "a weaker penalty". Storing the inputs makes that separation available, and
what makes the feature worth having is that a **replayed** run is bit-identical to the run that computed them:
anything less would mean the two runs are not being penalised by one term.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from clfly.connectome import graph

DATA = Path(graph.DEFAULT_DATA_DIR)
HAS_DATA = (DATA / graph.CONNECTIVITY_FILE).exists() and (DATA / graph.ANNOTATION_FILE).exists()
needs_data = pytest.mark.skipif(not HAS_DATA, reason="connectome data not downloaded")

#: small enough to run inside a test, large enough to train three tasks and compute a Fisher on each
TINY = ("--circuit-size", "300", "--iters", "5", "--repeats", "1", "--methods", "ewc", "--classes", "2",
        "--train", "24", "--test", "16", "--support", "40", "--batch", "8", "--fisher-batches", "2")


def test_the_two_flags_exist_and_are_documented(capsys):
    from experiments import e8_rate_network

    with pytest.raises(SystemExit):
        e8_rate_network.main(["--help"])
    text = capsys.readouterr().out
    assert "--save-fisher" in text and "--fisher-from" in text
    # the help says WHY, because the flags exist for one experiment's question and not as a convenience
    assert "penalty's OWN INPUTS" in text


@needs_data
def test_a_replayed_run_is_bit_identical_to_the_run_that_computed_the_inputs(tmp_path):
    from experiments import e8_rate_network

    saved, replayed = tmp_path / "saved.json", tmp_path / "replayed.json"
    store = tmp_path / "inputs"           # a DIRECTORY: one file per (method, replicate), because the Fisher is
                                          # seeded per replicate and so is a different object in each one
    assert e8_rate_network.main([*TINY, "--save-fisher", str(store), "--json-out", str(saved)]) == 0
    assert (store / "ewc_seed0.npz").is_file(), "one entry per method and replicate, named for both"
    assert e8_rate_network.main([*TINY, "--fisher-from", str(store), "--json-out", str(replayed)]) == 0

    a = json.loads(saved.read_text(encoding="utf-8"))["methods"]["ewc"]["replicates"]
    b = json.loads(replayed.read_text(encoding="utf-8"))["methods"]["ewc"]["replicates"]
    for ra, rb in zip(a, b):
        assert np.array_equal(np.asarray(ra["forgetting_per_task"]), np.asarray(rb["forgetting_per_task"]))
        assert ra["mean_forgetting"] == rb["mean_forgetting"]
    # and the only config keys that differ are the two flags themselves: nothing else moved
    ca = json.loads(saved.read_text(encoding="utf-8"))["config"]
    cb = json.loads(replayed.read_text(encoding="utf-8"))["config"]
    differ = {k for k in set(ca) | set(cb) if ca.get(k) != cb.get(k)}
    assert differ <= {"save_fisher", "fisher_from", "json_out"}


def test_no_help_string_contains_a_bare_percent():
    """The whole `--help` of the main runner was broken by two of them, and the guard is three lines.

    `argparse` runs the help string through `%`-formatting, so a bare `70%` raises
    `TypeError: %o format: an integer is required` and **the flag list cannot be printed at all** -- which is how
    two `%` characters in `--anchor-bias`'s help hid the runner's entire `--help` until `--save-fisher` needed to
    be documented. `%%` is the escape, and this test is what keeps the next one from hiding it again.
    """
    import ast

    src = Path("experiments/e8_rate_network.py").read_text(encoding="utf-8")
    offenders = []
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument"):
            continue
        for kw in node.keywords:
            # `%%` is the escape argparse accepts, so a *bare* percent is the defect -- and `70%%` must pass
            if kw.arg == "help" and isinstance(kw.value, ast.Constant)                     and "%" in str(kw.value.value).replace("%%", ""):
                offenders.append(([a.value for a in node.args if isinstance(a, ast.Constant)],
                                  kw.value.value[:60]))
    assert not offenders, f"a help string would break --help: {offenders}"


@needs_data
def test_a_missing_entry_for_this_replicate_is_refused_rather_than_borrowed(tmp_path):
    """Replaying another replicate's inputs would silently be a different penalty, so it must stop."""
    from experiments import e8_rate_network

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SystemExit, match="no entry for"):
        e8_rate_network.main([*TINY, "--fisher-from", str(empty), "--json-out", str(tmp_path / "x.json")])
