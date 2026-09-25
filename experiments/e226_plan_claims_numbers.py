"""E226 -- the plan's own Claims section, with the number check the paper already has.

`e192` asks whether every number the **paper** states, in a sentence that cites a finding, is a number that finding
carries. `e105` checks the numbers inside **findings'** tables. The document in between -- `docs/research_plan.md`,
which is what the next fire reads to decide what to run -- had no such check, and its `## Claims` section is 1198
lines carrying 898 number tokens (593 of them distinct counts or measurements). A claim is only worth the
measurement under it, so the same relation is asserted here: **a number the plan states is a number the findings
corpus carries.**

Three rules differ from `e192`, and every difference is measured rather than stylistic:

- **the match is a number token, not a substring.** `e192`'s first arm is `quoted in source`, and on this document,
  as it stood before this audit's own finding was written, that arm carries **592 of 593** against the token arm's
  **591** -- and the one member it adds, `556`, is carried **vacuously**: the digit run occurs inside longer numbers
  (`0.5563`, `15564`) in 26 findings. Matching a whole token (no word character or decimal point on either side) is
  what makes the check able to see a count that nothing computed. `--substring-arm` reproduces the looser rule, and
  the run prints the members that rule adds (`loose_arm_only`) rather than only their count.
- **the integers checked start at three digits.** One- and two-digit integers in this section are section numbers,
  ladder indices and multiplicities, not measurements; three digits is where counts live (neuron counts, draw
  counts, milliseconds).
- **a scientific notation's precision counts its exponent.** `e192` reads the decimals off the string's first `.`,
  which makes `7.6e-4` (stated to the fifth decimal) unsupportable by the `0.00076` a finding carries; with the
  exponent folded in, that number joins the corpus.

**What the exit code is.** The count of number tokens in the section that the findings corpus does not carry and
that the `DECLARED` table below does not account for. `DECLARED` is where a number whose source is the **annotation**
rather than a run is recorded: each entry names the **column, rule and prefix** that produces it, so the declaration
is a measurement to be re-run rather than an exemption to be trusted. An entry is printed whether or not the corpus
carries its number -- writing the finding that measures a count is what moves it out of the unwitnessed class, and
that transition is the state the report shows --

    python -m experiments.e226_plan_claims_numbers                       # seconds
    python -m experiments.e226_plan_claims_numbers --annotation-counts   # plus re-runs each declaration
    python -m experiments.e226_plan_claims_numbers --json-out ONE.json
"""

from __future__ import annotations

import argparse
import glob
import re
from pathlib import Path

from clfly.bench.artifacts import write_json

PLAN = Path("docs/research_plan.md")
FINDINGS = Path("docs/findings")
SECTION_START = "## Claims"
SECTION_END = "## Experimental programme"
NUMBER_RE = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:e-?\d+)?)(?![\w])")
ANY_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")
#: the numbers in this section whose source is the annotation rather than a run, each with the count that produces
#: it. The `column`/`rule`/`prefix` triple is re-run by `--annotation-counts` against `clfly.connectome.annotate`,
#: with the same `startswith` semantics `e185 --populations` uses, so an entry here is checked rather than asserted.
DECLARED: dict[str, dict] = {
    "556": {
        "column": "cell_class", "rule": "startswith", "prefix": "LH",
        "why": "the lateral-horn population, whole annotated brain -- printed by e185 --populations, whose prefix "
               "rule is the one the block's `{cell_class=LH}` probe resolves through",
    },
    "6114": {
        "column": "cell_type", "rule": "contains", "prefix": "T5",
        "why": "the plan's own contrast to the prefix count: T5 as a substring also matches LPT5*, LT5* and "
               "LHCENT5, so the count is larger than 6005 -- an annotation count declared here rather than quoted "
               "as a result, and it replaced a 6183 that neither rule produced",
    },
}


def ascii_safe(text: str) -> str:
    """The console this runs on is not UTF-8; a quoted line must not be able to raise mid-report."""
    return str(text).encode("ascii", "replace").decode("ascii")


def normalise(text: str) -> str:
    """Unicode minus and the dashes the prose uses, so `−0.0116` and `-0.0116` are the same number."""
    for ch in ("−", "–", "—"):
        text = text.replace(ch, "-")
    return text


