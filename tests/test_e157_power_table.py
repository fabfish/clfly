"""`e157`'s arithmetic is one line and that is exactly why it needs pinning: the table's whole content is
`(z * sd / d)^2`, and a transposed term would still print plausible numbers.

The test also pins the two conventions the script depends on: the sd it uses is the **paired** per-seed sd
(`sem * sqrt(n)`), not the arms' own spread, and `seeds_for` returns infinity at a zero effect rather than a
division error or a huge finite number that would read like a real count.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from experiments import e157_power_table as e157


def test_seeds_for_is_the_closed_form_and_honours_its_two_edges():
    # n = (z * sd / d)^2: 3 sigma, sd 0.02, effect 0.01 -> (3*0.02/0.01)^2 = 36
    assert abs(e157.seeds_for(0.02, 0.01, 3) - 36) < 1e-9
    assert abs(e157.seeds_for(0.02, -0.01, 3) - 36) < 1e-9      # the sign of the effect does not matter
    assert abs(e157.seeds_for(0.02, 0.02, 2) - 4) < 1e-9
    # half the effect at the same sd costs four times the seeds
    assert abs(e157.seeds_for(0.02, 0.005, 3) / e157.seeds_for(0.02, 0.01, 3) - 4) < 1e-9
    assert math.isinf(e157.seeds_for(0.02, 0.0, 3))             # a zero effect is not "a very large n"


def test_paired_sd_is_the_paired_one_and_not_the_arms_spread():
    rng = np.random.default_rng(0)
    shared = rng.normal(0.0, 0.3, size=40)     # the seed effect both arms see, which is what pairing removes
    a = 0.9 + shared + rng.normal(0.0, 0.05, size=40)
    b = 0.8 + shared + rng.normal(0.0, 0.05, size=40)
    r = e157.paired(a, b)
    assert abs(r["sd"] - r["sem"] * math.sqrt(40)) < 1e-12      # sem * sqrt(n) == the paired sd
    assert r["sd"] < a.std(ddof=1) / 2                          # paired: the shared seed effect is gone
    assert abs(r["change"] - float((a - b).mean())) < 1e-12


def test_the_registry_resolves_and_every_contrast_is_readable():
    missing = [lab for lab, pa, ma, pb, mb in e157.CONTRASTS
               if e157.load(Path(pa), ma) is None or e157.load(Path(pb), mb) is None]
    assert missing == [], f"contrasts whose artifacts do not resolve: {missing}"
    # every contrast must carry the newest-task series too, since five of them are read on that axis
    a = e157.load(Path(e157.C2B_FROZEN), "naive")
    assert a is not None and a["n"] == 40 and len(a["newest"]) == 40
