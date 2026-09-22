"""Writing run artifacts that a strict JSON parser will accept.

Every experiment writes a ``runs/*.json`` record, and those files are the evidence for the
numbers in the paper. Python's :mod:`json` writes ``NaN`` and ``Infinity`` by default --
extensions that are **not** in the JSON specification -- and reads them back by default, so
the non-conformance is invisible from inside this project and obvious to everyone else.
``JSON.parse`` in JavaScript, ``serde_json`` in Rust, ``encoding/json`` in Go and
``pandas.read_json`` all reject the files that :mod:`json` happily produced.

It is not hypothetical here: every artifact of the rate-network line contains ``NaN``, because
the retention matrix is initialised to ``NaN`` for the task pairs that have not been trained
yet -- a meaningful "not applicable" that belongs in the file as ``null``. An audit of the
committed artifacts found seven files that a strict parser refuses.

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