def section(text: str, start: str = SECTION_START, end: str = SECTION_END) -> str:
    """The Claims section and the benchmark block that follows it, up to the programme's first table.

    Both are read as one region: the benchmark block is in the middle of the same claim -- what the suite is -- and
    it is where the two annotation counts live. The end marker is the first LINE that starts with it, so a mention
    of the heading inside prose does not close the region early.
    """
    lines = text.splitlines()
    first = next((i for i, ln in enumerate(lines) if ln.startswith(start)), None)
    if first is None:
        raise SystemExit(f"no line in the plan starts with {start!r}")
    last = next((i for i in range(first + 1, len(lines)) if lines[i].startswith(end)), None)
    if last is None:
        raise SystemExit(f"no line after {start!r} starts with {end!r}")
    return "\n".join(lines[first:last])


def source_numbers(text: str) -> list[float]:
    return [float(tok) for tok in ANY_NUMBER_RE.findall(text)]


def where_line(region: str, number: str) -> list[str]:
    """The lines of the section that state this number, as evidence for the report rather than for the count."""
    return [ascii_safe(ln.strip()[:120]) for ln in region.splitlines()
            if re.search(rf"(?<![\w.]){re.escape(number)}(?![\w])", ln)][:3]


def claims(text: str, min_integer_digits: int = 3) -> list[str]:
    """The number tokens worth checking: anything with a decimal point, or an integer with enough digits to be a count."""
    floor = 10 ** (min_integer_digits - 1)
    out = []
    for tok in NUMBER_RE.findall(text):
        if "." in tok or "e" in tok or abs(int(tok)) >= floor:
            out.append(tok)
    return out


def quoted_precision(quoted: str) -> int:
    """The decimal place the quote is stated to, counting a scientific notation's exponent.

    `7.6e-4` is stated to the fifth decimal (7.6 x 10**-4, one decimal in the mantissa), so a source carrying
    `0.00076` supports it. Reading the decimals off the string's first `.` -- which is what `e192` does -- makes
    every scientific-notation quote unsupportable, and that is the third measured difference from `e192`: on this
    section it is the difference between one unsupported number and two.
    """
    mantissa, _, exponent = quoted.partition("e")
    decimals = len(mantissa.split(".")[1]) if "." in mantissa else 0
    return decimals - (int(exponent) if exponent else 0)


def supported(quoted: str, source: str, numbers: list[float], substring_arm: bool = False) -> bool:
    """Is `quoted` a number the source carries -- as a token, or as the rounding of a number it carries?

    The rounding arm is `e192`'s precision rule: `-0.0854` is what `-0.08542` rounds to at the quoted precision, and
    calling that unsupported would make the audit a formatting checker.
    """
    if substring_arm:
        if quoted in source:
            return True
    elif re.search(rf"(?<![\w.]){re.escape(quoted)}(?![\w])", source):
        return True
    try:
        value = float(quoted)
    except ValueError:
        return False
    decimals = quoted_precision(quoted)
    return any(abs(round(x, decimals) - value) < 1e-12 for x in numbers)


def audit(plan: Path = PLAN, findings_dir: Path = FINDINGS, min_integer_digits: int = 3,
          substring_arm: bool = False) -> dict:
    text = normalise(Path(plan).read_text(encoding="utf-8"))
    region = section(text)
    corpus = {}
    for p in sorted(glob.glob(str(findings_dir / "*.md"))):
        t = normalise(Path(p).read_text(encoding="utf-8"))
        corpus[Path(p).name] = (t, source_numbers(t))

    tokens = claims(region, min_integer_digits)
    distinct = sorted(set(tokens), key=lambda t: (float(t), t))
    # the loose arm is measured on every number, because the class it adds -- a digit run inside a longer number --
    # is the reason this audit matches tokens, and a count that moved with the corpus would otherwise be invisible
    carried_token, carried_loose = set(), set()
    for n in distinct:
        for t, nums in corpus.values():
            if supported(n, t, nums, False):
                carried_token.add(n)
                carried_loose.add(n)
                break
        else:
            if any(supported(n, t, nums, True) for t, nums in corpus.values()):
                carried_loose.add(n)
    absent, declared = [], []
    for n in distinct:
        carried = n in (carried_loose if substring_arm else carried_token)
        if n not in DECLARED:
            if not carried:
                absent.append({"number": n, "where": where_line(region, n)})
            continue
        # a declared number is reported whether or not the corpus carries it: the entry's job is to keep the
        # annotation count attached to the number, and the corpus can gain a witness for it (writing this audit's
        # own finding did exactly that), so `carried` is a state to print rather than the reason to print it.
        row = {"number": n, "carried_by_the_findings_corpus": n in carried_token,
               "substring_arm_would_support": n in carried_loose,
               "where": where_line(region, n)}
        row.update(DECLARED[n])
        declared.append(row)
    return {"plan": str(plan), "section_lines": region.count("\n") + 1, "section_chars": len(region),
            "number_tokens": len(tokens), "distinct_numbers": len(distinct),
            "supported_under_the_substring_arm": len(carried_loose),
            "loose_arm_only": [{"number": n, "where": where_line(region, n)}
                               for n in distinct if n in carried_loose - carried_token],
            "unsupported": absent, "declared": declared,
            "declared_without_measurement": sorted(set(DECLARED) - {r["number"] for r in declared})}


