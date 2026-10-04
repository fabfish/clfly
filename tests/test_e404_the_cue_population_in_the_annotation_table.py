"""`e404` screens five biological properties of the six cue populations, so the tests pin both faces of the five
claims, the refusal when the corpus or a run is absent, and the live screen the unit closes.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e404_the_cue_population_in_the_annotation_table as e404

#: the corpus's shape: the card's cue population is nearly maximally diverse, and so are two of the failing ones
GOOD = {
    "cue9": {"cueseed": 9, "gain": -0.2250, "cell_types": 12, "cell_classes": 6, "hemilineages": 11, "supertypes": 12,
             "largest_class_share": 1 / 3},
    "cue6": {"cueseed": 6, "gain": -0.2083, "cell_types": 11, "cell_classes": 7, "hemilineages": 11, "supertypes": 11,
             "largest_class_share": 0.25},
    "cue1": {"cueseed": 1, "gain": -0.1813, "cell_types": 12, "cell_classes": 6, "hemilineages": 10, "supertypes": 12,
             "largest_class_share": 5 / 12},
    "cue3": {"cueseed": 3, "gain": -0.1635, "cell_types": 11, "cell_classes": 5, "hemilineages": 12, "supertypes": 11,
             "largest_class_share": 5 / 12},
    "cue14": {"cueseed": 14, "gain": -0.1479, "cell_types": 11, "cell_classes": 7, "hemilineages": 10,
              "supertypes": 11, "largest_class_share": 0.25},
    "card": {"cueseed": None, "gain": 0.0854, "cell_types": 12, "cell_classes": 6, "hemilineages": 11,
             "supertypes": 12, "largest_class_share": 5 / 12},
}


def _doc(worlds=None, coverage=None, n_neurons=952, n_rows=139248, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when the corpus or a run is absent
        return {"ok": False, "worlds": {}, "properties": {}, "coverage": {}, "n_neurons": 0, "n_rows": 0,
                "order": None, "reason": reason}
    worlds = worlds if worlds is not None else {k: dict(v) for k, v in GOOD.items()}
    order = sorted(worlds, key=lambda n: worlds[n]["gain"])
    props = {}
    for p in e404.PROPERTIES:
        values = [worlds[n][p] for n in order]
        losers = [worlds[n][p] for n in order if n != "card"]
        props[p] = {"values": {n: worlds[n][p] for n in order},
                    "card_inside_the_losers": min(losers) <= worlds["card"][p] <= max(losers),
                    "strictly_orders": e404.strictly_orders(values)}
    return {"ok": True, "circuit": "mb+cx+al@n952", "n_neurons": n_neurons, "n_rows": n_rows,
            "coverage": coverage if coverage is not None else {c: 1.0 for c in e404.COLUMNS},
            "worlds": worlds, "properties": props, "order": order}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e404.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the annotations resolve, the card's cue population is inside every range, and none of the properties orders
    j = _judge()
    for cid in ("AE1", "AE2", "AE3", "AE4", "AE5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AE1: a column that does not cover the circuit, and a table under the bound
    assert _judge(coverage={c: (0.9 if c == "cell_type" else 1.0) for c in e404.COLUMNS})["AE1"].startswith("FALSIFIER")
    assert _judge(n_neurons=100)["AE1"].startswith("FALSIFIER")
    assert _judge(n_rows=10)["AE1"].startswith("FALSIFIER")

    # AE2: a card's cue population that is an extreme on a property, above and below the range
    assert _judge(worlds={**GOOD, "card": {**GOOD["card"], "cell_types": 20}})["AE2"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD, "card": {**GOOD["card"], "cell_classes": 1}})["AE2"].startswith("FALSIFIER")

    # AE3: every property constant across the populations
    flat = {k: {**v, **{p: 1 for p in e404.PROPERTIES}} for k, v in GOOD.items()}
    assert _judge(worlds=flat)["AE3"].startswith("FALSIFIER")

    # AE4: a failing world inside the bar, and the card's world not gaining
    assert _judge(worlds={**GOOD, "cue14": {**GOOD["cue14"], "gain": -0.05}})["AE4"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD, "card": {**GOOD["card"], "gain": -0.02}})["AE4"].startswith("FALSIFIER")

    # AE5: a property strictly monotone in the readings
    monotone = {k: dict(v) for k, v in GOOD.items()}
    for i, n in enumerate(sorted(monotone, key=lambda x: monotone[x]["gain"])):
        monotone[n]["hemilineages"] = i + 1
    assert _judge(worlds=monotone)["AE5"].startswith("FALSIFIER")

    #: the corpus or a run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e404.judge(_doc(ok=False)))


def test_the_five_columns_and_the_strict_ordering_test():
    #: the columns read are the annotation ladder's, and the ordering test is monotonicity rather than a correlation
    assert set(e404.COLUMNS) == {"cell_type", "cell_class", "ito_lee_hemilineage", "supertype"}, sorted(e404.COLUMNS)
    assert set(e404.PROPERTIES) == {"cell_types", "cell_classes", "hemilineages", "supertypes",
                                    "largest_class_share"}, e404.PROPERTIES
    assert e404.strictly_orders([1, 2, 3]) and e404.strictly_orders([3, 2, 1])
    assert not e404.strictly_orders([1, 1, 2]), "a tie is not an ordering"
    assert not e404.strictly_orders([11, 12, 12, 11]), "the corpus's supertypes"
    assert (e404.MIN_NEURONS, e404.MIN_ROWS, e404.MIN_VARYING) == (500, 100000, 3)


def test_the_live_screen_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e404_the_cue_population_in_the_annotation_table.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e404.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e404.judge(d)}
    #: the annotation join and the published readings are structural facts
    assert verdicts["AE1"].startswith("MET") and verdicts["AE4"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    #: the properties' values are the populations' own, so the screen is read off the artifact and not recomputed
    for p_ in e404.PROPERTIES:
        assert set(d["properties"][p_]["values"]) == set(d["worlds"]), p_
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
