"""E435 -- the front page's second region: the parameters clause, checked against the card.

`e429` put the closed-loop benchmark on the front page as a marked region of the card's numbers and made every row a
checked claim. `e431` to `e434` then measured where each arm spends its movement and wrote it into the card as the
**parameters** clause at revision 7, which the region did not carry.

**This unit adds a second region and reads it back.** The front page now carries the parameters clause's numbers between
their own markers, and this module parses that region and compares each row with the card's artifact, the way `e429`
does for the first -- and re-runs `e429`'s own check on the first region, so a revision that moved a number cannot leave
either behind. The section is written once, by hand, with the rest of this unit; the module reads it rather than
rewriting it, so the gate never touches a source file. Five claims, registered before this unit's pass over the README
and the card.

- **BK1 -- and the region is carried and names its source.** One marked region, every row's label from the unit's own
  vocabulary, and the section carrying it naming the card's artifact and its revision, both read from that artifact.
  **Falsifier**: no region, an unmarked boundary, a row whose label the vocabulary does not hold, or the wrong artifact
  or revision.
- **BK2 -- and its bias and drift rows are the card's.** The cells row and the four bias and drift ratios equal the
  values the card's parameters clause carries. **Falsifier**: any row disagreeing by more than a thousandth of a point.
- **BK3 -- and its joint rows are the card's.** The two rows for the share of cells with the weights held and the bias
  pushed equal the card's. **Falsifier**: any row disagreeing.
- **BK4 -- and its channel rows are the card's.** The two bias shares of the interference account and the frozen
  side's half equal the card's, the account's shares addressing the first task of their roll. **Falsifier**: any row
  disagreeing.
- **BK5 -- and the first region is still the card's.** `e429`'s markers are still on the page and its own five claims
  still hold when its reader is re-run. **Falsifier**: a missing marker, or any of its claims turning red.

**What it can do beyond that.** It puts the parameter ledger on the front page beside the benchmark's numbers, and it
makes the page's two regions a pair: the first says what the benchmark is worth on both axes, the second says where each
arm's movement goes, and both are checked against the card that carries them.

**What it cannot do.** *A front page is not a result*: the region summarises the clause and the clause summarises its
artifacts. *And the region is one table*: it carries the numbers this unit's vocabulary holds, not every number of the
clause, so a new number arrives on the page only when the vocabulary grows with it. *And the check is the unit's own*:
the vocabulary, the tolerances and the marker syntax are this unit's choices. *And BK5 re-runs a sibling's check*: it
shows `e429`'s reader still passes, not that its reading was ever the right one.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

README = Path("README.md")
CARD = Path("runs/e434_the_game_card_revision_seven.json")
START = "<!-- e435: the parameters clause's numbers, checked against the card -->"
END = "<!-- end e435 -->"
#: each row's label, the path into the card's parameters clause, and how closely the row must agree
VOCABULARY = {
    "the cells the parameters are pooled over": (("cells",), "int"),
    "the buffer's bias ratio": (("bias_ratio", "replay"), "tol"),
    "the diagonal penalty's bias ratio": (("bias_ratio", "ewc"), "tol"),
    "the buffer's drift ratio": (("drift_ratio", "replay"), "tol"),
    "the diagonal penalty's drift ratio": (("drift_ratio", "ewc"), "tol"),
    "the buffer's cells with the weights held and the bias pushed": (("joint_share", "replay"), "tol"),
    "the diagonal penalty's cells with the weights held and the bias pushed": (("joint_share", "ewc"), "tol"),
    "the diagonal penalty's bias share of the interference account":
        (("channel_bias_share", "pair/plastic", "ewc", 0), "tol"),
    "the unpenalised arm's bias share of the interference account":
        (("channel_bias_share", "pair/plastic", "naive", 0), "tol"),
    "the frozen side's bias half": (("frozen_bias_max",), "zero"),
}
GROUPS = {
    "BK2": ("bias and drift", ["the cells the parameters are pooled over", "the buffer's bias ratio",
                               "the diagonal penalty's bias ratio", "the buffer's drift ratio",
                               "the diagonal penalty's drift ratio"]),
    "BK3": ("joint", ["the buffer's cells with the weights held and the bias pushed",
                      "the diagonal penalty's cells with the weights held and the bias pushed"]),
    "BK4": ("channel", ["the diagonal penalty's bias share of the interference account",
                        "the unpenalised arm's bias share of the interference account",
                        "the frozen side's bias half"]),
}
TOL = 1e-3
CLAIMS = (
    ("BK1", "and the region is carried and names its source",
     "One marked region, every row's label from the unit's own vocabulary, and the section carrying it naming the "
     "card's artifact and its revision, both read from that artifact",
     "falsifier: no region, an unmarked boundary, a row whose label the vocabulary does not hold, or the wrong "
     "artifact or revision"),
    ("BK2", "and its bias and drift rows are the card's",
     "The cells row and the four bias and drift ratios equal the values the card's parameters clause carries",
     "falsifier: any row disagreeing by more than a thousandth of a point"),
    ("BK3", "and its joint rows are the card's",
     "The two rows for the share of cells with the weights held and the bias pushed equal the card's",
     "falsifier: any row disagreeing"),
    ("BK4", "and its channel rows are the card's",
     "The two bias shares of the interference account and the frozen side's half equal the card's",
     "falsifier: any row disagreeing"),
    ("BK5", "and the first region is still the card's",
     "`e429`'s markers are still on the page and its own five claims still hold when its reader is re-run",
     "falsifier: a missing marker, or any of its claims turning red"),
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
    before, after = text.split(START, 1)[0], text.split(END, 1)[1]
    heading = before.rfind("\n## ")
    section = before[(heading + 1) if heading >= 0 else 0:] + body + after.split("\n## ", 1)[0]
    return {"body": body, "rows": rows, "section": section}


def _value(parameters: dict, path):
    node = parameters
    for key in path:
        try:
            node = node[key]
        except (KeyError, IndexError, TypeError):
            return None
    return node


def _agrees(row: str, value, mode: str) -> bool:
    try:
        got = float(row)
    except ValueError:
        return False
    if value is None:
        return False
    if mode == "int":
        return abs(got - float(value)) < 0.5
    if mode == "zero":
        return abs(got) < TOL
    return abs(got - float(value)) < TOL


def reading(readme: Path = README, card_path: Path = CARD) -> dict:
    out = {"ok": True, "reason": None, "rows": {}, "unknown": [], "region": False, "artifact_named": False,
           "revision_named": False, "checked": {}, "first_region": False, "first": {}}
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
    parameters = doc.get("parameters") or {}
    out["parameters"] = parameters
    out["unknown"] = sorted(l for l in region["rows"] if l not in VOCABULARY)
    out["rows"] = region["rows"]
    names = region["section"]
    out["artifact_named"] = card_path.as_posix() in names
    out["revision_named"] = bool(re.search(rf"revision\s+\*{{0,2}}{doc.get('revision')}\b", names))
    out["checked"] = {label: _agrees(region["rows"][label], _value(parameters, path), mode)
                      for label, (path, mode) in VOCABULARY.items() if label in region["rows"]}
    #: the sibling unit's region and its own verdicts, re-run here rather than quoted
    try:
        from experiments import e429_the_front_page_gets_the_benchmark as e429
        sib = e429.reading(Path(readme), e429.CARD)
        out["first"] = {"markers": e429.START in text and e429.END in text,
                        "rows": len(sib.get("rows") or {}),
                        "verdicts": {row["id"]: row["verdict"] for row in e429.judge(sib)} if sib.get("ok") else {}}
    except Exception as exc:                                   # pragma: no cover - the sibling's own reading
        out["first"] = {"markers": False, "rows": 0, "verdicts": {}, "error": str(exc)}
    out["first_region"] = bool(out["first"].get("markers")) and all(
        v.startswith("MET") for v in (out["first"].get("verdicts") or {}).values()) and len(
        out["first"].get("verdicts") or {}) == 5
    out["spans"] = {"rows": len(region["rows"]), "vocabulary": len(VOCABULARY),
                    "first_rows": out["first"].get("rows", 0)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the README or the card is absent"}
                for c in CLAIMS]
    s = r["spans"]
    missing_rows = sorted(l for l in VOCABULARY if l not in r["rows"])
    j1 = {"id": "BK1",
          "measured": f"the region carries {s['rows']} rows of the vocabulary's {s['vocabulary']}, naming "
                      f"`{CARD.as_posix()}` ({r['artifact_named']}) and revision 7 ({r['revision_named']}), with "
                      f"{r['unknown']} outside it" + (f" and {missing_rows} absent" if missing_rows else ""),
          "verdict": f"MET -- the region is carried with the card's own artifact and revision named" if
                     (r["region"] and r["artifact_named"] and r["revision_named"] and not r["unknown"]
                      and not missing_rows) else
                     f"FALSIFIER FIRED -- unknown {r['unknown']}, missing {missing_rows[:4]}, artifact "
                     f"{r['artifact_named']}, revision {r['revision_named']}"}
    out = [j1]
    for cid in ("BK2", "BK3", "BK4"):
        what, labels = GROUPS[cid]
        bad = {l: r["rows"].get(l) for l in labels if not r.get("checked", {}).get(l)}
        out.append({"id": cid,
                    "measured": f"the {len(labels)} rows for the {what} are "
                                f"{ {l: r['rows'].get(l) for l in labels} }",
                    "verdict": f"MET -- the {what} rows are the card's own numbers" if not bad else
                    f"FALSIFIER FIRED -- {bad}"})
    first = r.get("first") or {}
    verdicts = first.get("verdicts") or {}
    out.append({"id": "BK5",
                "measured": f"`e429`'s region carries {first.get('rows', 0)} rows and its five claims are "
                            f"{verdicts}",
                "verdict": "MET -- the first region is still on the page and its five claims still hold" if
                           r["first_region"] else
                           f"FALSIFIER FIRED -- markers {first.get('markers')}, verdicts {verdicts}"})
    return out


def report(r: dict) -> int:
    print("== the front page's second region ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the README or the card is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"   the parameters region of `{README.as_posix()}` against `{CARD.as_posix()}`")
    print(f"\n   {'row':62} {'on the page':>12} {'in the card':>14} {'agrees':>7}")
    for label, (path, mode) in VOCABULARY.items():
        value = _value(r["parameters"], path)
        print(f"   {label[:62]:62} {r['rows'].get(label, '-'):>12} {value:>14} "
              f"{str(bool(r.get('checked', {}).get(label))):>7}")
    print(f"\n   {r['spans']['rows']} rows of {r['spans']['vocabulary']} in the vocabulary; the first region carries "
          f"{r['spans']['first_rows']} rows and its claims are {(r.get('first') or {}).get('verdicts')}")
    print("\n== the registered claims, BK1-BK5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e429` put the benchmark's numbers on the front page; `e431` to `e434` measured where each arm spends")
    print("    its movement, which is the card's parameters clause and what this reads back)")
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
