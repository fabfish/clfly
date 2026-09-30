"""E307 -- the front page's scope, in the currency the field it is measured in actually is.

`e299` scoped the README's front-page absence and named the field it is measured in, `mean_forgetting`. `e304` then
showed what that field **is**: the *lost* half of the shortfall `1 - R[T-1][j]`, exact and computable for every arm
from the retention matrix the corpus already stores, and blind to the other half -- the part of the task the arm never
learned. `e305` measured what that blindness costs at the level of one arm and `e306` at the level of the ordering.

**The clause on the front page does not say any of it.** A reader who meets *"55 of its 271 arms have a forgetting
indistinguishable from zero"* will read it as a statement about retention, and it is not: on those very arms the
unlearned share of the shortfall has a median of 0.821.

Three claims, registered before the reading below was taken:

- **N1 -- the clause names the field it is measured in.** **Falsifier**: no field.
- **N2 -- and it says what that field is.** It carries a phrase saying the field is half of the shortfall.
  **Falsifier**: no such phrase.
- **N3 -- and it cites the unit that measured that.** **Falsifier**: nothing cited.

They are stated as the **invariant the front page now satisfies**, as `e298` stated the paper's, because that is what
makes the unit useful going forward: an edit that drops the currency turns it red. The reading below prints the
as-found count first.

**What it cannot do.** *The cues are lexical*, so a clause that says the same thing in other words reads as absent
and the count is a lower bound -- `e298`'s caveat applies here unchanged. *This is a claim about text*: N2 verifies
that the clause carries a phrase and not that the phrase's numbers are right, and the numbers are `e304` to `e306`'s
business. *And as-found claims about a corrected document cannot be re-run*: the claims are the invariant, and the
as-found count (one of three) lives in the finding rather than in the artifact.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e299_the_front_page_claim as e299

README = Path("README.md")
#: The field the front page's absence is measured in, and the mark `e299`'s clause opens with.
FIELD = "mean_forgetting"
SCOPE_MARK = "> **Scoped"
#: The cue that a clause says what the field *is* -- that it is half of a larger quantity. Declared rather than
#: derived, and therefore the instrument's definition: a clause that says the same thing in other words reads absent.
DECOMPOSITION_CUES = ("lost half", "half of the shortfall", "the shortfall", "never learned", "never learned it")
#: The units that measured it, as `e304` to `e306` name them, and as a finding path names them.
UNITS = ("e304", "e305", "e306", "2026-10-01-the-decomposition-the-block-asked-for",
         "2026-10-01-the-arms-that-forget-nothing", "2026-10-01-the-ordering-in-the-other-currency")
CLAIMS = (
    ("N1", "the clause names the field it is measured in",
     f"The front page's scope clause carries `{FIELD}`", "falsifier: no field"),
    ("N2", "and it says what that field is",
     "The clause carries a phrase saying the field is half of the shortfall",
     "falsifier: no such phrase"),
    ("N3", "and it cites the unit that measured that",
     "The clause cites the unit that measured the decomposition", "falsifier: nothing cited"),
)


def clause(text: str) -> str:
    """The front page's scope blockquote, and nothing else.

    The blockquote runs from the marked line to the first line that is not a blockquote line, so the claims below
    are about the scope clause rather than about the README.
    """
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(SCOPE_MARK)), None)
    if start is None:
        return ""
    out = []
    for ln in lines[start:]:
        if not ln.startswith(">"):
            break
        out.append(ln)
    return " ".join(out)


def reading(readme: Path = README) -> dict:
    text = readme.read_text(encoding="utf-8")
    c = clause(text)
    low = c.lower()
    return {"mark": bool(c), "chars": len(c),
            "field": bool(re.search(rf"\b{FIELD}\b", c)),
            "decomposition": [cue for cue in DECOMPOSITION_CUES if cue in low],
            "units": [u for u in UNITS if u in c],
            #: `e299`'s own reader, so this unit does not invent a second count of the same sentences
            "absences": len(e299.absence_claims(text))}


def judge(r: dict) -> list[dict]:
    if not r.get("mark"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the front page carries no scope clause"}
                for c in CLAIMS]
    out = [{"id": "N1", "measured": f"the clause is {r['chars']} characters and "
                                    f"{'carries' if r['field'] else 'does not carry'} `{FIELD}`",
            "verdict": "MET -- the clause names the field" if r["field"] else
                       "FALSIFIER FIRED -- the clause does not name the field it is measured in"}]
    out.append({"id": "N2", "measured": f"the clause carries {len(r['decomposition'])} decomposition cue(s): "
                                        f"{r['decomposition'] or 'none'}",
                "verdict": "MET -- the clause says what the field is" if r["decomposition"] else
                           "FALSIFIER FIRED -- the reader is not told the field is half of a larger quantity"})
    out.append({"id": "N3", "measured": f"the clause cites {r['units'] or 'nothing'}",
                "verdict": "MET -- the clause cites the unit that measured it" if r["units"] else
                           "FALSIFIER FIRED -- nothing cited"})
    return out


def report(r: dict) -> int:
    print("== the front page's scope clause ==")
    print(f"   {r['chars']} characters; {r['absences']} absence claim(s) on the front page")
    print(f"   the field it is measured in: {'`' + FIELD + '`' if r['field'] else 'not named'}")
    print(f"   what that field is: {r['decomposition'] or 'not said'}")
    print(f"   the unit that measured it: {r['units'] or 'not cited'}")

    print("\n== the registered claims, N1-N3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the front page's absence is measured in a field that is the lost half of the shortfall, so a clause")
    print("    that names the field and not the half tells a reader the arms retained what they may never have had)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--readme", type=Path, default=README)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.readme)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
