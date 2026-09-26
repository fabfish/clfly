"""What the three pooled readers say about the declared domain once they apply it themselves.

`e252` declared a domain and re-read every pooled claim inside it, but the rule lived in that one module while the
three readers it applies to knew nothing about it -- and this line has already paid for that shape once: `e230` folded
away a second column because **a verdict could leave the table when the instrument's subject stopped applying to it**,
and the spread line's version of the same hole is that a reader's claims are pooled over the whole corpus, so a cell
that scatters can silently demote a verdict at the reader while the domain-restored reading stays in a module the
reader's report never mentions. `domain_rule` now holds the rule and `e244`, `e246` and `e247` each take a `--domain`
flag that prints their claims twice, so the two readings travel together.

    a cell is IN the domain when every family measured there scatters by at most `T` across its own drawings

Four things are registered about that fold, all **confirmatory**, computed in the exploration that wrote the module --
the value being that the instrument computes them rather than the narrative:

**F1** no reader's claim leaves the table when the domain is applied; **F2** the domain is not decorative for any of
the three; **F3** the readers move the claims `e252` named, and only toward MET; **F4** the flag is additive, so the
unflagged reading a reader's exit code stands on is untouched.

**What it cannot do**: `e246`'s CLI takes no `--runs`, so that reader's half of F4 is always read off `runs/` and the
additivity is only checked on the corpus the gate runs from; F1 to F3 are statements about THIS corpus, whose moved
list `e252` has already watched change twice as cells were drawn, so they are re-read on every run rather than pinned
by the module's tests; the fold makes no claim stronger than `e252`'s -- it moves the same three verdicts to the same
words; and nothing here is a new measurement of the substrate.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import domain_rule
from experiments import e244_drawing_spread_by_kind as e244
from experiments import e246_spread_volatility_by_family as e246
from experiments import e247_count_matched_spread as e247
from experiments import e252_spread_domain as e252

RUNS = Path("runs")

CLAIMS = (
    ("F1", "no reader's claim leaves the table when the domain is applied",
     "Each reader returns the same claim ids inside the domain as outside it, so the filter costs the reader cells "
     "and not claims",
     "falsifier: an id a reader returns on the whole corpus and not inside the domain"),
    ("F2", "the domain is not decorative for any of the three readers",
     "Each of `e244`, `e246` and `e247` has at least one claim whose verdict the domain changes",
     "falsifier: a reader whose two readings agree on every claim"),
    ("F3", "the readers move what `e252` named, and only toward MET",
     "The union of the readers' moved ids equals the moved list `e252` computes on the same corpus, and every moved "
     "claim reads MET inside the domain",
     "falsifier: a difference between the two lists either way, or a moved claim whose in-domain reading is not MET"),
    ("F4", "the flag is additive",
     "With and without `--domain` each reader writes the same `claims` and returns the same exit code, and the flagged "
     "run adds a domain reading",
     "falsifier: a difference in the claims or the codes, or a flagged artifact with no `claims_domain`"),
)


def moved(before: list[dict], after: list[dict]) -> list[str]:
    """The ids whose verdict differs once the domain is applied -- a claim missing from `after` counts as moved."""
    a = {r["id"]: r["verdict"] for r in after}
    return [r["id"] for r in before if a.get(r["id"]) != r["verdict"]]


def reading(root: Path = RUNS) -> dict:
    """Every reader's two readings, the domain they were taken on, and `e252`'s moved list on the same corpus."""
    inside, outside = domain_rule.corpus(root)
    gs, _control = e244.groups(root)
    fam = e247.per_cell(root)
    pairs = {"e244": (e244.judge(gs), e244.judge(domain_rule.filter_gs(gs, inside))),
             "e246": (e246.judge(gs), e246.judge(domain_rule.filter_gs(gs, inside))),
             "e247": (e247.judge(fam), e247.judge(domain_rule.filter_fam(fam, inside)))}
    before, after = e252.verdicts(set(e252.cell_scatters(fam)), gs, fam), e252.verdicts(inside, gs, fam)
    return {"inside": inside, "outside": outside, "pairs": pairs,
            "moved": {name: moved(*p) for name, p in pairs.items()},
            "e252_moved": sorted(cid for cid in before if before[cid] != after.get(cid))}


def additive(root: Path = RUNS) -> list[dict]:
    """Run each reader's CLI twice, with and without `--domain`, and keep what the two runs wrote and returned."""
    out = []
    with tempfile.TemporaryDirectory() as td:
        for name, mod, argv in (("e244", e244, ["--runs", str(root)]),
                                ("e246", e246, []),
                                ("e247", e247, ["--runs", str(root)])):
            runs = []
            for flag in (False, True):
                p = Path(td) / f"{name}_{flag}.json"
                args = argv + ["--json-out", str(p)] + (["--domain"] if flag else [])
                with contextlib.redirect_stdout(io.StringIO()):
                    code = mod.main(args)
                d = json.loads(p.read_text(encoding="utf-8"))
                runs.append({"flag": flag, "code": code, "claims": d["claims"],
                             "has_domain": "claims_domain" in d})
            out.append({"reader": name, "runs": runs})
    return out


