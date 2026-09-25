"""Writing run artifacts that a strict JSON parser will accept.

Every experiment writes a ``runs/*.json`` record, and those files are the evidence for the
numbers in the paper. Python's :mod:`json` writes ``NaN`` and ``Infinity`` by default --
extensions that are **not** in the JSON specification -- and reads them back by default, so
the non-conformance is invisible from inside this project and obvious to everyone else.
``JSON.parse`` in JavaScript, ``serde_json`` in Rust, ``encoding/json`` in Go and
``pandas.read_json`` all reject the files that :mod:`json` happily produced.

It is not hypothetical here: every artifact of the rate-network line contains ``NaN``, because
the retention matrix is initialised to ``NaN`` for the task pairs that have not been trained
yet -- a meaningful "not applicable" that belongs in the file as ``null``.  ``e98`` measured the
corpus: **13 of 216 artifacts** under ``runs/`` were refused by a strict parser, eight of them
rate-network and five carrying ``NaN`` from a ratio instead; those thirteen have been normalised
in place with every value verified unchanged.  **And the debt is in the writers, not the files:
of 72 modules, 32 write with :func:`json.dump` directly and 10 use this one**, so re-running a
direct writer restores its ``NaN`` -- demonstrated by re-running ``e38_variance_budget.py``,
which put all sixteen of its tokens back.

``nonfinite_to_null`` rewrites non-finite floats as ``None`` recursively, touching only the
values that are already unrepresentable, and ``write_json`` is the drop-in replacement for
``Path.write_text(json.dumps(...))``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


def nonfinite_to_null(obj):
    """Recursively replace non-finite floats with ``None``.

    Handles the containers the experiments actually produce: dicts, lists, tuples, numpy
    arrays (via ``tolist``, which also converts numpy scalars), and plain floats. Anything
    else is returned unchanged, so a caller that has already stringified a value keeps it.
    """
    if isinstance(obj, dict):
        return {k: nonfinite_to_null(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [nonfinite_to_null(v) for v in obj]
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if hasattr(obj, "tolist"):                      # numpy scalars and arrays
        return nonfinite_to_null(obj.tolist())
    return obj


def duration_field(payload: dict) -> str | None:
    """Which spelling this artifact recorded its duration under, or ``None`` if it recorded none.

    The corpus uses two, and `e205` measured that the split is not random: the analytic line
    (`e3_basis_selection`, `e9`, `e13`, `e58`, `e79`) writes ``timing = {"total_s": ...}`` and carries no
    ``methods`` dict, and every trained runner writes a top-level ``timing_s``.
    """
    if isinstance(payload.get("timing_s"), (int, float)):
        return "timing_s"
    timing = payload.get("timing")
    if isinstance(timing, dict) and isinstance(timing.get("total_s"), (int, float)):
        return "timing.total_s"
    return None


def duration_seconds(payload: dict) -> float | None:
    """A run's wall-clock duration in seconds, under **either** spelling the corpus uses.

    Every reader of a duration goes through this function rather than through a key, because the key is
    a property of which instrument wrote the artifact and not of the quantity: a reader keying on
    ``timing_s`` cannot see the thirteen analytic artifacts, and one keying on ``timing.total_s`` cannot
    see the other 298 (`e205`). The two spellings are the same measurement -- both are ``time.time() - t0``
    taken at the end of ``main`` -- so they are interchangeable and the caller needs no branch.
    """
    field = duration_field(payload)
    if field == "timing_s":
        return float(payload["timing_s"])
    if field == "timing.total_s":
        return float(payload["timing"]["total_s"])
    return None


def write_json(path, obj, indent: int = 1) -> None:
    """Write ``obj`` as strict, spec-conformant JSON, creating parent directories.

    ``nonfinite_to_null`` is what makes the output conformant, and it needs no second check:
    it handles plain floats and anything numpy, and everything else that :mod:`json` cannot
    serialise goes through ``default=str``, which produces a *quoted* string rather than a
    bare ``NaN`` token.  (A first version of this function re-parsed the text with
    ``parse_constant`` set to raise.  A test showed the check could not fire for any input,
    because ``default=str`` had already quoted the offending value, so it was removed rather
    than left in as decoration.)

    The one consequence worth knowing: an unserialisable object lands in the file as its
    ``str``, which is valid JSON but may be unhelpful to a reader.  That is a property of the
    experiment's payload, not of this writer.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nonfinite_to_null(obj), indent=indent, default=str))
