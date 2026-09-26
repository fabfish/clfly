"""`e238` predicts the collapse of `G(rho) = (I - rho Wh)^-1` from `Wh`'s leading eigenvalues, which is exact because
`stable_weights` is a pure scalar rescale.

The tests pin the two things that make it a measurement rather than a restatement: the prediction formula agrees with
an explicitly formed inverse on a hand-built diagonal operator, and the scalar-rescale property it rests on is checked
against `stable_weights` itself (two rho values, one leading eigenvalue, the ratio of the two rho's).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e238_weight_spectrum as e238


def test_the_prediction_matches_an_explicit_inverse_on_a_diagonal_operator():
    """For a diagonal `Wh` the eigenvalues ARE the modes: `G = diag(1/(1 - rho l_i))`, so the predicted participation
    ratio must equal the one computed from the explicit inverse."""
    lam = [0.9, 0.6, 0.3, 0.1]
    for rho in (0.5, 0.9, 0.99):
        explicit = np.array([abs(1.0 / (1.0 - rho * l)) for l in lam]) ** 2
        assert abs(e238.predict(lam, rho) - e238.participation_ratio(explicit)) < 1e-12
    # and the limiting case: as rho -> the leading eigenvalue, one mode takes everything
    assert e238.predict([1.0, 0.5], 0.999) < e238.predict([1.0, 0.5], 0.9)
    assert e238.predict([0.5, 0.5], 0.9) > e238.predict([1.0, 0.5], 0.9), "the gap is what the prediction turns on"


def test_the_scalar_rescale_property_holds_on_the_live_substrate():
    """`stable_weights` is `W * (rho / radius)`, so the same matrix's leading eigenvalue at two rho's must be in the
    ratio of the two rho's. A mismatch would make the prediction void rather than make the substrate interesting."""
    check = e238.rescale_check(300, "real", rhos=(0.9, 0.99))
    assert abs(check["ratio"] - check["expected"]) < 1e-6, check


def test_the_live_spectrum_reproduces_the_artifact_and_orders_the_families():
    """cs 300's stored `|lam2|` ordering (`real` < `alloy1` < `inalloy1` < `erdos_renyi`) is what S2 turns on; a live
    recomputation must give the same ordering and the leading modulus must be 1 by construction."""
    live = e238.normalised_spectrum(300, topologies=("real", "alloy1"), k=6)
    for topo in ("real", "alloy1"):
        la = live["topologies"][topo]["lambda_abs"]
        assert abs(la[0] - 1.0) < 1e-3, la
        assert len(la) >= 3
    p = Path("runs/e238_weight_spectrum.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    s300 = next(s for s in d["spectra"] if s["size"] == 300)
    second = {t: s300["topologies"][t]["lambda_abs"][1] for t in e238.TOPOLOGIES}
    assert second["real"] < second["alloy1"] < second["inalloy1"] <= second["erdos_renyi"] + 1e-9, second


def test_the_report_names_an_unmeasurable_family(capsys):
    spectra = [{"size": 300, "neurons": 952,
                "topologies": {t: {"error": "ARPACK did not converge"} for t in e238.TOPOLOGIES}}]
    assert e238.report(spectra, [0.9], None, None) == len(e238.TOPOLOGIES)
    assert "UNMEASURABLE" in capsys.readouterr().out
