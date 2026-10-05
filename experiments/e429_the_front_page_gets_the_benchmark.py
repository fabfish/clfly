"""E429 -- the front page gets the closed-loop benchmark: every number in it is one of the card's clauses.

The README has been the front page of the frozen-connectome programme since its first commit, and `e307` reads its
scope blockquote. The **closed-loop** benchmark the repository has grown since 2026-10-01 -- the card `e409` to `e428`
maintain by revision -- is named nowhere on it, so a reader reaching the front page learns about the anchored-Fisher
question and not about the benchmark built beside it.

**This unit adds a section to the front page and reads it back.** The README now carries a marked region listing the
card's own numbers, and this unit parses that region and checks every row against the card's artifact: a number on the
front page that the card does not carry, or that disagrees with it, turns the unit red. The section is written once, by
hand, with the rest of this unit; the module reads it rather than rewriting it, so the gate never touches a source file.
Five claims, registered before this unit's pass over the README and the card.

- **BE1 -- and the region is carried and names its source.** One marked region, every row's label from the unit's own
  vocabulary, and the region naming the card's artifact and its revision, both read from that artifact. **Falsifier**:
  no region, an unmarked boundary, a row whose label the vocabulary does not hold, or the wrong artifact or revision.
- **BE2 -- and its trade rows are the card's.** The seven rows for the trade clause equal the values the card carries.
  **Falsifier**: any row disagreeing by more than a thousandth of a point.
- **BE3 -- and its order rows are the card's.** The five rows for the order clause equal the card's. **Falsifier**: any
  row disagreeing.
- **BE4 -- and its controls rows are the card's.** The four rows for the controls clause equal the card's.
  **Falsifier**: any row disagreeing.
- **BE5 -- and its terms rows are the card's, and its findings are on disk.** The five rows for the terms and
  arm-terms clauses equal the card's, and every `docs/findings/...` path the region names exists. **Falsifier**: any
  row disagreeing, or a named finding absent from disk.

**What it can do beyond that.** It puts the second benchmark on the front page with the same discipline the first one
is held to: the section is short, every number in it is a clause of a maintained card, and a reader who follows any
number lands on the artifact that measured it. It also gives the front page a machine-readable list, so a later
revision that moves a number cannot leave the README behind.

**What it cannot do.** *A front page is not a result*: the section summarises the card and the card summarises its
artifacts. *And the region is one table*: it carries the numbers this unit's vocabulary holds, not every clause of the
card, so a new clause arrives here only when this unit's vocabulary grows with it. *And the check is the unit's own*:
the vocabulary, the tolerances and the marker syntax are this unit's choices, so a reader should take the region as a
checked summary rather than as the card. *And a summary is not a benchmark.*
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

README = Path("README.md")
CARD = Path("runs/e428_the_game_card_revision_six.json")
START = "<!-- e429: the closed-loop card's numbers, checked against its own artifact -->"
END = "<!-- end e429 -->"
FINDINGS = Path("docs/findings")
#: each row's label, the card field behind it, and how closely the row must agree
VOCABULARY = {
    "the far-point cells": (("trade", "far_cells"), "int"),
    "the far point's newest task cost": (("trade", "far_newest_cost"), "int"),
    "the oldest task's recovery at the far point": (("trade", "far_oldest_min"), "tol"),
    "the newest task's loss at the far point": (("trade", "far_loss_max"), "tol"),
    "the near-point cells": (("trade", "near_cells"), "int"),
    "the near point's newest task cost": (("trade", "near_newest_cost"), "int"),
    "the oldest task's recovery at the near point": (("trade", "near_oldest_max"), "tol"),
    "the oldest task's learning term": (("terms", "oldest_learning"), "zero"),
    "the newest task's retention term": (("terms", "newest_retention"), "zero"),
    "the middle task's retention over its learning price": (("terms", "middle_ratio_min"), "ratio"),
    "the buffer's retention over the penalty's": (("arm_terms", "retention_ratio_min"), "ratio"),
    "the two learning prices' gap": (("arm_terms", "price_gap_max"), "tol"),
    "the arm-rolls of the order axis": (("order", "rolls"), "int"),
    "the arm-rolls with the first position ahead": (("order", "first_ahead"), "int"),
    "the reversal's largest cost": (("order", "reversal_costs"), "absmin"),
    "the reversal's smallest cost": (("order", "reversal_costs"), "absmax"),
    "the penalty arm-rolls worst in the middle": (("order", "penalty_worst_middle"), "int"),
    "the frozen-body cells": (("controls", "frozen_body_cells"), "int"),
    "the largest gain on a frozen body": (("controls", "frozen_body_worst_gain"), "tol"),
    "the frozen bias's share of the buffer's gain": (("controls", "frozen_bias_gain_ratio"), "ratio"),
    "the frozen bias's share of the buffer's cut": (("controls", "frozen_bias_cut_ratio"), "ratio"),
}
GROUPS = {
    "BE2": ("trade", ["the far-point cells", "the far point's newest task cost",
                      "the oldest task's recovery at the far point", "the newest task's loss at the far point",
                      "the near-point cells", "the near point's newest task cost",
                      "the oldest task's recovery at the near point"]),
    "BE3": ("order", ["the arm-rolls of the order axis", "the arm-rolls with the first position ahead",
                      "the reversal's largest cost", "the reversal's smallest cost",
                      "the penalty arm-rolls worst in the middle"]),
    "BE4": ("controls", ["the frozen-body cells", "the largest gain on a frozen body",
                         "the frozen bias's share of the buffer's gain", "the frozen bias's share of the buffer's cut"]),
    "BE5": ("terms and arm terms", ["the oldest task's learning term", "the newest task's retention term",
                                    "the middle task's retention over its learning price",
                                    "the buffer's retention over the penalty's", "the two learning prices' gap"]),
}
TOL = 1e-3
RATIO_TOL = 0.01
MIN_FINDINGS = 3
CLAIMS = (
    ("BE1", "and the region is carried and names its source",
     "One marked region, every row's label from the unit's own vocabulary, and the section carrying it naming the "
     "card's artifact and its revision, both read from that artifact",
     "falsifier: no region, an unmarked boundary, a row whose label the vocabulary does not hold, or the wrong "
     "artifact or revision"),
    ("BE2", "and its trade rows are the card's",
     "The seven rows for the trade clause equal the values the card carries",
     "falsifier: any row disagreeing by more than a thousandth of a point"),
    ("BE3", "and its order rows are the card's",
     "The five rows for the order clause equal the card's",
     "falsifier: any row disagreeing"),
    ("BE4", "and its controls rows are the card's",
     "The four rows for the controls clause equal the card's",
     "falsifier: any row disagreeing"),
    ("BE5", "and its terms rows are the card's, and its findings are on disk",
     "The five rows for the terms and arm-terms clauses equal the card's, and every findings path the region names "
     "exists",
     "falsifier: any row disagreeing, or a named finding absent from disk"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _region(text: str):
    if START not in text or END not in text:
        return None
    body = text.split(START, 1)[1].split(END, 1)[0]
    rows = {}
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 2 or cells[0] in ("clause", "") or set(cells[0]) <= set("-: "):
            continue
        rows[cells[0]] = cells[1]
    #: the section the region sits in, from its own heading to the next one
    before, after = text.split(START, 1)[0], text.split(END, 1)[1]
    heading = before.rfind("\n## ")
    section = before[(heading + 1) if heading >= 0 else 0:] + body + after.split("\n## ", 1)[0]
    return {"body": body, "rows": rows, "section": section}


def _card_value(card: dict, field):
    clause, key = field
    return (card.get(clause) or {}).get(key)


def _agrees(row: str, value, mode: str) -> bool:
    try:
        got = float(row)
    except ValueError:
        return False
    if mode == "int":
        return abs(got - float(value)) < 0.5
    if mode == "zero":
        return abs(got) < TOL
    if mode == "ratio":
        return abs(got - float(value)) < RATIO_TOL
    if mode == "absmin":
        return abs(got - abs(min(value))) < TOL
    if mode == "absmax":
        return abs(got - abs(max(value))) < TOL
    return abs(got - float(value)) < TOL


def reading(readme: Path = README, card_path: Path = CARD) -> dict:
    out = {"ok": True, "reason": None, "rows": {}, "unknown": [], "region": False, "artifact_named": False,
           "revision_named": False, "findings": [], "missing_findings": [], "card": None}
    if not Path(readme).is_file():
        return {**out, "ok": False, "reason": f"{readme} is absent"}
    text = Path(readme).read_text(encoding="utf-8")
    region = _region(text)
    if region is None:
        return {**out, "ok": False, "reason": "the marked region is absent"}
    out["region"] = True
    card = load(card_path)
    if not card:
        return {**out, "ok": False, "reason": f"{card_path} is absent, so the region has nothing to be checked against"}
    doc = card.get("card") or {}
    out["card"] = doc
    out["unknown"] = sorted(l for l in region["rows"] if l not in VOCABULARY)
    out["rows"] = region["rows"]
    names = region["section"]
    out["artifact_named"] = card_path.as_posix() in names
    out["revision_named"] = bool(re.search(rf"revision\s+\*{{0,2}}{doc.get('revision')}\b", names))
    found = sorted({m for m in re.findall(r"`?(docs/findings/[A-Za-z0-9_.\-]+\.md)`?", names)})
    out["findings"] = sorted(found)
    out["missing_findings"] = [f for f in out["findings"] if not Path(f).is_file()]
    out["checked"] = {label: _agrees(region["rows"][label], _card_value(doc, field), mode)
                      for label, (field, mode) in VOCABULARY.items() if label in region["rows"]}
    out["spans"] = {"rows": len(region["rows"]), "vocabulary": len(VOCABULARY),
                    "findings_named": len(out["findings"]), "missing": len(out["missing_findings"])}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the README or the card is absent"}
                for c in CLAIMS]
    card, s = r["card"], r["spans"]
    missing_rows = sorted(l for l in VOCABULARY if l not in r["rows"])
    j1 = {"id": "BE1",
          "measured": f"the region carries {s['rows']} rows of the vocabulary's {s['vocabulary']} and its section names "
                      f"`{CARD.as_posix()}` ({r['artifact_named']}) and revision {card.get('revision')} "
                      f"({r['revision_named']}), with {r['unknown']} outside it"
                      + (f" and {missing_rows} absent" if missing_rows else ""),
          "verdict": f"MET -- the region is carried with the card's own artifact and revision named" if
                     (r["region"] and r["artifact_named"] and r["revision_named"] and not r["unknown"]
                      and not missing_rows) else
                     f"FALSIFIER FIRED -- unknown {r['unknown']}, missing {missing_rows[:4]}, artifact "
                     f"{r['artifact_named']}, revision {r['revision_named']}"}
    order = ["BE2", "BE3", "BE4", "BE5"]
    verdicts = []
    for cid in order:
        what, labels = GROUPS[cid]
        bad = {l: r["rows"].get(l) for l in labels if not r.get("checked", {}).get(l)}
        extra = {}
        if cid == "BE5" and r["missing_findings"]:
            extra = {"missing findings": r["missing_findings"]}
        if cid == "BE5" and s["findings_named"] < MIN_FINDINGS:
            extra = {**extra, "findings named": s["findings_named"]}
        verdicts.append((cid, what, labels, bad, extra))
    out = [j1]
    for cid, what, labels, bad, extra in verdicts:
        good = not bad and not extra
        out.append({"id": cid,
                    "measured": f"the {len(labels)} rows for the {what} are "
                                f"{ {l: r['rows'].get(l) for l in labels} }"
                                + (f", with {extra}" if extra else
                                   f", and the region names {s['findings_named']} findings, all on disk"),
                    "verdict": f"MET -- the {what} rows are the card's own numbers" + (
                        f", and all {s['findings_named']} named findings are on disk" if cid == "BE5" else "") if good
                    else f"FALSIFIER FIRED -- {bad or extra}"})
    return out


def report(r: dict) -> int:
    print("== the front page gets the closed-loop benchmark ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the README or the card is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"   the marked region of `{README.as_posix()}` against `{CARD.as_posix()}`")
    print(f"\n   {'row':52} {'on the page':>12} {'in the card':>14} {'agrees':>7}")
    for label, (field, mode) in VOCABULARY.items():
        value = _card_value(r["card"], field)
        print(f"   {label[:52]:52} {r['rows'].get(label, '-'):>12} "
              f"{value if not isinstance(value, list) else abs(min(value)):>14} "
              f"{str(bool(r.get('checked', {}).get(label))):>7}")
    print(f"\n   {r['spans']['rows']} rows of {r['spans']['vocabulary']} in the vocabulary, "
          f"{r['spans']['findings_named']} findings named, {r['spans']['missing']} of them absent")
    print("\n== the registered claims, BE1-BE5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e307` reads the front page's scope blockquote; this puts the second benchmark on the same page and")
    print("    reads the numbers back against the card that carries them)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
