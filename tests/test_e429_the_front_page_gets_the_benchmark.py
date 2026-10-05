"""`e429` reads the front page's closed-loop section back against the card's artifact, so the tests pin both faces of
the five claims, the refusal when the README or the card is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e429_the_front_page_gets_the_benchmark as e429

#: a card shaped like `e428`'s, carrying every field the vocabulary reads
CARD = {
    "revision": 6,
    "trade": {"far_cells": 12, "far_newest_cost": 12, "far_oldest_min": 0.23333333432674408,
              "far_loss_max": 0.103125, "near_cells": 13, "near_newest_cost": 8, "near_oldest_max": 0.075},
    "terms": {"oldest_learning": 0.0, "newest_retention": 0.0, "middle_ratio_min": 3.9861111938953417},
    "arm_terms": {"retention_ratio_min": 7.128205670877801, "price_gap_max": 0.03437499403953559},
    "order": {"rolls": 16, "first_ahead": 16, "reversal_costs": [-0.0694, -0.0618, -0.0028],
              "penalty_worst_middle": 9},
    "controls": {"frozen_body_cells": 3, "frozen_body_worst_gain": 0.0017361114422480561,
                 "frozen_bias_gain_ratio": 0.26881725910234167, "frozen_bias_cut_ratio": 0.26578073490745047},
}
ROWS = {
    "the far-point cells": "12", "the far point's newest task cost": "12",
    "the oldest task's recovery at the far point": "0.2333", "the newest task's loss at the far point": "0.1031",
    "the near-point cells": "13", "the near point's newest task cost": "8",
    "the oldest task's recovery at the near point": "0.0750", "the oldest task's learning term": "0.0",
    "the newest task's retention term": "0.0", "the middle task's retention over its learning price": "3.99",
    "the buffer's retention over the penalty's": "7.13", "the two learning prices' gap": "0.0344",
    "the arm-rolls of the order axis": "16", "the arm-rolls with the first position ahead": "16",
    "the reversal's largest cost": "0.0694", "the reversal's smallest cost": "0.0028",
    "the penalty arm-rolls worst in the middle": "9", "the frozen-body cells": "3",
    "the largest gain on a frozen body": "0.0017", "the frozen bias's share of the buffer's gain": "0.27",
    "the frozen bias's share of the buffer's cut": "0.27",
}
FINDING = "docs/findings/2026-10-05-the-game-card-revision-six.md"


def _readme(rows=None, naming=True, findings=3, start=True, end=True, revision=6):
    body = "\n".join(f"| {k} | {v} |" for k, v in (ROWS if rows is None else rows).items())
    named = (f"the card at **revision {revision}** (`{e429.CARD.as_posix()}`)" if naming else "the card")
    found = " ".join(f"`{FINDING}`" for _ in range(findings))
    return (
        "# clfly\n\n## Status\n\nscope.\n\n"
        + (f"{e429.START}\n" if start else "")
        + "\n## The closed-loop benchmark\n\n"
        + named + "\n\n| clause | number |\n|---|---|\n" + body + "\n"
        + (f"{e429.END}\n" if end else "")
        + "and " + found + "\n\n## Next section\n"
    )


def _doc(rows=None, naming=True, findings=3, start=True, end=True, revision=6, card=None, ok=True,
         reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rows": {}, "unknown": [], "region": False, "artifact_named": False,
                "revision_named": False, "findings": [], "missing_findings": [], "card": None, "checked": {},
                "spans": {}}
    card = CARD if card is None else card
    rows = ROWS if rows is None else rows
    text = _readme(rows, naming, findings, start, end, revision)
    region = e429._region(text)
    section = region["section"] if region else ""
    checked = {l: e429._agrees(rows[l], e429._card_value(card, f), m)
               for l, (f, m) in e429.VOCABULARY.items() if l in rows}
    import re as _re
    findings_named = len(_re.findall(r"`?(docs/findings/[A-Za-z0-9_.\-]+\.md)`?", section))
    return {"ok": True, "reason": None, "rows": dict(rows), "unknown": sorted(l for l in rows if l not in
                                                                            e429.VOCABULARY),
            "region": region is not None, "artifact_named": e429.CARD.as_posix() in section,
            "revision_named": f"revision {card['revision']}" in section, "findings": [FINDING],
            "missing_findings": [], "card": card, "checked": checked,
            "spans": {"rows": len(rows), "vocabulary": len(e429.VOCABULARY), "findings_named": findings_named,
                      "missing": 0}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e429.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the front page's shape: the region carried, every row the card's own, the section naming artifact and revision
    j = _judge()
    for cid in ("BE1", "BE2", "BE3", "BE4", "BE5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BE1: a missing boundary at either end, an unknown label, the wrong artifact, the wrong revision
    assert _judge(start=False)["BE1"].startswith("FALSIFIER")
    assert _judge(end=False)["BE1"].startswith("FALSIFIER")
    assert _judge(rows={**ROWS, "an unknown clause": "1"})["BE1"].startswith("FALSIFIER")
    assert _judge(naming=False)["BE1"].startswith("FALSIFIER")
    assert _judge(revision=5)["BE1"].startswith("FALSIFIER")

    # BE2: a trade row that is not the card's
    assert _judge(rows={**ROWS, "the far-point cells": "11"})["BE2"].startswith("FALSIFIER")
    assert _judge(rows={**ROWS, "the oldest task's recovery at the far point": "0.30"})["BE2"].startswith("FALSIFIER")

    # BE3: an order row that is not the card's
    assert _judge(rows={**ROWS, "the arm-rolls with the first position ahead": "15"})["BE3"].startswith("FALSIFIER")
    assert _judge(rows={**ROWS, "the reversal's largest cost": "0.0200"})["BE3"].startswith("FALSIFIER")

    # BE4: a controls row that is not the card's
    assert _judge(rows={**ROWS, "the frozen-body cells": "4"})["BE4"].startswith("FALSIFIER")
    assert _judge(rows={**ROWS, "the frozen bias's share of the buffer's gain": "0.50"})["BE4"].startswith("FALSIFIER")

    # BE5: a terms row that is not the card's, and too few findings named
    assert _judge(rows={**ROWS, "the oldest task's learning term": "0.01"})["BE5"].startswith("FALSIFIER")
    assert _judge(findings=1)["BE5"].startswith("FALSIFIER")

    #: the README or the card absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e429.judge(_doc(ok=False)))


def test_the_region_and_the_vocabulary_are_registered():
    #: the front page, the card artifact, the two markers, and the vocabulary's size
    assert e429.README.name == "README.md"
    assert e429.CARD.name == "e428_the_game_card_revision_six.json"
    assert e429.START.startswith("<!-- e429") and e429.END == "<!-- end e429 -->"
    assert len(e429.VOCABULARY) == 21 and len(ROWS) == 21
    assert sorted(e429.GROUPS) == ["BE2", "BE3", "BE4", "BE5"], sorted(e429.GROUPS)
    assert sum(len(labels) for _, labels in e429.GROUPS.values()) == len(e429.VOCABULARY)
    assert (e429.TOL, e429.RATIO_TOL, e429.MIN_FINDINGS) == (1e-3, 0.01, 3)


def test_the_live_region_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e429_the_front_page_gets_the_benchmark.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e429.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e429.judge(d)}
    #: the region being carried and its rows being the card's are structural facts
    assert verdicts["BE1"].startswith("MET") and verdicts["BE2"].startswith("MET"), verdicts
    assert d["region"] and d["artifact_named"] and d["revision_named"], d["spans"]
    assert len(d["rows"]) == len(e429.VOCABULARY), len(d["rows"])
    #: every row's label is one the vocabulary holds, and every one of them was checked against the card
    assert not d["unknown"], d["unknown"]
    assert all(label in d["checked"] for label in d["rows"]), sorted(set(d["rows"]) - set(d["checked"]))
    assert d["spans"]["missing"] == 0, d["missing_findings"]
    #: the README on disk is the one the unit read, and it still carries the front page's own scope blockquote
    text = Path("README.md").read_text(encoding="utf-8")
    assert e429.START in text and e429.END in text, "the markers are on disk"
    assert "Scoped 2026-09-29, re-read 2026-10-01" in text, "the front page's scope blockquote is untouched"
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