def annotation_counts(rows: list[dict]) -> list[dict]:
    """Re-run each declaration's count on the annotation -- the same rule `e185 --populations` counts with."""
    from clfly.connectome import annotate

    ann = annotate.load_annotations()
    out = []
    for row in rows:
        column, prefix, rule = row.get("column"), row.get("prefix"), row.get("rule")
        if column is None or column not in ann.frame.columns:
            out.append({"number": row["number"], "count": None, "matches_claim": None})
            continue
        vals = ann.frame[column].astype(str)
        hits = vals.str.startswith(prefix) if rule == "startswith" else vals.str.contains(prefix, regex=False)
        count = int(hits.sum())
        out.append({"number": row["number"], "column": column, "prefix": prefix, "rule": rule,
                    "count": count, "matches_claim": count == int(float(row["number"]))})
    return out


def report(res: dict, counts: list[dict] | None = None) -> int:
    print(f"   == {res['plan']} :: {SECTION_START} -> {SECTION_END} ==")
    print(f"   lines {res['section_lines']}, chars {res['section_chars']}")
    print(f"   number tokens checked (decimal point, or an integer of three digits or more) : {res['number_tokens']}")
    print(f"        distinct                                                                : {res['distinct_numbers']}")
    print(f"        carried by the findings corpus, not an annotation count                     : "
          f"{res['distinct_numbers'] - len(res['unsupported']) - len(res['declared'])}")
    print(f"        DECLARED as an annotation count                                          : {len(res['declared'])}")
    print(f"        carried by nothing                                                      : {len(res['unsupported'])}")
    loose_note = (f", and the {len(res['loose_arm_only'])} it adds: "
                  + ", ".join(r["number"] for r in res["loose_arm_only"][:6])
                  + " -- read their lines before believing them)") if res["loose_arm_only"] else ")"
    print(f"   (the looser arm -- a digit run anywhere, not a number token -- carries "
          f"{res['supported_under_the_substring_arm']} of the {res['distinct_numbers']}{loose_note}")
    for row in res["declared"]:
        print(f"   DECLARED {row['number']:>8}  {row['column']} {row['rule']} {row['prefix']}   ["
              + ("carried by the corpus" if row["carried_by_the_findings_corpus"] else "no witness in the corpus")
              + ("; but the substring arm would carry it VACUOUSLY"
                 if row["substring_arm_would_support"] and not row["carried_by_the_findings_corpus"] else "")
              + "]")
        print(f"            {ascii_safe(row['why'])}")
    for row in res["unsupported"]:
        print(f"   UNSUPPORTED {row['number']!r}  in: {row['where'][0] if row['where'] else '?'}")
    if res["declared_without_measurement"]:
        print(f"   NOTE: declared but never reached: {res['declared_without_measurement']}")
    if counts is not None:
        print("   == the declarations, re-run on the annotation ==")
        for c in counts:
            verdict = {True: "MATCHES", False: "DOES NOT MATCH", None: "not an annotation count"}[c["matches_claim"]]
            print(f"        {c['number']:>8}  {c.get('column')} {c.get('rule')} {c.get('prefix')} -> "
                  f"{c['count']}  {verdict}")
    if not res["unsupported"]:
        print("   (a zero here is the claim: every number this section states is a number the findings carry, or a")
        print("    declared annotation count. The section's own arithmetic -- projections, agreements between two")
        print("    artifacts -- is the class to read first if this ever fires.)")
    return len(res["unsupported"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--plan", type=Path, default=PLAN)
    p.add_argument("--findings", type=Path, default=FINDINGS)
    p.add_argument("--min-integer-digits", type=int, default=3)
    p.add_argument("--substring-arm", action="store_true",
                   help="match a digit run anywhere, e192's first arm (measured to lose both members of the class)")
    p.add_argument("--annotation-counts", action="store_true",
                   help="re-run each DECLARED entry's count on the annotation (loads the connectome, ~a minute)")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.plan, args.findings, args.min_integer_digits, args.substring_arm)
    counts = annotation_counts(res["declared"]) if args.annotation_counts else None
    n = report(res, counts)
    if counts is not None:
        res["declared_reruns"] = counts
        if any(c["matches_claim"] is False for c in counts):
            print("   a declaration that does not re-run is a defect: fix the entry, not the section")
            n += 1
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
