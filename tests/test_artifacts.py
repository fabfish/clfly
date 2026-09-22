"""Tests for the run-artifact writer.

The failure this guards against is invisible from inside Python: :mod:`json` writes ``NaN``
and ``Infinity`` by default and reads them back without complaint, so an artifact that half the
world's parsers reject looks fine here.  These tests parse the output the strict way.
"""

from __future__ import annotations

import json

import numpy as np

from clfly.bench.artifacts import nonfinite_to_null, write_json


def _strict(text: str):
    """``json.loads`` that refuses the non-standard constants, as most parsers do."""
    def reject(name):
        raise ValueError(name)
    return json.loads(text, parse_constant=reject)


# --------------------------------------------------------------------------
# the transform
# --------------------------------------------------------------------------
def test_nonfinite_floats_become_none():
    out = nonfinite_to_null({"a": 1.0, "b": float("nan"), "c": float("inf"),
                            "d": float("-inf"), "e": 0.0})
    assert out == {"a": 1.0, "b": None, "c": None, "d": None, "e": 0.0}


def test_it_walks_nested_containers():
    out = nonfinite_to_null({"x": [1.0, float("nan")], "y": {"z": (float("inf"), 2.0)}})
    assert out == {"x": [1.0, None], "y": {"z": [None, 2.0]}}


def test_numpy_scalars_and_arrays_are_handled():
    arr = np.array([1.0, np.nan, np.inf])
    assert nonfinite_to_null(arr) == [1.0, None, None]
    assert nonfinite_to_null(np.float64("nan")) is None
    assert nonfinite_to_null(np.int64(3)) == 3


def test_it_leaves_other_types_alone():
    assert nonfinite_to_null("nan") == "nan"
    assert nonfinite_to_null(None) is None
    assert nonfinite_to_null(True) is True


# --------------------------------------------------------------------------
# the writer
# --------------------------------------------------------------------------
def test_write_json_produces_something_a_strict_parser_accepts(tmp_path):
    # the retention matrix of the rate-network line is NaN in its untrained upper triangle
    R = np.full((3, 3), np.nan)
    R[2, 0] = 0.75
    path = tmp_path / "run.json"
    write_json(path, {"R": R, "gap": float("inf"), "spearman": 0.995})
    out = _strict(path.read_text())
    assert out["R"][0][0] is None
    assert out["R"][2][0] == 0.75
    assert out["gap"] is None
    assert out["spearman"] == 0.995


def test_write_json_makes_parent_directories(tmp_path):
    path = tmp_path / "deep" / "nested" / "run.json"
    write_json(path, {"ok": True})
    assert _strict(path.read_text()) == {"ok": True}


def test_an_unserialisable_object_lands_as_a_quoted_string(tmp_path):
    # the first version of `write_json` re-parsed its own output with `parse_constant` set to
    # raise, to catch a non-finite value that had slipped through. That check cannot fire:
    # `default=str` has already quoted anything json cannot serialise, so the offending token
    # is never bare. This test pins the actual behaviour instead.
    class Opaque:
        def __str__(self):
            return "NaN"

    path = tmp_path / "run.json"
    write_json(path, {"x": Opaque()})
    out = _strict(path.read_text())          # a strict parser accepts it
    assert out["x"] == "NaN"                 # ...as a string, not as a number


def test_finite_values_survive_a_round_trip(tmp_path):
    payload = {"a": [1, 2, 3], "b": {"c": 1.5}, "d": "text", "e": None, "f": True}
    path = tmp_path / "run.json"
    write_json(path, payload)
    assert _strict(path.read_text()) == payload
