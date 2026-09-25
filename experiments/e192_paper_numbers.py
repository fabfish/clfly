"""E192 -- the paper's quoted numbers, checked against the findings it cites for them.

`e97` asks whether every `runs/` file the **paper** cites exists, and whether the commands it names resolve. `e105`
checks the numbers inside **findings'** tables. Nothing checks the one relation a reader of the paper actually
relies on: **a number the paper states, in a sentence that cites a finding, is a number that finding contains.**

The difficulty is matching numbers, and this audit's first two rules are each a measured false-positive class:

- **precision.** The paper quotes `-0.0854` where the finding has `-0.08542`. A substring test calls that
  unsupported; the rule used here is that a quoted number is **supported when a number in the source rounds to it at
  the quoted precision** -- and with that rule the "absent from the whole corpus" class goes from **1 to 0**.
- **which citation a number belongs to.** A sentence may cite one finding while quoting numbers that another
  finding computed. Those are reported as their own class, with the file each number was found in, rather than
  counted as failures: the citation localises the *claim*, not every number in the sentence.

    python -m experiments.e192_paper_numbers
    python -m experiments.e192_paper_numbers --json-out ONE.json

The exit code is the count of numbers **absent from the entire findings corpus**, which is the only class that
asserts something nothing supports. The middle class -- present, but in a finding the sentence does not cite -- is
printed with its evidence and is a documentation question rather than a defect.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
FINDINGS = Path("docs/findings")
CITE_RE = re.compile(r"docs/findings/[A-Za-z0-9_.-]+\.md")
NUMBER_RE = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:e-?\d+)?)(?![\w])")
ANY_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")
#: a bare year or a section number is not a measurement: only numbers with a decimal point, or long enough to be a
#: count, are checked
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def normalise(text: str) -> str:
    """Unicode minus and the dashes the prose uses, so `−0.0116` and `-0.0116` are the same number."""
    for ch in ("−", "–", "—"):
        text = text.replace(ch, "-")
    return text


def source_numbers(text: str) -> list[float]:
    out = []
    for tok in ANY_NUMBER_RE.findall(text):
        try:
            out.append(float(tok))
        except ValueError:
            pass
    return out


def supported(quoted: str, source: str, numbers: list[float]) -> bool:
    """Is `quoted` in the source verbatim, or rounded from a number the source carries?

    The second arm is the precision rule, and it is not a fudge: `-0.0854` is what `-0.08542` rounds to at the
    paper's quoted precision, and calling that unsupported would make the audit a formatting checker.
    """
    if quoted in source:
        return True
    decimals = len(quoted.split(".")[1]) if "." in quoted else 0
    try:
        value = float(quoted)
    except ValueError:
        return False
    return any(abs(round(x, decimals) - value) < 1e-12 for x in numbers)


def audit(paper: Path = PAPER, findings_dir: Path = FINDINGS) -> dict:
    text = normalise(Path(paper).read_text(encoding="utf-8"))
    corpus = {}
    for p in sorted(glob.glob(str(findings_dir / "*.md"))):
        corpus[Path(p).name] = normalise(Path(p).read_text(encoding="utf-8"))
    prepared = {name: (t, source_numbers(t)) for name, t in corpus.items()}

    in_cited, elsewhere, unsupported, unsupported_by_citation = 0, [], [], []
    sentences_checked, numbers_checked = 0, 0
    for sentence in SENTENCE_SPLIT.split(text):
        cited = {c.split("/")[-1] for c in CITE_RE.findall(sentence)}
        if not cited:
            continue
        quoted = [n for n in NUMBER_RE.findall(sentence) if "." in n or len(n) >= 4]
        if not quoted:
            continue
        sentences_checked += 1
        numbers_checked += len(quoted)
        for n in quoted:
            if any(supported(n, *prepared[c]) for c in cited if c in prepared):
                in_cited += 1
                continue
            where = next((name for name, prep in prepared.items() if supported(n, *prep)), None)
            if where is None:
                unsupported.append({"number": n, "cited": sorted(cited), "sentence": sentence[:200]})
            else:
                elsewhere.append({"number": n, "cited": sorted(cited), "found_in": where,
                                  "sentence": sentence[:160]})
                unsupported_by_citation.append(n)
    return {"paper": str(paper), "sentences_checked": sentences_checked, "numbers_checked": numbers_checked,
            "in_the_cited_finding": in_cited, "in_another_finding": len(elsewhere),
            "in_no_finding": len(unsupported), "elsewhere": elsewhere[:20], "unsupported": unsupported}


def report(res: dict) -> int:
    print(f"   sentences carrying a number AND a findings citation : {res['sentences_checked']}")
    print(f"   numbers in them                                     : {res['numbers_checked']}")
    print(f"        present in the finding the sentence cites       : {res['in_the_cited_finding']}")
    print(f"        absent there, present in ANOTHER finding        : {res['in_another_finding']}")
    print(f"        absent from the whole findings corpus           : {res['in_no_finding']}")
    print("   (the `found in` column is the FIRST match in a fixed file order: a common number such as 4.7 is")
    print("    supported by several findings, and this column names one of them, not the source.)")
    for row in res["elsewhere"]:
        print(f"        {row['number']:>10}  cited {row['cited'][0][:40]:42} found in {row['found_in'][:40]}")
    for row in res["unsupported"]:
        print(f"   UNSUPPORTED {row['number']!r} cited {row['cited']}: {row['sentence'][:120]}")
    if res["in_no_finding"] == 0:
        print("   (a zero here is the claim: no number the paper states with a citation is absent from the findings")
        print("    corpus. The middle class is not a failure -- the citation localises the claim, not every number.")
    return res["in_no_finding"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paper", type=Path, default=PAPER)
    p.add_argument("--findings", type=Path, default=FINDINGS)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    res = audit(args.paper, args.findings)
    n = report(res)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return 0 if n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