def judge(r: dict, add: list[dict]) -> list[dict]:
    out: list[dict] = []
    pairs = r["pairs"]

    lost = {name: sorted({x["id"] for x in p[0]} - {x["id"] for x in p[1]}) for name, p in pairs.items()}
    gained = {name: sorted({x["id"] for x in p[1]} - {x["id"] for x in p[0]}) for name, p in pairs.items()}
    counts = "; ".join(f"{name} {len(p[0])} to {len(p[1])}" for name, p in pairs.items())
    if any(lost.values()) or any(gained.values()):
        out.append({"id": "F1", "measured": f"{counts}; lost {lost}, gained {gained}",
                    "verdict": "FALSIFIER FIRED -- the filter takes a claim out of a reader's table"})
    else:
        out.append({"id": "F1", "measured": f"{counts}; no id appears or disappears",
                    "verdict": "MET -- the domain costs the readers cells and not claims"})

    blind = sorted(name for name, m in r["moved"].items() if not m)
    out.append({"id": "F2", "measured": "; ".join(f"{name} {r['moved'][name] or 'nothing'}"
                                                  for name in sorted(pairs)),
                "verdict": "MET -- every reader has a claim the domain moves" if not blind else
                           f"FALSIFIER FIRED -- {blind} read the same inside and outside"})

    union = sorted({cid for m in r["moved"].values() for cid in m})
    where: dict = {}
    for name, p in pairs.items():
        for x in p[1]:
            if x["id"] in union:
                where[x["id"]] = x["verdict"]
    away = sorted(cid for cid in union if not where.get(cid, "").startswith("MET"))
    n_claims = sum(len(p[0]) for p in pairs.values())
    seen = {cid: where.get(cid, "(the claim left the table)") for cid in union}
    measured = (f"the readers move {union} and e252 moves {r['e252_moved']}; "
                + "; ".join(f"{cid} reads {seen[cid].split(' -- ')[0]}" for cid in union))
    if union != r["e252_moved"]:
        out.append({"id": "F3", "measured": measured,
                    "verdict": "FALSIFIER FIRED -- the readers' moved list is not e252's"})
    elif away:
        out.append({"id": "F3", "measured": measured,
                    "verdict": f"FALSIFIER FIRED -- {away} did not move toward MET"})
    else:
        out.append({"id": "F3", "measured": measured,
                    "verdict": f"MET -- {len(union)} of {n_claims} claims move, and every one of them to MET"})

    if any("error" in d for d in add):
        out.append({"id": "F4", "measured": "; ".join(d.get("error", "") for d in add),
                    "verdict": "REFUSED -- a reader could not be run twice"})
        return out
    drifted = sorted(d["reader"] for d in add if d["runs"][0]["code"] != d["runs"][1]["code"])
    changed = sorted(d["reader"] for d in add if d["runs"][0]["claims"] != d["runs"][1]["claims"])
    missing = sorted(d["reader"] for d in add if not d["runs"][1]["has_domain"])
    measured = "; ".join(f"{d['reader']} exit {d['runs'][0]['code']} to {d['runs'][1]['code']}"
                         for d in add)
    if drifted or changed or missing:
        out.append({"id": "F4", "measured": measured + f"; codes moved {drifted}, claims moved {changed}, "
                                                      f"no domain reading {missing}",
                    "verdict": "FALSIFIER FIRED -- the flag changes what a reader returns"})
    else:
        out.append({"id": "F4", "measured": measured + "; the unflagged claims are identical in every reader",
                    "verdict": "MET -- the flag adds a reading and changes nothing a reader's exit code stands on"})
    return out


def report(r: dict, add: list[dict]) -> int:
    print("== each reader's claims, over the whole corpus and inside the declared domain ==")
    print(f"   the rule is the same for all three: {len(r['inside'])} cells in and {len(r['outside'])} out of the domain")
    for name in sorted(r["pairs"]):
        before, after = r["pairs"][name]
        a = {x["id"]: x["verdict"] for x in after}
        print(f"\n   {name}: {len(before)} claims")
        for x in before:
            b, c = x["verdict"].split(" -- ")[0], a[x["id"]].split(" -- ")[0]
            print(f"      {x['id']:>4}  {b:22} {c:22}{'  <- moved' if b != c else ''}")

    print(f"\n   the moved list the readers themselves report: {sorted(c for m in r['moved'].values() for c in m)}")
    print(f"   the same list as e252 computes it:              {r['e252_moved']}")

    print("\n== F4: the flag is additive, measured by running each reader's CLI twice ==")
    for d in add:
        if "error" in d:
            print(f"   {d['reader']}: {d['error']}")
            continue
        lo, hi = d["runs"]
        print(f"   {d['reader']}: exit {lo['code']} without the flag, {hi['code']} with it; "
              f"{'identical' if lo['claims'] == hi['claims'] else 'DIFFERENT'} claims; "
              f"{'a domain reading is written' if hi['has_domain'] else 'no domain reading'}")

    print("\n== the registered claims, F1-F4 ==")
    j = judge(r, add)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the read is live: the moved list is a property of the corpus and e252 has watched it change twice as")
    print("    cells were drawn, so a green F1 to F3 is a statement about today's corpus and not a pinned result)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    r = reading(args.runs)
    try:
        add = additive(args.runs)
    except Exception as exc:  # a reader that cannot be run twice is a REFUSED and not a traceback
        add = [{"reader": "all three", "error": repr(exc)}]
    if args.json_out:
        write_json(args.json_out, {"T": domain_rule.T,
                                   "in_domain": sorted(str(c) for c in r["inside"]),
                                   "out_of_domain": sorted(str(c) for c in r["outside"]),
                                   "readings": {name: {"all": p[0], "domain": p[1]}
                                                for name, p in r["pairs"].items()},
                                   "moved": r["moved"], "e252_moved": r["e252_moved"],
                                   "additive": [{"reader": d["reader"],
                                                 "codes": [x["code"] for x in d.get("runs", [])],
                                                 "same_claims": (d["runs"][0]["claims"] == d["runs"][1]["claims"])
                                                 if "runs" in d else None} for d in add],
                                   "claims": judge(r, add)})
        print(f"wrote {args.json_out}")
    return report(r, add)


if __name__ == "__main__":
    sys.exit(main())
